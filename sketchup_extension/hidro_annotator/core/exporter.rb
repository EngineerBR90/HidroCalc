# encoding: utf-8
# Exportador: coleta entidades anotadas, calcula derivados e serializa JSON.
# Inclui logging e tratamento de erros.

require 'json'

module HidroAnnotator
  module Exporter
    DICT_NAME = Annotator::DICT_NAME

    # ─── Coleta de entidades anotadas ───────────────────────────────────────

    def self.collect_annotated_entities(model)
      tanks = Hash.new { |h, k| h[k] = { faces: [], edges: [] } }

      model.active_entities.each do |entity|
        begin
          annotation = Annotator.get_annotation(entity)
          next unless annotation

          tank_id = annotation['tank']
          next unless tank_id

          case annotation['type']
          when 'face'
            tanks[tank_id][:faces] << {
              entity:  entity,
              region:  annotation['region'],
              pid:     annotation['pid'],
              area_m2:       annotation['area_m2'],
              area_sources:  annotation['area_source_faces'],
              stair_masonry: annotation['stair_masonry']
            }
          when 'edge'
            tanks[tank_id][:edges] << {
              entity:        entity,
              label:         annotation['label'],
              linked_region: annotation['linked_region'],
              pid:           annotation['pid'],
              depth_m:       annotation['depth_m'],
              depth_sources: annotation['depth_source_edges']
            }
          end
        rescue => e
          HidroAnnotator.log("AVISO: erro ao coletar entidade: #{e.message}")
        end
      end

      tanks
    end

    # ─── Cálculo de derivados ───────────────────────────────────────────────

    def self.build_tanks(tanks_raw)
      tanks_raw.map do |tank_id, data|
        begin
          regions = build_regions(data[:faces], data[:edges])
          edges   = build_edges(data[:edges])

          total_area   = regions.inject(0.0) { |sum, r| sum + r[:area_m2] }
          total_volume = regions.inject(0.0) { |sum, r| sum + r[:volume_m3] }

          {
            id:              tank_id,
            regions:         regions,
            total_area_m2:   total_area.round(2),
            total_volume_m3: total_volume.round(2),
            edges:           edges
          }
        rescue => e
          HidroAnnotator.log("ERRO em build_tanks para '#{tank_id}': #{e.message}")
          { id: tank_id, regions: [], total_area_m2: 0.0, total_volume_m3: 0.0, edges: [] }
        end
      end
    end

    # ─── Serialização JSON ──────────────────────────────────────────────────

    def self.export_json(model, filepath)
      begin
        HidroAnnotator.log("Exportando JSON para: #{filepath}")

        tanks_raw = collect_annotated_entities(model)

        if tanks_raw.empty?
          HidroAnnotator.log("Nenhuma entidade anotada encontrada")
          UI.messagebox("Nenhuma entidade anotada encontrada no modelo.\n" \
                        "Ative o Annotation Mode e use o menu de contexto para anotar faces e arestas.")
          return false
        end

        tanks     = build_tanks(tanks_raw)
        walllines = collect_walllines(tanks_raw)

        # Resumo para logging
        total_faces = tanks_raw.values.sum { |d| d[:faces].length }
        total_edges = tanks_raw.values.sum { |d| d[:edges].length }
        HidroAnnotator.log("  Tanques: #{tanks_raw.keys.length}, " \
                           "Faces: #{total_faces}, Arestas: #{total_edges}")

        model_name = if model.path && !model.path.empty?
                       File.basename(model.path, '.*')
                     else
                       'modelo_sem_nome'
                     end

        data = {
          meta: {
            model_name:  model_name,
            export_date: Time.now.strftime('%Y-%m-%d'),
            units:       'meters'
          },
          tanks:             tanks,
          walllines:         walllines,
          device_placements: []
        }

        json_str = JSON.pretty_generate(data)

        File.open(filepath, 'w:UTF-8') do |f|
          f.write(json_str)
        end

        HidroAnnotator.log("JSON exportado com sucesso: #{File.size(filepath)} bytes")
        UI.messagebox("✅ JSON exportado com sucesso!\n\n#{filepath}\n\n" \
                      "#{tanks_raw.keys.length} tanque(s), " \
                      "#{total_faces} face(s), #{total_edges} aresta(s)")
        true

      rescue => e
        HidroAnnotator.log("ERRO ao exportar JSON: #{e.message}")
        HidroAnnotator.log(e.backtrace.first(3).join("\n"))
        UI.messagebox("Erro ao exportar JSON:\n#{e.message}")
        false
      end
    end

    # ─── Métodos de construção ────────────────────────────────────────────

    def self.build_regions(faces, edges)
      # Indexar arestas de profundidade por região vinculada
      depth_map = {}
      depth_sources_map = {}
      
      edges.each do |e|
        begin
          linked = e[:linked_region]
          next unless linked
          
          base_label = Vocabulary.label_base(linked)
          
          # Se já tiver depth_m (múltiplas edges), usa ele; senão recalcula legado
          depth = e[:depth_m] || Geometry.edge_length_m(e[:entity])
          
          depth_map[base_label] ||= 0.0
          depth_map[base_label] += depth
          
          depth_sources_map[base_label] ||= []
          if e[:depth_sources] && e[:depth_sources].is_a?(Array)
            depth_sources_map[base_label].concat(e[:depth_sources])
          elsif e[:pid]
            depth_sources_map[base_label] << e[:pid]
          end
        rescue => e_err
          HidroAnnotator.log("AVISO: erro ao processar aresta de profundidade: #{e_err.message}")
        end
      end

      faces.map do |f|
        begin
          area_m2  = f[:area_m2] || Geometry.face_area_m2(f[:entity])
          region   = f[:region]
          base     = Vocabulary.label_base(region)
          depth_m  = depth_map[base] || 0.0
          
          # Cálculo de volume com regra de alvenaria
          stair_masonry = f[:stair_masonry] == true
          if stair_masonry
            volume = area_m2 * (depth_m / 2.0)
          else
            volume = area_m2 * depth_m
          end
          
          vertices = Geometry.face_vertices_m(f[:entity])

          region_data = {
            label:              region,
            area_m2:            area_m2.round(2),
            depth_m:            depth_m.round(2),
            volume_m3:          volume.round(2),
            face_persistent_id: f[:pid],
            vertices:           vertices.map { |v| v.map { |c| c.round(4) } }
          }
          
          # Injeção de auditoria de seleções múltiplas
          region_data[:area_source_faces] = f[:area_sources] if f[:area_sources] && !f[:area_sources].empty?
          depth_sources = depth_sources_map[base]
          region_data[:depth_source_edges] = depth_sources if depth_sources && !depth_sources.empty?
          region_data[:stair_masonry] = true if stair_masonry

          region_data
        rescue => e
          HidroAnnotator.log("AVISO: erro ao construir região '#{f[:region]}': #{e.message}")
          { label: f[:region] || '?', area_m2: 0.0, depth_m: 0.0, volume_m3: 0.0,
            face_persistent_id: f[:pid], vertices: [] }
        end
      end
    end

    def self.build_edges(edges)
      edges
        .reject { |e| Vocabulary.depth_label?(e[:label]) || Vocabulary.wallline_label?(e[:label]) }
        .map do |e|
          begin
            {
              label:         e[:label],
              length_m:      Geometry.edge_length_m(e[:entity]).round(2),
              persistent_id: e[:pid]
            }
          rescue => err
            HidroAnnotator.log("AVISO: erro ao construir edge '#{e[:label]}': #{err.message}")
            { label: e[:label] || '?', length_m: 0.0, persistent_id: e[:pid] }
          end
        end
    end

    def self.collect_walllines(tanks_raw)
      walllines = []
      tanks_raw.each do |tank_id, data|
        data[:edges].each do |e|
          next unless Vocabulary.wallline_label?(e[:label])
          begin
            walllines << {
              tank_id:       tank_id,
              label:         e[:label],
              length_m:      Geometry.edge_length_m(e[:entity]).round(2),
              persistent_id: e[:pid]
            }
          rescue => err
            HidroAnnotator.log("AVISO: erro ao coletar wallline: #{err.message}")
          end
        end
      end
      walllines
    end
  end
end

# encoding: utf-8
# Lógica de anotação: leitura e escrita de atributos nas entidades do modelo.
# Usa o dicionário de atributos 'hidro_annotator' para evitar colisão com
# outras extensões. Todas as operações são envolvidas em begin/rescue.

module HidroAnnotator
  module Annotator
    DICT_NAME = 'hidro_annotator'

    # ─── Anotar faces (múltiplas) ───────────────────────────────────────────

    # Anota um conjunto de faces. O primeiro recebe os totais, os demais são 'face_part'.
    #
    # @param faces [Array<Sketchup::Face>]
    # @param tank_id [String]
    # @param region_label [String]
    # @return [Boolean]
    def self.annotate_faces(faces, tank_id, region_label)
      begin
        faces = [faces] unless faces.is_a?(Array)
        
        unless faces.all? { |f| f.is_a?(Sketchup::Face) }
          HidroAnnotator.log("ERRO: annotate_faces chamado com entidades inválidas")
          UI.messagebox('Erro: a seleção contém entidades que não são faces.')
          return false
        end

        if faces.empty?
          UI.messagebox('Nenhuma face fornecida para anotação.')
          return false
        end

        unless Vocabulary.valid_face_label?(region_label)
          HidroAnnotator.log("ERRO: label de face inválido '#{region_label}'")
          UI.messagebox("Label de face inválido: '#{region_label}'.\n" \
                        "Labels válidos: #{Vocabulary::FACE_LABELS.join(', ')}")
          return false
        end

        model = Sketchup.active_model
        model.start_operation('HidroCalc: Anotar Face(s)', true)

        # Cálculo de áreas e PIDs globais
        total_area_m2 = 0.0
        source_pids = []
        
        faces.each do |f|
          total_area_m2 += Geometry.face_area_m2(f)
          pid = Geometry.persistent_id(f)
          source_pids << pid if pid
        end
        
        # Determinar se é escada de alvenaria
        base_label = Vocabulary.label_base(region_label)
        stair_masonry = (base_label == 'escada')

        # Gravar na entidade principal (primeira face)
        main_face = faces.first
        main_face.set_attribute(DICT_NAME, 'tank', tank_id)
        main_face.set_attribute(DICT_NAME, 'region', region_label)
        main_face.set_attribute(DICT_NAME, 'type', 'face')
        main_face.set_attribute(DICT_NAME, 'area_m2', total_area_m2)
        main_face.set_attribute(DICT_NAME, 'area_source_faces', source_pids)
        main_face.set_attribute(DICT_NAME, 'stair_masonry', stair_masonry)
        main_face.set_attribute(DICT_NAME, 'pid', Geometry.persistent_id(main_face))

        # Gravar nas entidades complementares (partes) para não duplicar no json
        faces[1..-1].each do |part_face|
          part_face.set_attribute(DICT_NAME, 'tank', tank_id)
          part_face.set_attribute(DICT_NAME, 'region', region_label)
          part_face.set_attribute(DICT_NAME, 'type', 'face_part')
          part_face.set_attribute(DICT_NAME, 'parent_pid', Geometry.persistent_id(main_face))
          part_face.set_attribute(DICT_NAME, 'pid', Geometry.persistent_id(part_face))
        end

        model.commit_operation

        HidroAnnotator.log("Face(s) anotada(s): tank='#{tank_id}' region='#{region_label}' " \
                           "area=#{total_area_m2.round(2)}m² (parts: #{faces.length})")

        # Atualizar painel de revisão se estiver aberto
        refresh_review_panel

        true
      rescue => e
        HidroAnnotator.log("ERRO em annotate_faces: #{e.message}")
        UI.messagebox("Erro ao anotar face(s):\n#{e.message}")
        false
      end
    end

    def self.annotate_face(face, tank_id, region_label)
      annotate_faces([face], tank_id, region_label)
    end

    # ─── Anotar arestas (múltiplas profundidades ou única lineares) ─────────

    # Anota as arestas correspondentes a profundidade juntas.
    # Outros labels devem continuar recebendo as anotações individualmente com tipo `edge` direto.
    #
    # @param edges [Array<Sketchup::Edge>]
    # @param label [String]
    # @param tank_id [String]
    # @return [Boolean]
    def self.annotate_depth_edges(edges, label, tank_id)
      begin
        edges = [edges] unless edges.is_a?(Array)
        
        unless edges.all? { |e| e.is_a?(Sketchup::Edge) }
          HidroAnnotator.log("ERRO: annotate_depth_edges chamado com entidades inválidas")
          UI.messagebox('Erro: a seleção contém entidades que não são arestas.')
          return false
        end

        if edges.empty?
          UI.messagebox('Nenhuma aresta fornecida para profundidade.')
          return false
        end

        unless Vocabulary.valid_edge_label?(label)
          HidroAnnotator.log("ERRO: label de aresta inválido '#{label}'")
          UI.messagebox("Label de aresta inválido: '#{label}'.\n" \
                        "Labels válidos: #{Vocabulary::EDGE_LABELS.join(', ')}")
          return false
        end

        model = Sketchup.active_model
        model.start_operation('HidroCalc: Anotar Profundidade', true)

        # Cálculo de comprimento total e PIDs
        total_depth_m = 0.0
        source_pids = []
        
        edges.each do |e|
          total_depth_m += Geometry.edge_length_m(e)
          pid = Geometry.persistent_id(e)
          source_pids << pid if pid
        end

        main_edge = edges.first
        main_edge.set_attribute(DICT_NAME, 'label',  label)
        main_edge.set_attribute(DICT_NAME, 'tank',   tank_id)
        main_edge.set_attribute(DICT_NAME, 'type',   'edge')
        main_edge.set_attribute(DICT_NAME, 'depth_m', total_depth_m)
        main_edge.set_attribute(DICT_NAME, 'depth_source_edges', source_pids)
        main_edge.set_attribute(DICT_NAME, 'pid',    Geometry.persistent_id(main_edge))

        # Registrar a região vinculada se for de profundidade
        if Vocabulary.depth_label?(label)
          region = Vocabulary.region_from_depth(label)
          main_edge.set_attribute(DICT_NAME, 'linked_region', region)
          HidroAnnotator.log("  -> depth vinculado à região '#{region}'")
        end

        # Gravar nas arestas complementares
        edges[1..-1].each do |part_edge|
          part_edge.set_attribute(DICT_NAME, 'label', label)
          part_edge.set_attribute(DICT_NAME, 'tank', tank_id)
          part_edge.set_attribute(DICT_NAME, 'type', 'edge_part')
          part_edge.set_attribute(DICT_NAME, 'parent_pid', Geometry.persistent_id(main_edge))
          part_edge.set_attribute(DICT_NAME, 'pid', Geometry.persistent_id(part_edge))
        end

        model.commit_operation

        HidroAnnotator.log("Aresta(s) de profundidade anotada(s): tank='#{tank_id}' label='#{label}' " \
                           "length=#{total_depth_m.round(2)}m (parts: #{edges.length})")

        refresh_review_panel

        true
      rescue => e
        HidroAnnotator.log("ERRO em annotate_depth_edges: #{e.message}")
        UI.messagebox("Erro ao anotar profundidade:\n#{e.message}")
        false
      end
    end

    def self.annotate_edge(edges, label, tank_id)
      # Para compatibilidade do código existente das walllines/lineares, roteia conforme o label
      edges = [edges] unless edges.is_a?(Array)
      
      if Vocabulary.depth_label?(label)
        annotate_depth_edges(edges, label, tank_id)
      else
        begin
          unless edges.all? { |e| e.is_a?(Sketchup::Edge) }
            HidroAnnotator.log("ERRO: annotate_edge chamado com entidades inválidas")
            UI.messagebox('Erro: a seleção contém entidades que não são arestas.')
            return false
          end

          if edges.empty?
            UI.messagebox('Nenhuma aresta fornecida para anotação.')
            return false
          end

          unless Vocabulary.valid_edge_label?(label)
            HidroAnnotator.log("ERRO: label de aresta inválido '#{label}'")
            UI.messagebox("Label de aresta inválido: '#{label}'.\n" \
                          "Labels válidos: #{Vocabulary::EDGE_LABELS.join(', ')}")
            return false
          end

          model = Sketchup.active_model
          model.start_operation('HidroCalc: Anotar Aresta', true)
          
          total_length_m = 0.0
          source_pids = []
          
          edges.each do |e|
            total_length_m += Geometry.edge_length_m(e)
            pid = Geometry.persistent_id(e)
            source_pids << pid if pid
          end

          main_edge = edges.first
          main_edge.set_attribute(DICT_NAME, 'label',  label)
          main_edge.set_attribute(DICT_NAME, 'tank',   tank_id)
          main_edge.set_attribute(DICT_NAME, 'type',   'edge')
          main_edge.set_attribute(DICT_NAME, 'length_m', total_length_m)
          main_edge.set_attribute(DICT_NAME, 'edge_source_pids', source_pids)
          main_edge.set_attribute(DICT_NAME, 'pid',    Geometry.persistent_id(main_edge))

          if Vocabulary.depth_label?(label)
            region = Vocabulary.region_from_depth(label)
            main_edge.set_attribute(DICT_NAME, 'linked_region', region)
            HidroAnnotator.log("  -> depth vinculado à região '#{region}'")
          end
          
          edges[1..-1].each do |part_edge|
            part_edge.set_attribute(DICT_NAME, 'label', label)
            part_edge.set_attribute(DICT_NAME, 'tank', tank_id)
            part_edge.set_attribute(DICT_NAME, 'type', 'edge_part')
            part_edge.set_attribute(DICT_NAME, 'parent_pid', Geometry.persistent_id(main_edge))
            part_edge.set_attribute(DICT_NAME, 'pid', Geometry.persistent_id(part_edge))
          end

          model.commit_operation

          HidroAnnotator.log("Aresta(s) anotada(s): tank='#{tank_id}' label='#{label}' " \
                             "length=#{total_length_m.round(2)}m (parts: #{edges.length})")

          refresh_review_panel

          true
        rescue => e
          HidroAnnotator.log("ERRO em annotate_edge: #{e.message}")
          UI.messagebox("Erro ao anotar aresta:\n#{e.message}")
          false
        end
      end
    end

    # ─── Vincular profundidade ──────────────────────────────────────────────

    def self.link_depth(edges, region_label, tank_id)
      depth_label = "prof_#{Vocabulary.label_base(region_label)}"
      annotate_depth_edges(edges, depth_label, tank_id)
    end

    # ─── Remover anotação ───────────────────────────────────────────────────

    def self.remove_annotation(entity)
      begin
        ann = get_annotation(entity)
        desc = ann ? (ann['region'] || ann['label'] || '?') : '?'

        model = Sketchup.active_model
        model.start_operation('HidroCalc: Remover Anotação', true)
        
        # Se for entity master, remover também das partes associadas
        pid = Geometry.persistent_id(entity)
        if pid && ann && (ann['type'] == 'face' || ann['type'] == 'edge')
          model.active_entities.each do |e|
            next unless annotated?(e)
            ann_e = get_annotation(e)
            if ann_e['parent_pid'] == pid
              e.delete_attribute(DICT_NAME)
            end
          end
        end

        entity.delete_attribute(DICT_NAME)
        model.commit_operation

        HidroAnnotator.log("Anotação removida: '#{desc}'")

        # Atualizar painel de revisão
        refresh_review_panel
      rescue => e
        HidroAnnotator.log("ERRO em remove_annotation: #{e.message}")
        UI.messagebox("Erro ao remover anotação:\n#{e.message}")
      end
    end

    # ─── Ler anotação ──────────────────────────────────────────────────────

    def self.get_annotation(entity)
      dict = entity.attribute_dictionary(DICT_NAME)
      return nil unless dict

      result = {}
      dict.each_pair { |key, value| result[key] = value }
      result
    rescue => e
      HidroAnnotator.log("ERRO em get_annotation: #{e.message}")
      nil
    end

    # Verifica se uma entidade tem anotação HidroAnnotator.
    def self.annotated?(entity)
      !entity.attribute_dictionary(DICT_NAME).nil?
    rescue
      false
    end

    # ─── Contagem e sugestão de labels ──────────────────────────────────────

    def self.count_faces_in_tank(model, tank_id, label_base)
      count = 0
      model.active_entities.each do |entity|
        next unless entity.is_a?(Sketchup::Face)
        next unless entity.get_attribute(DICT_NAME, 'tank') == tank_id
        region = entity.get_attribute(DICT_NAME, 'region')
        next unless region
        base = Vocabulary.label_base(region)
        count += 1 if base == label_base
      end
      count
    rescue => e
      HidroAnnotator.log("ERRO em count_faces_in_tank: #{e.message}")
      0
    end

    # Sugere o próximo label numerado para uma região em um tanque.
    def self.suggest_label(model, tank_id, label)
      base = Vocabulary.label_base(label)
      return base unless Vocabulary.numeravel?(base)

      existing = count_faces_in_tank(model, tank_id, base)
      existing == 0 ? base : Vocabulary.gerar_id_numerado(base, existing + 1)
    rescue => e
      HidroAnnotator.log("ERRO em suggest_label: #{e.message}")
      label
    end

    # ─── Refresh do painel de revisão ───────────────────────────────────────

    def self.refresh_review_panel
      dialog = HidroAnnotator.review_dialog
      return unless dialog

      begin
        dialog.execute_script('refresh()')
      rescue => e
        HidroAnnotator.log("AVISO: não foi possível dar refresh no painel: #{e.message}")
      end
    end
  end
end

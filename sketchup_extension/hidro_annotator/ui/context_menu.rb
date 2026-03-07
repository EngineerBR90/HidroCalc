# encoding: utf-8
# Menu de contexto (botão direito) para anotação rápida.
# Só aparece quando Annotation Mode está ativo E a seleção é válida.
# O diálogo de tank_id é chamado DENTRO do handler do item (não no build).

module HidroAnnotator
  module ContextMenuUI

    def self.setup_context_menu
      HidroAnnotator.log("Registrando context menu handler...")

      UI.add_context_menu_handler do |menu|
        begin
          # Só mostra se Annotation Mode ativo
          next unless HidroAnnotator.annotation_mode?

          model = Sketchup.active_model
          next unless model

          selection = model.selection
          next if selection.empty?

          entities = selection.to_a
          
          # Verificar homogeneidade: todas faces ou todas arestas
          all_faces = entities.all? { |e| e.is_a?(Sketchup::Face) }
          all_edges = entities.all? { |e| e.is_a?(Sketchup::Edge) }

          next unless all_faces || all_edges

          submenu = menu.add_submenu('HidroCalc')

          if all_faces
            build_face_menu(submenu, entities, model)
          elsif all_edges
            build_edge_menu(submenu, entities, model)
          end

          # Opção para remover anotação (se existir)
          if Annotator.annotated?(entity)
            ann = Annotator.get_annotation(entity)
            label_text = ann['region'] || ann['label'] || '?'
            submenu.add_separator
            submenu.add_item("❌ Remover anotação (#{label_text})") do
              begin
                Annotator.remove_annotation(entity)
                Sketchup.active_model.active_view.invalidate
              rescue => e
                HidroAnnotator.log("ERRO ao remover via menu: #{e.message}")
                UI.messagebox("Erro ao remover anotação:\n#{e.message}")
              end
            end
          end

        rescue => e
          HidroAnnotator.log("ERRO no context menu handler: #{e.message}")
        end
      end

      HidroAnnotator.log("Context menu handler registrado.")
    end

    # ─── Menu para Faces ──────────────────────────────────────────────────

    def self.build_face_menu(submenu, faces, model)
      # faces é um Array<Sketchup::Face>
      sub_face = submenu.add_submenu('Anotar como região...')

      Vocabulary::FACE_LABELS.each do |label|
        # Exibir label base no menu — o tank_id será pedido ao clicar
        sub_face.add_item(label) do
          begin
            # 1. Obter tank_id (diálogo aqui, não no build)
            tank_id = prompt_tank_id(faces.first)
            next unless tank_id

            # 2. Sugerir label numerado
            suggested = Annotator.suggest_label(model, tank_id, label)

            # 3. Anotar
            if Annotator.annotate_faces(faces, tank_id, suggested)
              model.active_view.invalidate
            end
          rescue => e
            HidroAnnotator.log("ERRO ao anotar face '#{label}': #{e.message}")
            UI.messagebox("Erro ao anotar face:\n#{e.message}")
          end
        end
      end
    end

    # ─── Menu para Arestas (smart: detecta orientação) ────────────────────

    def self.build_edge_menu(submenu, edges, model)
      # edges é Array<Sketchup::Edge>
      # Detectar orientação da aresta (pelo menos uma vertical ou todas)
      vertical = edges.any? { |e| edge_vertical?(e) }

      if vertical
        # Aresta vertical → mostrar opções de profundidade
        sub_depth = submenu.add_submenu('Profundidade (prof_)...')
        Vocabulary::DEPTH_LABELS.each do |label|
          sub_depth.add_item(label) do
            begin
              tank_id = prompt_tank_id(edges.first)
              next unless tank_id
              if Annotator.annotate_depth_edges(edges, label, tank_id)
                model.active_view.invalidate
              end
            rescue => e
              HidroAnnotator.log("ERRO ao anotar profundidade '#{label}': #{e.message}")
              UI.messagebox("Erro ao anotar aresta:\n#{e.message}")
            end
          end
        end
      else
        # Aresta horizontal/inclinada → comprimentos lineares e walllines
        sub_linear = submenu.add_submenu('Comprimento linear...')
        Vocabulary::LINEAR_LABELS.each do |label|
          sub_linear.add_item(label) do
            begin
              # Para lineares, agrupamos as arestas selecionadas
              tank_id = prompt_tank_id(edges.first)
              next unless tank_id
              
              if Annotator.annotate_edge(edges, label, tank_id)
                model.active_view.invalidate
              end
            rescue => e
              HidroAnnotator.log("ERRO ao anotar linear '#{label}': #{e.message}")
              UI.messagebox("Erro ao anotar aresta:\n#{e.message}")
            end
          end
        end

        sub_wall = submenu.add_submenu('Wallline (Fase 2+)...')
        Vocabulary::WALLLINE_LABELS.each do |label|
          sub_wall.add_item(label) do
            begin
               # Para walllines agrupamos as arestas selecionadas
              tank_id = prompt_tank_id(edges.first)
              next unless tank_id
              
              if Annotator.annotate_edge(edges, label, tank_id)
                model.active_view.invalidate
              end
            rescue => e
              HidroAnnotator.log("ERRO ao anotar wallline '#{label}': #{e.message}")
              UI.messagebox("Erro ao anotar aresta:\n#{e.message}")
            end
          end
        end
      end

      # Sempre permitir todas as opções via submenu "Todos os labels..."
      sub_all = submenu.add_submenu('Todos os labels de aresta...')
      Vocabulary::EDGE_LABELS.each do |label|
        sub_all.add_item(label) do
          begin
            tank_id = prompt_tank_id(edges.first)
            next unless tank_id
            
            success = false
            if Vocabulary.depth_label?(label)
              success = Annotator.annotate_depth_edges(edges, label, tank_id)
            else
              success = Annotator.annotate_edge(edges, label, tank_id)
            end
            model.active_view.invalidate if success
          rescue => e
            HidroAnnotator.log("ERRO ao anotar aresta '#{label}': #{e.message}")
            UI.messagebox("Erro ao anotar aresta:\n#{e.message}")
          end
        end
      end
    end

    # ─── Helpers ──────────────────────────────────────────────────────────

    # Solicita o tank_id via UI.inputbox. Chamado no momento do clique,
    # NÃO durante a construção do menu.
    def self.prompt_tank_id(entity)
      # Se a entidade já tem tank_id, reutilizar
      existing = Annotator.get_annotation(entity)
      if existing && existing['tank']
        HidroAnnotator.log("Reutilizando tank_id existente: '#{existing['tank']}'")
        return existing['tank']
      end

      result = UI.inputbox(
        ['Tanque (id):'],
        ['piscina'],
        'HidroCalc — Identificar Tanque'
      )

      # UI.inputbox retorna false se o usuário cancelou
      unless result
        HidroAnnotator.log("Diálogo de tank_id cancelado pelo usuário")
        return nil
      end

      tank_id = result[0].to_s.strip.downcase.gsub(/\s+/, '_')
      if tank_id.empty?
        HidroAnnotator.log("Tank_id vazio, cancelando")
        UI.messagebox("O identificador do tanque não pode estar vazio.")
        return nil
      end

      HidroAnnotator.log("Tank_id informado: '#{tank_id}'")
      tank_id
    rescue => e
      HidroAnnotator.log("ERRO em prompt_tank_id: #{e.message}")
      nil
    end

    # Detecta se uma aresta é predominantemente vertical.
    # Uma aresta é considerada vertical se o componente Z do vetor
    # é maior que os componentes X e Y combinados.
    def self.edge_vertical?(edge)
      v = edge.line[1] # vetor direção [x, y, z]
      return false unless v

      z_abs = v.z.abs
      xy_abs = Math.sqrt(v.x ** 2 + v.y ** 2)

      z_abs > xy_abs
    rescue => e
      HidroAnnotator.log("AVISO: erro ao detectar orientação: #{e.message}")
      false # fallback: tratar como horizontal
    end

    # Inicializar o menu de contexto
    unless file_loaded?(File.basename(__FILE__))
      setup_context_menu
      file_loaded(File.basename(__FILE__))
    end
  end
end

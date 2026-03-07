# encoding: utf-8
# Barra de ferramentas: Annotation Mode toggle, Exportar, Painel de Revisão.

module HidroAnnotator
  module ToolbarUI
    def self.create_toolbar
      toolbar = UI::Toolbar.new('HidroCalc')

      HidroAnnotator.log("Criando toolbar...")

      # ─── Botão Annotation Mode (toggle) ─────────────────────────────────
      cmd_annotate = UI::Command.new('Annotation Mode') do
        begin
          HidroAnnotator.annotation_mode = !HidroAnnotator.annotation_mode?
          status = HidroAnnotator.annotation_mode? ? 'ATIVADO' : 'DESATIVADO'
          Sketchup.status_text = "HidroAnnotator: Annotation Mode #{status}"
        rescue => e
          HidroAnnotator.log("ERRO no toggle Annotation Mode: #{e.message}")
          UI.messagebox("Erro ao alternar Annotation Mode:\n#{e.message}")
        end
      end

      cmd_annotate.tooltip = 'Ativar/Desativar modo de anotação'
      cmd_annotate.status_bar_text = 'Quando ativo, o menu de contexto mostra opções de anotação HidroCalc'

      # Ícones do toggle — usa set_validation_proc para visual de estado
      icon_annotate_16 = File.join(ICONS_DIR, 'annotate_16.png')
      icon_annotate_24 = File.join(ICONS_DIR, 'annotate_24.png')
      cmd_annotate.small_icon = icon_annotate_16 if File.exist?(icon_annotate_16)
      cmd_annotate.large_icon = icon_annotate_24 if File.exist?(icon_annotate_24)

      cmd_annotate.set_validation_proc do
        HidroAnnotator.annotation_mode? ? MF_CHECKED : MF_UNCHECKED
      end

      toolbar.add_item(cmd_annotate)

      # ─── Botão Exportar ─────────────────────────────────────────────────
      cmd_export = UI::Command.new('Exportar HidroCalc') do
        begin
          HidroAnnotator.log("Botão Exportar clicado")
          model = Sketchup.active_model
          unless model
            UI.messagebox('Nenhum modelo aberto.')
            next
          end

          default_name = if model.path && !model.path.empty?
                           "#{File.basename(model.path, '.*')}_hidrocalc.json"
                         else
                           'modelo_hidrocalc.json'
                         end

          filepath = UI.savepanel(
            'Salvar JSON para HidroCalc',
            '',
            default_name
          )

          if filepath
            filepath += '.json' unless filepath.downcase.end_with?('.json')
            Exporter.export_json(model, filepath)
          end
        rescue => e
          HidroAnnotator.log("ERRO ao exportar: #{e.message}")
          UI.messagebox("Erro ao exportar JSON:\n#{e.message}")
        end
      end

      cmd_export.tooltip = 'Exportar anotações para JSON (HidroCalc)'
      cmd_export.status_bar_text = 'Exporta faces e arestas anotadas para arquivo JSON'
      icon_export_16 = File.join(ICONS_DIR, 'export_16.png')
      icon_export_24 = File.join(ICONS_DIR, 'export_24.png')
      cmd_export.small_icon = icon_export_16 if File.exist?(icon_export_16)
      cmd_export.large_icon = icon_export_24 if File.exist?(icon_export_24)

      toolbar.add_item(cmd_export)

      # ─── Botão Painel de Revisão ────────────────────────────────────────
      cmd_review = UI::Command.new('Painel HidroCalc') do
        begin
          HidroAnnotator.log("Botão Painel de Revisão clicado")
          DialogUI.show_review_panel
        rescue => e
          HidroAnnotator.log("ERRO ao abrir painel: #{e.message}")
          UI.messagebox("Erro ao abrir painel:\n#{e.message}")
        end
      end

      cmd_review.tooltip = 'Abrir painel de revisão de anotações'
      cmd_review.status_bar_text = 'Mostra tabela com todas as anotações do modelo'
      icon_review_16 = File.join(ICONS_DIR, 'review_16.png')
      icon_review_24 = File.join(ICONS_DIR, 'review_24.png')
      cmd_review.small_icon = icon_review_16 if File.exist?(icon_review_16)
      cmd_review.large_icon = icon_review_24 if File.exist?(icon_review_24)

      toolbar.add_item(cmd_review)

      toolbar.show
      HidroAnnotator.log("Toolbar criada com #{toolbar.count} itens")
      toolbar
    end

    # Inicializa a toolbar ao carregar o módulo
    unless file_loaded?(File.basename(__FILE__))
      @toolbar = create_toolbar
      file_loaded(File.basename(__FILE__))
    end
  end
end

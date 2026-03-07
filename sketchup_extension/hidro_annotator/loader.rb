# encoding: utf-8
# Carrega todos os módulos da extensão HidroAnnotator na ordem correta.

module HidroAnnotator
  CORE_DIR = File.join(EXTENSION_DIR, 'core')
  UI_DIR   = File.join(EXTENSION_DIR, 'ui')
  ICONS_DIR = File.join(EXTENSION_DIR, 'icons')

  # Helper de log — centralizado para toda a extensão
  def self.log(msg)
    puts "[HidroAnnotator] #{msg}"
  end

  log("Carregando extensão v1.0.0 ...")
  log("  PLUGIN_DIR:    #{PLUGIN_DIR}")
  log("  EXTENSION_DIR: #{EXTENSION_DIR}")

  # Estado global: modo de anotação (desligado por padrão)
  @annotation_mode = false

  def self.annotation_mode?
    @annotation_mode
  end

  def self.annotation_mode=(val)
    @annotation_mode = val
    log("Annotation Mode: #{val ? 'ATIVADO' : 'DESATIVADO'}")
  end

  # Referência global ao diálogo de revisão (para refresh)
  @review_dialog = nil

  def self.review_dialog
    @review_dialog
  end

  def self.review_dialog=(d)
    @review_dialog = d
  end

  begin
    # 1. Lógica pura (sem dependência de UI)
    require File.join(CORE_DIR, 'vocabulary.rb')
    require File.join(CORE_DIR, 'geometry.rb')
    require File.join(CORE_DIR, 'annotator.rb')
    require File.join(CORE_DIR, 'exporter.rb')

    # 2. Interface de usuário
    require File.join(UI_DIR, 'toolbar.rb')
    require File.join(UI_DIR, 'context_menu.rb')
    require File.join(UI_DIR, 'dialog.rb')

    log("Todos os módulos carregados com sucesso.")
  rescue => e
    log("ERRO ao carregar módulos: #{e.message}")
    log(e.backtrace.first(5).join("\n"))
    UI.messagebox("HidroAnnotator: Erro ao carregar extensão.\n#{e.message}")
  end
end

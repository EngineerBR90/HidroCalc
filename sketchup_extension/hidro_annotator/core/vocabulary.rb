# encoding: utf-8
# Vocabulário fixo de labels — fonte da verdade para toda a extensão.
# Qualquer label não listado aqui será rejeitado pela anotação.

module HidroAnnotator
  module Vocabulary
    # ─── Labels de face (região) ────────────────────────────────────────────
    FACE_LABELS = %w[
      fundo
      prainha
      escada
      banco
      piso_spa
      cocho
    ].freeze

    # Labels numeráveis: quando há mais de uma instância no mesmo tanque,
    # recebem sufixo _1, _2, etc.
    NUMERAVEIS = %w[
      fundo
      prainha
      escada
      banco
      piso_spa
    ].freeze

    # ─── Labels de aresta — profundidade ────────────────────────────────────
    # Sempre vinculada a uma região. O comprimento da aresta = valor de h[m].
    DEPTH_LABELS = FACE_LABELS.map { |l| "prof_#{l}" }.freeze

    # ─── Labels de aresta — comprimentos lineares ───────────────────────────
    LINEAR_LABELS = %w[
      borda_infinita
      borda_prainha
    ].freeze

    # ─── Labels de aresta — walllines (coletados Fase 1, usados Fase 2+) ───
    WALLLINE_LABELS = %w[
      wallline_refletores
      wallline_retorno_filtragem
      wallline_retorno_aquecimento
      wallline_retorno_transbordo
      wallline_retorno_hidromassagem
    ].freeze

    # Todos os labels de aresta válidos
    EDGE_LABELS = (DEPTH_LABELS + LINEAR_LABELS + WALLLINE_LABELS).freeze

    # ─── Métodos utilitários ────────────────────────────────────────────────

    # Verifica se um label de face é numerável (pode ter _1, _2…)
    def self.numeravel?(label)
      base = label.sub(/_\d+\z/, '')
      NUMERAVEIS.include?(base)
    end

    # Gera o label numerado: prainha → prainha_2 (n >= 2)
    def self.gerar_id_numerado(label, n)
      base = label.sub(/_\d+\z/, '')
      n <= 1 ? base : "#{base}_#{n}"
    end

    # Extrai o label base removendo sufixo numérico
    def self.label_base(label)
      label.sub(/_\d+\z/, '')
    end

    # Verifica se é um label de face válido (incluindo numerados)
    def self.valid_face_label?(label)
      base = label.sub(/_\d+\z/, '')
      FACE_LABELS.include?(base)
    end

    # Verifica se é um label de aresta válido
    def self.valid_edge_label?(label)
      EDGE_LABELS.include?(label)
    end

    # Verifica se é um label de profundidade
    def self.depth_label?(label)
      DEPTH_LABELS.include?(label)
    end

    # Extrai o nome da região a partir do label de profundidade
    # prof_fundo → fundo, prof_prainha → prainha
    def self.region_from_depth(label)
      return nil unless depth_label?(label)
      label.sub(/\Aprof_/, '')
    end

    # Verifica se é um label de wallline
    def self.wallline_label?(label)
      WALLLINE_LABELS.include?(label)
    end
  end
end

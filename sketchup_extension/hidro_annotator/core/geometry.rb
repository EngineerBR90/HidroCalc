# encoding: utf-8
# Funções de geometria: conversão de unidades e extração de dados geométricos.
# A API do SketchUp usa polegadas internamente. Todas as conversões para
# metros são feitas aqui, no momento da exportação.

module HidroAnnotator
  module Geometry
    # Fator de conversão: 1 polegada = 0.0254 metros
    INCH_TO_M  = 0.0254
    # Fator de conversão de área: 1 in² = 0.0254² m²
    INCH2_TO_M2 = INCH_TO_M ** 2

    # Calcula a área de uma face em metros quadrados.
    # A API do SketchUp retorna a área em polegadas quadradas.
    #
    # @param face [Sketchup::Face] a face do modelo
    # @return [Float] área em m²
    def self.face_area_m2(face)
      raise ArgumentError, 'Esperado Sketchup::Face' unless face.is_a?(Sketchup::Face)
      face.area * INCH2_TO_M2
    end

    # Extrai os vértices de uma face em coordenadas globais (metros).
    # Retorna array de arrays [x, y, z] em metros.
    #
    # @param face [Sketchup::Face] a face do modelo
    # @return [Array<Array<Float>>] vértices [[x,y,z], ...]
    def self.face_vertices_m(face)
      raise ArgumentError, 'Esperado Sketchup::Face' unless face.is_a?(Sketchup::Face)
      face.vertices.map do |vertex|
        pt = vertex.position
        [
          pt.x.to_f * INCH_TO_M,
          pt.y.to_f * INCH_TO_M,
          pt.z.to_f * INCH_TO_M
        ]
      end
    end

    # Calcula o comprimento de uma aresta em metros.
    #
    # @param edge [Sketchup::Edge] a aresta do modelo
    # @return [Float] comprimento em metros
    def self.edge_length_m(edge)
      raise ArgumentError, 'Esperado Sketchup::Edge' unless edge.is_a?(Sketchup::Edge)
      edge.length.to_f * INCH_TO_M
    end

    # Retorna o persistent_id da entidade (sobrevive a edições de geometria).
    # Disponível a partir do SketchUp 2017.
    #
    # @param entity [Sketchup::Entity]
    # @return [String, nil] persistent_id ou nil se não disponível
    def self.persistent_id(entity)
      entity.respond_to?(:persistent_id) ? entity.persistent_id.to_s : nil
    end
  end
end

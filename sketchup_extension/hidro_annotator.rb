# encoding: utf-8
# HidroAnnotator — Extensão SketchUp para anotação de piscinas
# Integração com HidroCalc Piscinas

require 'sketchup.rb'
require 'extensions.rb'

module HidroAnnotator
  PLUGIN_DIR = File.dirname(__FILE__)
  EXTENSION_DIR = File.join(PLUGIN_DIR, 'hidro_annotator')

  unless file_loaded?(__FILE__)
    extension = SketchupExtension.new(
      'HidroAnnotator',
      File.join(EXTENSION_DIR, 'loader.rb')
    )

    extension.description = 'Anotação de piscinas para integração com HidroCalc. ' \
                            'Classifica faces e arestas do modelo 3D e exporta JSON ' \
                            'para dimensionamento automático de equipamentos.'
    extension.version     = '1.0.0'
    extension.creator     = 'HidroCalc'
    extension.copyright   = '2026'

    Sketchup.register_extension(extension, true)
    file_loaded(__FILE__)
  end
end

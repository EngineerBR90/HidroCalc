# encoding: utf-8
# Painel de revisão: HtmlDialog com tabela de anotações e refresh em tempo real.
# O método refresh() é exposto via JavaScript para que o annotator possa
# forçar atualização após cada anotação.

module HidroAnnotator
  module DialogUI
    DIALOG_ID = 'hidro_annotator_review'

    # Abre ou foca o painel de revisão de anotações.
    def self.show_review_panel
      begin
        model = Sketchup.active_model
        unless model
          UI.messagebox('Nenhum modelo aberto.')
          return
        end

        HidroAnnotator.log("Abrindo painel de revisão...")

        # Se o diálogo já existe e está visível, apenas dar refresh
        if HidroAnnotator.review_dialog && HidroAnnotator.review_dialog.visible?
          HidroAnnotator.log("Painel já aberto, forçando refresh")
          HidroAnnotator.review_dialog.execute_script('refresh()')
          return
        end

        dialog = UI::HtmlDialog.new(
          dialog_title:    'HidroCalc — Revisão de Anotações',
          preferences_key: DIALOG_ID,
          width:           720,
          height:          520,
          resizable:       true,
          style:           UI::HtmlDialog::STYLE_DIALOG
        )

        # HTML com JavaScript refresh()
        dialog.set_html(build_html_with_refresh)

        # Callback: solicitar dados da tabela (chamado pelo JS refresh())
        dialog.add_action_callback('request_data') do |_ctx|
          begin
            json_data = build_table_json(model)
            dialog.execute_script("updateTable(#{json_data})")
          rescue => e
            HidroAnnotator.log("ERRO em request_data: #{e.message}")
          end
        end

        # Callback: remover anotação
        dialog.add_action_callback('remove') do |_ctx, entity_pid|
          begin
            HidroAnnotator.log("Painel: remover PID=#{entity_pid}")
            remove_by_pid(model, entity_pid)
            # Refresh acontece automaticamente via Annotator.remove_annotation
          rescue => e
            HidroAnnotator.log("ERRO em remove callback: #{e.message}")
          end
        end

        # Callback: selecionar entidade no modelo
        dialog.add_action_callback('select') do |_ctx, entity_pid|
          begin
            select_by_pid(model, entity_pid)
          rescue => e
            HidroAnnotator.log("ERRO em select callback: #{e.message}")
          end
        end

        # Ao fechar, limpar referência global
        dialog.set_on_closed do
          HidroAnnotator.review_dialog = nil
          HidroAnnotator.log("Painel de revisão fechado")
        end

        # Guardar referência global para refresh externo
        HidroAnnotator.review_dialog = dialog

        dialog.show

        HidroAnnotator.log("Painel de revisão aberto")

      rescue => e
        HidroAnnotator.log("ERRO ao abrir painel: #{e.message}")
        UI.messagebox("Erro ao abrir painel de revisão:\n#{e.message}")
      end
    end

    # ─── Geração de HTML ──────────────────────────────────────────────────

    def self.build_html_with_refresh
      <<~HTML
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              font-family: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
              font-size: 13px;
              color: #333;
              background: #f5f7fa;
              padding: 16px;
            }
            h2 {
              font-size: 16px;
              color: #1a4e8a;
              margin-bottom: 4px;
            }
            .summary {
              color: #666;
              margin-bottom: 12px;
              font-size: 12px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              background: #fff;
              border-radius: 6px;
              overflow: hidden;
              box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            th {
              background: #1a4e8a;
              color: #fff;
              font-weight: 600;
              text-align: left;
              padding: 8px 10px;
              font-size: 12px;
            }
            td {
              padding: 6px 10px;
              border-bottom: 1px solid #eee;
              font-size: 12px;
            }
            tr:hover td { background: #f0f4ff; }
            .actions button {
              background: none;
              border: 1px solid #ddd;
              cursor: pointer;
              font-size: 13px;
              padding: 2px 8px;
              border-radius: 4px;
              margin: 0 2px;
            }
            .actions button:hover { background: #e0e0e0; }
            .empty-msg {
              text-align: center;
              color: #888;
              padding: 24px;
              font-style: italic;
            }
            #status {
              color: #1a4e8a;
              font-size: 11px;
              margin-top: 8px;
            }
          </style>
        </head>
        <body>
          <h2>💧 HidroCalc — Anotações do Modelo</h2>
          <p class="summary" id="summary">Carregando...</p>
          <table>
            <thead>
              <tr>
                <th>Tanque</th>
                <th>Tipo</th>
                <th>Label</th>
                <th>Valor</th>
                <th>PID</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody id="tbody">
              <tr><td colspan="6" class="empty-msg">Carregando dados...</td></tr>
            </tbody>
          </table>
          <p id="status"></p>

          <script>
            // Função chamada pelo Ruby (execute_script) para atualizar a tabela
            function refresh() {
              document.getElementById('status').innerText = 'Atualizando...';
              sketchup.request_data();
            }

            // Recebe dados do Ruby e reconstrói a tabela
            function updateTable(data) {
              var tbody = document.getElementById('tbody');
              var summary = document.getElementById('summary');
              var status = document.getElementById('status');

              if (!data || !data.rows || data.rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="empty-msg">' +
                  'Nenhuma anotação encontrada no modelo.</td></tr>';
                summary.innerText = '0 tanque(s) · 0 face(s) · 0 aresta(s)';
                status.innerText = '';
                return;
              }

              var html = '';
              for (var i = 0; i < data.rows.length; i++) {
                var r = data.rows[i];
                var pidShort = r.pid ? r.pid.substring(0, 8) : '—';
                html += '<tr>' +
                  '<td>' + r.tank + '</td>' +
                  '<td>' + r.tipo + '</td>' +
                  '<td>' + r.label + '</td>' +
                  '<td>' + r.valor + '</td>' +
                  '<td>' + pidShort + '</td>' +
                  '<td class="actions">' +
                    '<button onclick="sketchup.select(\\'' + r.pid + '\\')">📍</button>' +
                    '<button onclick="sketchup.remove(\\'' + r.pid + '\\')">❌</button>' +
                  '</td>' +
                '</tr>';
              }

              tbody.innerHTML = html;
              summary.innerText = data.tanks + ' tanque(s) · ' +
                data.faces + ' face(s) · ' + data.edges + ' aresta(s)';
              status.innerText = 'Atualizado: ' + new Date().toLocaleTimeString();
            }

            // Carregar dados ao abrir
            window.onload = function() { refresh(); };
          </script>
        </body>
        </html>
      HTML
    end

    # ─── Dados em JSON para o JS ──────────────────────────────────────────

    def self.build_table_json(model)
      begin
        tanks_raw = Exporter.collect_annotated_entities(model)
        rows = []
        total_faces = 0
        total_edges = 0

        tanks_raw.each do |tank_id, data|
          data[:faces].each do |f|
            begin
              area_val = f[:area_m2] || Geometry.face_area_m2(f[:entity])
              area = area_val.round(2)
              rows << {
                tank:  tank_id,
                tipo:  'Face',
                label: f[:region],
                valor: "#{area} m²",
                pid:   f[:pid] || ''
              }
              total_faces += 1
            rescue => e
              HidroAnnotator.log("AVISO: erro ao ler face: #{e.message}")
            end
          end

          data[:edges].each do |e_data|
            begin
              length_val = e_data[:length_m] || e_data[:depth_m] || Geometry.edge_length_m(e_data[:entity])
              length = length_val.round(2)
              rows << {
                tank:  tank_id,
                tipo:  'Aresta',
                label: e_data[:label],
                valor: "#{length} m",
                pid:   e_data[:pid] || ''
              }
              total_edges += 1
            rescue => e
              HidroAnnotator.log("AVISO: erro ao ler aresta: #{e.message}")
            end
          end
        end

        result = {
          tanks: tanks_raw.keys.length,
          faces: total_faces,
          edges: total_edges,
          rows:  rows
        }

        # Serializar para JSON
        require 'json'
        JSON.generate(result)
      rescue => e
        HidroAnnotator.log("ERRO em build_table_json: #{e.message}")
        '{"tanks":0,"faces":0,"edges":0,"rows":[]}'
      end
    end

    # ─── Métodos auxiliares ────────────────────────────────────────────────

    def self.remove_by_pid(model, pid)
      model.active_entities.each do |entity|
        entity_pid = Geometry.persistent_id(entity)
        if entity_pid == pid && Annotator.annotated?(entity)
          Annotator.remove_annotation(entity)
          return
        end
      end
      HidroAnnotator.log("AVISO: PID '#{pid}' não encontrado para remoção")
    rescue => e
      HidroAnnotator.log("ERRO em remove_by_pid: #{e.message}")
    end

    def self.select_by_pid(model, pid)
      model.selection.clear
      model.active_entities.each do |entity|
        if Geometry.persistent_id(entity) == pid
          model.selection.add(entity)
          HidroAnnotator.log("Entidade selecionada: PID=#{pid}")
          return
        end
      end
      HidroAnnotator.log("AVISO: PID '#{pid}' não encontrado para seleção")
    rescue => e
      HidroAnnotator.log("ERRO em select_by_pid: #{e.message}")
    end
  end
end

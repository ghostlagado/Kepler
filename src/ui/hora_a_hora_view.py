"""Tela Hora a Hora: colar/coletar o relatório de DCOs e ver a tabela do dia.

Fluxo: texto bruto -> parsers.dco_text -> domain.hora_a_hora -> services
(snapshot/histórico) -> esta tabela. A tela não contém regra de negócio;
mantém apenas estado de apresentação (relatório exibido e ordenação).
"""

from datetime import datetime

import flet as ft

from core import config, palette
from reports import hora_a_hora_xlsx
from services import hora_a_hora
from ui.format import brl
from ui.hora_a_hora_table import build_table


def _card(title: str, value: str) -> ft.Container:
    """Cartão-resumo no topo da tela (realizado/meta e departamentos abaixo)."""
    return ft.Container(
        bgcolor=palette.SURFACE,
        border=ft.Border.all(1, palette.BORDER),
        border_radius=10,
        padding=16,
        expand=True,
        content=ft.Column(
            [
                ft.Text(title, color=palette.TEXT_SECONDARY, size=12),
                ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=6,
        ),
    )


def build(page: ft.Page) -> ft.Control:
    """Monta a tela; o snapshot salvo é reaproveitado para não começar vazia."""
    store_dropdown = ft.Dropdown(
        label="Loja",
        width=140,
        value=config.DEFAULT_STORE,
        options=[ft.dropdown.Option(store) for store in config.E_STORE_STORES],
    )
    raw_field = ft.TextField(
        label="Cole aqui o relatório de DCOs (TXT/HTML copiado do sistema)",
        multiline=True,
        min_lines=8,
        max_lines=14,
        text_size=12,
    )
    status = ft.Text("", color=palette.TEXT_SECONDARY, selectable=True)
    last_update = ft.Text("", color=palette.TEXT_SECONDARY, size=12)
    table_holder = ft.Container()

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    def set_status(text: str, error: bool = False) -> None:
        status.value = text
        status.color = palette.PRIMARY if error else palette.TEXT_SECONDARY
        page.update()

    # Estado apenas de apresentação: relatório exibido e ordenação da tabela.
    state = {"report": None, "sort_index": None, "sort_ascending": True}

    def render_report(report, reset_sort: bool = False) -> None:
        state["report"] = report
        if reset_sort:
            state["sort_index"] = None
            state["sort_ascending"] = True
        table_holder.content = build_table(
            report,
            sort_index=state["sort_index"],
            sort_ascending=state["sort_ascending"],
            on_sort=on_sort,
        )
        last_update.value = (
            f"Última atualização válida: {report.collected_at:%d/%m/%Y %H:%M} "
            f"· loja {report.store}"
        )

    def on_sort(event) -> None:
        """Clique no cabeçalho: mesma coluna inverte a direção, nova coluna recomeça crescente."""
        idx = event.column_index
        if state["sort_index"] == idx:
            state["sort_ascending"] = not state["sort_ascending"]
        else:
            state["sort_index"] = idx
            state["sort_ascending"] = True
        render_report(state["report"])
        column_names = ["Departamento", "Meta do dia", "Realizado", "Gap",
                        "% da meta"]
        if idx in range(len(column_names)):
            direction = "crescente" if state["sort_ascending"] else "decrescente"
            status.value = f"tabela ordenada por {column_names[idx]} ({direction})"
            status.color = palette.TEXT_SECONDARY
        page.update()

    def load_file(event: ft.ControlEvent) -> None:
        if not event.files:
            return
        path = event.files[0].path
        try:
            raw_field.value = _read_text(path)
        except OSError as exc:
            set_status(f"falha ao ler {path}: {exc}", error=True)
            return
        set_status(f"arquivo carregado: {path}")
        page.update()

    def process(event: ft.ControlEvent) -> None:
        outcome = hora_a_hora.run(store_dropdown.value, raw_field.value or "")
        if outcome.ok:
            render_report(outcome.report, reset_sort=True)
            set_status("coleta processada e relatório atualizado")
        else:
            set_status(" · ".join(outcome.errors) or "falha na coleta", error=True)
        page.update()

    def export_xlsx(event: ft.ControlEvent) -> None:
        report = hora_a_hora.load_snapshot()
        if report is None:
            set_status("nenhum relatório válido para exportar", error=True)
            page.update()
            return
        name = f"hora_a_hora_{report.store}_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        path = hora_a_hora_xlsx.export(report, config.EXPORTS_DIR / name)
        set_status(f"planilha exportada: {path}")
        page.update()

    file_picker.on_result = load_file

    process_btn = ft.FilledButton("Processar coleta", on_click=process)
    export_btn = ft.FilledTonalButton(
        "Exportar planilha", icon=ft.Icons.DOWNLOAD, on_click=export_xlsx
    )
    load_btn = ft.OutlinedButton(
        "Carregar arquivo TXT",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda e: file_picker.pick_files(
            dialog_title="Selecionar relatório de DCOs", allow_multiple=False
        ),
    )

    snapshot = hora_a_hora.load_snapshot()
    if snapshot is not None:
        render_report(snapshot)
        total = (
            f"{brl(snapshot.total_realizado)} de {brl(snapshot.total_meta)}"
        )
        below = (
            f"{snapshot.departments_below_meta} departamento(s) abaixo da meta"
        )
    else:
        table_holder.content = ft.Text(
            "Nenhum relatório válido ainda. Cole o relatório de DCOs ou carregue "
            "um arquivo e clique em Processar coleta.",
            color=palette.TEXT_SECONDARY,
        )
        total = "sem dados"
        below = "sem dados"

    return ft.Column(
        [
            ft.Text("Hora a Hora", size=24, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    _card("Realizado / Meta (loja)", total),
                    _card("Departamentos abaixo da meta", below),
                ],
                spacing=12,
            ),
            ft.Row([store_dropdown, load_btn, process_btn, export_btn], spacing=10),
            raw_field,
            ft.Row([last_update], ),
            status,
            ft.Container(
                bgcolor=palette.SURFACE,
                border=ft.Border.all(1, palette.BORDER),
                border_radius=10,
                padding=12,
                content=ft.Column([
                    ft.Text("Realizado por departamento × meta do dia", size=13),
                    ft.Row([table_holder], scroll=ft.ScrollMode.AUTO),
                ]),
            ),
            ft.Text(
                "Fórmulas herdadas do PDV_V2: gap = realizado − meta; metas lidas "
                "de metas/metas.xlsx por data, loja e grupo de operações.",
                size=11,
                color=palette.TEXT_SECONDARY,
            ),
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _read_text(path) -> str:
    from pathlib import Path

    p = Path(path)
    for encoding in ("utf-8", "latin-1"):
        try:
            return p.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise OSError("arquivo ilegível")

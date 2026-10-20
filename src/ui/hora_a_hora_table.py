"""Tabela do Hora a Hora: uma linha por departamento + linha TOTAL da loja.

Recebendo apenas um HourlyReport pronto, a tabela se limita a formatar
(money pt-BR, cores de status) e a ordenar localmente — sem recalculador
nada. A linha TOTAL fica sempre ao final, mesmo ordenada.
"""

import flet as ft

from core import palette
from domain.hora_a_hora import (
    HourlyReport,
    STATUS_ABOVE,
    STATUS_BELOW,
    STATUS_NEAR,
    STATUS_NO_META,
)
from ui.format import brl, percent

_STATUS_COLOR = {
    STATUS_BELOW: palette.STATUS_BELOW,
    STATUS_NEAR: palette.STATUS_NEAR,
    STATUS_ABOVE: palette.STATUS_ABOVE,
    STATUS_NO_META: palette.STATUS_NO_META,
}

# Índice da coluna -> chave de ordenação (colunas 0..4 do DataTable).
# Departamentos sem meta (% = None) vão para o fim na ordenação crescente.
_SORT_KEYS = {
    0: lambda r: r.department.label,
    1: lambda r: r.meta,
    2: lambda r: r.realizado,
    3: lambda r: r.gap,
    4: lambda r: r.percent if r.percent is not None else -1.0,
}


def _cell(text: str, bold=False, color=None) -> ft.DataCell:
    return ft.DataCell(
        ft.Text(text, weight=ft.FontWeight.BOLD if bold else None, color=color)
    )


def _total_row(report: HourlyReport) -> ft.DataRow:
    """Linha fixa de total da loja; gap negativo aparece em vermelho."""
    return ft.DataRow(cells=[
        _cell("TOTAL LOJA", bold=True),
        _cell(brl(report.total_meta), bold=True),
        _cell(brl(report.total_realizado), bold=True),
        _cell(
            brl(report.total_gap),
            bold=True,
            color=_STATUS_COLOR[
                STATUS_BELOW if report.total_gap < 0 else STATUS_ABOVE
            ],
        ),
        _cell(
            percent(
                report.total_realizado / report.total_meta
                if report.total_meta > 0 else None
            ),
            bold=True,
        ),
    ])


def build_table(
    report: HourlyReport,
    sort_index: int | None = None,
    sort_ascending: bool = True,
    on_sort=None,
) -> ft.DataTable:
    """DataTable ordenável; a ordenação é aplicada aqui (Flet só pinta o ícone)."""
    results = list(report.results)
    if sort_index in _SORT_KEYS:
        results.sort(key=_SORT_KEYS[sort_index], reverse=not sort_ascending)
    rows = [
        ft.DataRow(cells=[
            _cell(result.department.label),
            _cell(brl(result.meta)),
            _cell(brl(result.realizado)),
            _cell(
                brl(result.gap),
                bold=True,
                color=_STATUS_COLOR[result.status],
            ),
            _cell(percent(result.percent), color=_STATUS_COLOR[result.status]),
        ])
        for result in results
    ]
    rows.append(_total_row(report))
    columns = [
        ft.DataColumn(ft.Text("Departamento"), on_sort=on_sort),
        ft.DataColumn(ft.Text("Meta do dia"), numeric=True, on_sort=on_sort),
        ft.DataColumn(ft.Text("Realizado"), numeric=True, on_sort=on_sort),
        ft.DataColumn(ft.Text("Gap"), numeric=True, on_sort=on_sort),
        ft.DataColumn(ft.Text("% da meta"), numeric=True, on_sort=on_sort),
    ]
    return ft.DataTable(
        columns=columns,
        rows=rows,
        heading_row_color=palette.SURFACE,
        divider_thickness=0.5,
        column_spacing=28,
        expand=True,
        sort_column_index=sort_index,
        sort_ascending=sort_ascending,
    )

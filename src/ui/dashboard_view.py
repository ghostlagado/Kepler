"""Tela de Dashboard: visão consolidada do dia de uma loja.

Os números vêm sempre do módulo Hora a Hora (snapshot + histórico em JSONL),
reconstruídos para a loja escolhida no seletor. Nada aqui calcula regra de
negócio — apenas formata e desenha.
"""

import flet as ft
import flet_charts as ffc

from core import config, palette
from domain.hora_a_hora import (
    STATUS_ABOVE,
    STATUS_BELOW,
    STATUS_NEAR,
    STATUS_NO_META,
)
from services import hora_a_hora
from ui.format import brl, percent

# Cor da barra de "meta" no gráfico de departamentos (cinza neutro,
# para não brigar com as cores de status do realizado).
_META_ROD = "#3E444A"
_STATUS_COLOR = {
    STATUS_BELOW: palette.STATUS_BELOW,
    STATUS_NEAR: palette.STATUS_NEAR,
    STATUS_ABOVE: palette.STATUS_ABOVE,
    STATUS_NO_META: palette.STATUS_NO_META,
}


def _chart_border() -> ft.Border:
    """Borda sutil apenas nas laterais dos gráficos (estilo do tema escuro)."""
    side = ft.BorderSide(
        width=1,
        color=ft.Colors.with_opacity(0.5, palette.BORDER),
        style=ft.BorderStyle.SOLID,
    )
    return ft.Border.symmetric(vertical=side)


def _card(title: str, value: str, sub: str = "", color=None) -> ft.Container:
    """Cartão de indicador. `sub` sempre renderiza (mesmo vazio) para os
    cartões ficarem com a mesma altura e alinharem na grade responsiva."""
    items = [
        ft.Text(title, color=palette.TEXT_SECONDARY, size=12),
        ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
        ft.Text(sub or "", size=11, color=palette.TEXT_SECONDARY),
    ]
    return ft.Container(
        bgcolor=palette.SURFACE,
        border=ft.Border.all(1, palette.BORDER),
        border_radius=10,
        padding=16,
        # 4 por linha em telas grandes, 2 em médias, 1 em pequenas.
        # Breakpoints superiores precisam vir explícitos: o Flet usa a chave
        # definida mais próxima abaixo do tamanho atual.
        col={"col": 3, "xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 3},
        content=ft.Column(items, spacing=6),
    )


def _legend_item(color: str, label: str) -> ft.Row:
    return ft.Row(
        [
            ft.Container(width=10, height=10, border_radius=3, bgcolor=color),
            ft.Text(label, size=11, color=palette.TEXT_SECONDARY),
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _panel(title: str, chart: ft.Control, legend: list[ft.Control]) -> ft.Container:
    return ft.Container(
        bgcolor=palette.SURFACE,
        border=ft.Border.all(1, palette.BORDER),
        border_radius=10,
        padding=16,
        col={"col": 6, "xs": 12, "sm": 12, "md": 12, "lg": 6, "xl": 6},
        content=ft.Column(
            [
                ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
                ft.Row(legend, spacing=14),
                ft.Row([chart], scroll=ft.ScrollMode.AUTO),
            ],
            spacing=8,
        ),
    )


def _short_label(label: str) -> str:
    """Rótulo compacto para o eixo do gráfico de barras (ex.: 'Moda')."""
    words = label.split()
    if len(words) > 1:
        return words[0][:4]
    return label[:4]


def _department_chart(report) -> ffc.BarChart:
    """Barras lado a lado: meta (cinza) e realizado (cor do status) por departamento."""
    groups = [
        ffc.BarChartGroup(
            x=index,
            rods=[
                ffc.BarChartRod(
                    to_y=round(result.meta, 2),
                    color=_META_ROD,
                    width=12,
                    border_radius=4,
                ),
                ffc.BarChartRod(
                    to_y=round(result.realizado, 2),
                    color=_STATUS_COLOR[result.status],
                    width=12,
                    border_radius=4,
                ),
            ],
        )
        for index, result in enumerate(report.results)
    ]
    labels = [
        ffc.ChartAxisLabel(
            value=index,
            label=ft.Text(
                _short_label(result.department.label),
                size=10,
                color=palette.TEXT_SECONDARY,
            ),
        )
        for index, result in enumerate(report.results)
    ]
    top = max(
        [r.meta for r in report.results]
        + [r.realizado for r in report.results]
        + [100.0]
    )
    return ffc.BarChart(
        groups=groups,
        width=720,
        height=310,
        min_y=0,
        max_y=top * 1.1,
        border=_chart_border(),
        left_axis=ffc.ChartAxis(labels=labels, show_labels=True),
        bgcolor=palette.SURFACE,
    )


def _evolution_chart(entries: list[dict], total_meta: float) -> ffc.LineChart:
    """Curva do realizado acumulado por coleta, com a meta do dia como linha tracejada."""
    points = [
        ffc.LineChartDataPoint(x=index, y=entry["total_realizado"])
        for index, entry in enumerate(entries)
    ]
    last = max(len(entries) - 1, 1)
    meta_line = ffc.LineChartData(
        points=[
            ffc.LineChartDataPoint(x=0, y=total_meta),
            ffc.LineChartDataPoint(x=last, y=total_meta),
        ],
        color=palette.TEXT_SECONDARY,
        stroke_width=1,
        dash_pattern=[6, 5],
    )
    realizado_line = ffc.LineChartData(
        points=points,
        color=palette.PRIMARY,
        stroke_width=3,
        curved=True,
        below_line_bgcolor=ft.Colors.with_opacity(0.10, palette.PRIMARY),
    )
    labels = [
        ffc.ChartAxisLabel(
            value=index,
            label=ft.Text(
                entry["collected_at"][11:16], size=10, color=palette.TEXT_SECONDARY
            ),
        )
        for index, entry in enumerate(entries)
    ]
    top = max([e["total_realizado"] for e in entries] + [total_meta, 100.0])
    return ffc.LineChart(
        data_series=[meta_line, realizado_line],
        width=720,
        height=310,
        min_y=0,
        max_y=top * 1.1,
        min_x=-0.2,
        max_x=last + 0.2,
        border=_chart_border(),
        left_axis=ffc.ChartAxis(
            labels=[
                ffc.ChartAxisLabel(
                    value=v * top / 2,
                    label=ft.Text(f"{v * top / 2000:.0f}k", size=10,
                                  color=palette.TEXT_SECONDARY),
                )
                for v in (0, 1, 2)
            ],
            show_labels=True,
        ),
        bottom_axis=ffc.ChartAxis(labels=labels, show_labels=True),
        bgcolor=palette.SURFACE,
    )


def _empty_body(store: str) -> ft.Control:
    """Placeholder quando a loja selecionada ainda não tem coleta no dia."""
    return ft.Container(
        bgcolor=palette.SURFACE,
        border=ft.Border.all(1, palette.BORDER),
        border_radius=10,
        padding=24,
        content=ft.Column([
            ft.Text("Nenhum indicador disponível", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(
                f"Ainda não há coleta processada hoje para a loja {store}. "
                "Processe uma coleta no módulo Hora a Hora para ver os "
                "indicadores aqui.",
                color=palette.TEXT_SECONDARY,
            ),
        ]),
    )


def _body(store: str) -> ft.Control:
    """Monta cartões + gráficos para a loja: report é reconstruído do histórico."""
    report = hora_a_hora.load_dashboard_report(store)
    if report is None:
        return _empty_body(store)

    gap_color = palette.PRIMARY if report.total_gap < 0 else palette.STATUS_ABOVE
    cards = ft.ResponsiveRow(
        [
            _card(
                f"Meta do dia · {report.store}", brl(report.total_meta),
                sub=f"{report.report_date:%d/%m/%Y}",
            ),
            _card(
                "Realizado", brl(report.total_realizado),
                sub=percent(
                    report.total_realizado / report.total_meta
                    if report.total_meta else None
                ) + " da meta",
            ),
            _card(
                "Gap da loja", brl(report.total_gap),
                sub="para bater a meta" if report.total_gap < 0 else "acima da meta",
                color=gap_color,
            ),
            _card(
                "Abaixo da meta",
                str(report.departments_below_meta),
                sub=f"de {len(report.results)} departamentos",
            ),
        ],
        spacing=12,
        run_spacing=12,
    )

    dept_chart = _panel(
        "Realizado × Meta por departamento",
        _department_chart(report),
        [
            _legend_item(_META_ROD, "Meta do dia"),
            _legend_item(palette.STATUS_BELOW, "Realizado (abaixo)"),
            _legend_item(palette.STATUS_ABOVE, "Realizado (acima)"),
        ],
    )

    entries = hora_a_hora.load_history(store=report.store, on_date=report.report_date)
    if len(entries) >= 2:
        evolution = _panel(
            "Evolução da loja no dia (coletas por hora)",
            _evolution_chart(entries, report.total_meta),
            [
                _legend_item(palette.PRIMARY, "Realizado acumulado"),
                _legend_item(palette.TEXT_SECONDARY, "Meta do dia"),
            ],
        )
    else:
        evolution = ft.Container(
            bgcolor=palette.SURFACE,
            border=ft.Border.all(1, palette.BORDER),
            border_radius=10,
            padding=16,
            col={"col": 6, "xs": 12, "sm": 12, "md": 12, "lg": 6, "xl": 6},
            content=ft.Text(
                "A curva de evolução aparece após a segunda coleta do dia.",
                size=12,
                color=palette.TEXT_SECONDARY,
            ),
        )

    updated = ft.Text(
        f"Última coleta válida: {report.collected_at:%d/%m/%Y %H:%M} · "
        f"{len(entries)} coleta(s) hoje · Fonte: Hora a Hora",
        color=palette.TEXT_SECONDARY,
        size=12,
    )
    return ft.Column(
        [
            cards,
            ft.ResponsiveRow([dept_chart, evolution], spacing=12, run_spacing=12),
            updated,
        ],
        spacing=14,
    )


def build(page: ft.Page) -> ft.Control:
    """Renderiza o Dashboard; a loja inicial é a do último snapshot válido."""
    snapshot = hora_a_hora.load_snapshot()
    initial_store = snapshot.store if snapshot else config.DEFAULT_STORE
    header = ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD)
    body = ft.Container(expand=True)

    def on_store_change(event: ft.ControlEvent) -> None:
        body.content = _body(store_dropdown.value)
        page.update()

    store_dropdown = ft.Dropdown(
        label="Loja",
        width=140,
        value=initial_store,
        options=[ft.dropdown.Option(store) for store in config.E_STORE_STORES],
        # No Flet 1.0 o evento do Dropdown se chama on_select (não on_change).
        on_select=on_store_change,
    )

    body.content = _body(initial_store)
    return ft.Column(
        [
            ft.Row(
                [header, ft.Container(expand=True), store_dropdown],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            body,
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

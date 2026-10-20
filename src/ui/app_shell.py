"""Casca da aplicação: navegação lateral e troca entre as telas.

O AppShell é o único ponto que conhece todas as views. Ele também mantém um
watcher assíncrono que recarrega a tela atual sempre que aparece uma coleta
nova (o snapshot em disco muda), sem precisar reiniciar o app.
"""

import asyncio

import flet as ft

from core import palette
from services import hora_a_hora
from ui import dashboard_view, hora_a_hora_view

# Frequência com que o watcher verifica se houve uma nova coleta válida.
WATCH_INTERVAL_SECONDS = 60


class AppShell:
    """Contêiner raiz: NavigationRail (Dashboard / Hora a Hora) + área de conteúdo."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._rendered_key: tuple | None = None
        self.content = ft.Container(
            expand=True,
            padding=24,
            bgcolor=palette.BG,
        )
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=110,
            group_alignment=-0.9,
            bgcolor=palette.SURFACE,
            indicator_color=palette.PRIMARY,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.TIMELINE_OUTLINED,
                    selected_icon=ft.Icons.TIMELINE,
                    label="Hora a Hora",
                ),
            ],
            on_change=self._select,
        )

    def _snapshot_key(self):
        """Identidade da última coleta válida, ou None se ainda não existe."""
        report = hora_a_hora.load_snapshot()
        if report is None:
            return None
        return (report.store, report.collected_at.isoformat())

    def _render(self) -> None:
        """Constrói a view da aba selecionada e registra a chave do snapshot."""
        if self.rail.selected_index == 0:
            self.content.content = dashboard_view.build(self.page)
        else:
            self.content.content = hora_a_hora_view.build(self.page)
        self._rendered_key = self._snapshot_key()

    def _select(self, event: ft.ControlEvent) -> None:
        self._render()
        self.page.update()

    async def _watch_for_new_collection(self) -> None:
        """Loop de fundo: recarrega a tela quando surge uma coleta mais recente.

        Erros de leitura são ignorados de propósito — o watcher não deve
        derrubar a UI se o snapshot estiver sendo reescrito neste instante.
        """
        while True:
            await asyncio.sleep(WATCH_INTERVAL_SECONDS)
            try:
                if self._snapshot_key() != self._rendered_key:
                    self._render()
                    self.page.update()
            except Exception:
                continue

    def build(self) -> ft.Control:
        self._render()
        # run_task só existe em builds desktop/web com eventos assíncronos.
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._watch_for_new_collection)
        return ft.Row(
            [
                self.rail,
                ft.VerticalDivider(width=1, color=palette.BORDER),
                self.content,
            ],
            expand=True,
        )

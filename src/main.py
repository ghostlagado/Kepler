"""Ponto de entrada do Kepler (Flet desktop/web).

A janela é montada aqui; todo o resto vive em `ui/` (apresentação),
`services/` (pipeline) e `domain/` (regras de negócio testáveis sem UI).
"""

import logging

import flet as ft

from core import config, palette, theme
from ui.app_shell import AppShell


async def main(page: ft.Page):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    page.title = "Kepler"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = theme.build_theme()
    page.bgcolor = palette.BG
    page.padding = 0

    page.add(AppShell(page).build())


ft.run(main)

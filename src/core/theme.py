"""Constrói o ft.Theme a partir da paleta (cores Material mapeadas uma a uma)."""

import flet as ft

from core import palette


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=palette.PRIMARY,
            on_primary=ft.Colors.WHITE,
            secondary=palette.PRIMARY,
            surface=palette.SURFACE,
            on_surface=palette.TEXT,
            on_surface_variant=palette.TEXT_SECONDARY,
            surface_container=palette.SURFACE,
        ),
        font_family="Roboto",
    )

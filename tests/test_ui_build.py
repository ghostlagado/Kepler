"""Smoke test: monta toda a árvore de controles Flet sem renderer.

Pega erros de API (kwargs inválidos) nas views sem precisar abrir a janela.
"""

import types

import flet as ft

from core import theme
from ui import dashboard_view, hora_a_hora_view
from ui.app_shell import AppShell


def stub_page():
    page = types.SimpleNamespace()
    page.overlay = []
    page.services = []
    page.update = lambda: None
    return page


def test_theme_builds():
    assert isinstance(theme.build_theme(), ft.Theme)


def test_shell_and_views_build():
    page = stub_page()
    shell = AppShell(page)
    assert isinstance(shell.build(), ft.Control)

    shell._select(ft.ControlEvent(control=shell.rail, name="", data=""))
    assert isinstance(shell.content.content, ft.Control)

    assert isinstance(dashboard_view.build(page), ft.Control)
    assert isinstance(hora_a_hora_view.build(page), ft.Control)

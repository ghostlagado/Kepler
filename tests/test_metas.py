from datetime import date, datetime

import pytest
from openpyxl import Workbook

from domain.metas import MetasError, load_daily_metas


def make_metas_file(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["Filtros aplicados", "", "", ""])
    ws.append(["Data", "Local", "Grupo Operações", "Soma de Meta Total Loja"])
    ws.append(["", "", "", ""])
    rows = [
        (datetime(2026, 10, 20), "L062", "Perfumaria", 2000.0),
        (datetime(2026, 10, 20), "L062", "Calçados", 1000.0),
        (datetime(2026, 10, 20), "L062", "Grupo Desconhecido", 50.0),
        (datetime(2026, 10, 20), "L051", "Perfumaria", 999.0),
        (datetime(2026, 10, 19), "L062", "Perfumaria", 777.0),
        (datetime(2026, 10, 20), "L062", "Relógios", 300.5),
    ]
    for row in rows:
        ws.append(row)
    path = tmp_path / "metas.xlsx"
    wb.save(path)
    return path


def test_filters_by_date_store_and_group(tmp_path):
    path = make_metas_file(tmp_path)
    metas = load_daily_metas(path, "L062", date(2026, 10, 20))
    assert metas == {"beleza": 2000.0, "calcados": 1000.0, "relogios": 300.5}


def test_string_dates_are_accepted(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["meta", "headers"])
    ws.append(["row 3"])
    ws.append(["row 4 filler"])
    ws.append(["2026-10-20 00:00:00", "L062", "Basket", 12.5])
    path = tmp_path / "metas_str.xlsx"
    wb.save(path)
    assert load_daily_metas(path, "L062", date(2026, 10, 20)) == {"basket": 12.5}


def test_missing_file_raises_metas_error(tmp_path):
    with pytest.raises(MetasError):
        load_daily_metas(tmp_path / "nao_existe.xlsx", "L062", date(2026, 10, 20))

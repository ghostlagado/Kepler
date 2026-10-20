from datetime import date, datetime

from openpyxl import Workbook

from services import hora_a_hora


def hxh_line(value: str) -> str:
    tokens = [f"t{i}" for i in range(10)]
    tokens[5] = value
    tokens[1] = "280-01"
    return " ".join(tokens)


def make_metas(tmp_path):
    wb = Workbook()
    ws = wb.active
    for row in [
        ("Data", "Local", "Grupo", "Meta"),
        ("", "", "", ""),
        ("", "", "", ""),
        (datetime(2026, 10, 20), "L062", "Perfumaria", 1000.0),
        (datetime(2026, 10, 20), "L062", "Basket", 500.0),
    ]:
        ws.append(row)
    path = tmp_path / "metas.xlsx"
    wb.save(path)
    return path


def context(tmp_path):
    return {
        "metas_path": make_metas(tmp_path),
        "data_dir": tmp_path / "data",
        "report_date": date(2026, 10, 20),
        "collected_at": datetime(2026, 10, 20, 12, 0),
    }


def test_valid_run_persists_snapshot_and_raw(tmp_path):
    outcome = hora_a_hora.run("L062", hxh_line("1.500,25"), **context(tmp_path))
    assert outcome.ok, outcome.errors
    report = outcome.report
    beleza = next(r for r in report.results if r.department.key == "beleza")
    assert beleza.realizado == 1500.25
    assert beleza.gap == 500.25
    assert outcome.raw_path.exists()
    assert hora_a_hora.load_snapshot(outcome.snapshot_path.parent) == report


def test_empty_collection_is_rejected(tmp_path):
    outcome = hora_a_hora.run("L062", "   ", **context(tmp_path))
    assert not outcome.ok
    assert "vazia" in outcome.errors[0]


def test_broken_line_keeps_last_valid_snapshot(tmp_path):
    ctx = context(tmp_path)
    good = hora_a_hora.run("L062", hxh_line("1.500,25"), **ctx)
    assert good.ok

    broken = hora_a_hora.run("L062", "280-01 valor sem formato", **ctx)
    assert not broken.ok
    assert "linha" in broken.errors[0]

    current = hora_a_hora.load_snapshot(ctx["data_dir"])
    assert current == good.report


def test_missing_metas_file_keeps_previous_result(tmp_path):
    ctx = context(tmp_path)
    good = hora_a_hora.run("L062", hxh_line("10,00"), **ctx)
    assert good.ok

    ctx["metas_path"] = tmp_path / "nao_existe.xlsx"
    failed = hora_a_hora.run("L062", hxh_line("99,00"), **ctx)
    assert not failed.ok
    assert hora_a_hora.load_snapshot(ctx["data_dir"]) == good.report


def test_store_without_metas_for_the_day_is_rejected(tmp_path):
    outcome = hora_a_hora.run("L051", hxh_line("10,00"), **context(tmp_path))
    assert not outcome.ok
    assert "nenhuma meta" in outcome.errors[0]


def test_valid_run_appends_history_entry(tmp_path):
    ctx = context(tmp_path)
    outcome = hora_a_hora.run("L062", hxh_line("1.500,25"), **ctx)
    assert outcome.ok
    entries = hora_a_hora.load_history(ctx["data_dir"])
    assert len(entries) == 1
    entry = entries[0]
    assert entry["store"] == "L062"
    assert entry["date"] == "2026-10-20"
    assert entry["total_realizado"] == 1500.25
    assert entry["departments"]["beleza"] == 1500.25


def test_failed_run_does_not_append_history(tmp_path):
    ctx = context(tmp_path)
    assert hora_a_hora.run("L062", hxh_line("10,00"), **ctx).ok
    assert not hora_a_hora.run("L062", "   ", **ctx).ok
    assert len(hora_a_hora.load_history(ctx["data_dir"])) == 1


def test_load_history_filters_by_store_and_date(tmp_path):
    ctx = context(tmp_path)
    hora_a_hora.run("L062", hxh_line("10,00"), **ctx)

    wb = Workbook()
    ws = wb.active
    for row in [
        ("Data", "Local", "Grupo", "Meta"),
        ("", "", "", ""),
        ("", "", "", ""),
        (datetime(2026, 10, 21), "L051", "Perfumaria", 800.0),
    ]:
        ws.append(row)
    other_metas = tmp_path / "other_metas.xlsx"
    wb.save(other_metas)

    hora_a_hora.run(
        "L051", hxh_line("20,00"),
        metas_path=other_metas,
        data_dir=ctx["data_dir"],
        report_date=date(2026, 10, 21),
        collected_at=datetime(2026, 10, 21, 9, 0),
    )

    assert len(hora_a_hora.load_history(ctx["data_dir"])) == 2
    assert len(hora_a_hora.load_history(ctx["data_dir"], store="L062")) == 1
    assert len(hora_a_hora.load_history(
        ctx["data_dir"], on_date=date(2026, 10, 21))) == 1
    assert hora_a_hora.load_history(
        ctx["data_dir"], store="L999") == []


def test_dashboard_report_rebuilds_store_from_history(tmp_path):
    ctx = context(tmp_path)
    assert hora_a_hora.run("L062", hxh_line("1.500,25"), **ctx).ok

    report = hora_a_hora.load_dashboard_report(
        "L062", on_date=date(2026, 10, 20),
        metas_path=ctx["metas_path"], data_dir=ctx["data_dir"],
    )
    assert report is not None
    assert report.total_realizado == 1500.25
    assert report.total_meta == 1500.0
    beleza = next(r for r in report.results if r.department.key == "beleza")
    assert beleza.realizado == 1500.25


def test_dashboard_report_none_without_collection(tmp_path):
    ctx = context(tmp_path)
    assert hora_a_hora.load_dashboard_report(
        "L062", on_date=date(2026, 10, 20),
        metas_path=ctx["metas_path"], data_dir=ctx["data_dir"],
    ) is None

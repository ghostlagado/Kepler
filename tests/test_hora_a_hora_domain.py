from datetime import date, datetime

from domain.departments import DEPARTMENTS_BY_KEY
from domain.hora_a_hora import (
    STATUS_ABOVE,
    STATUS_BELOW,
    STATUS_NEAR,
    STATUS_NO_META,
    build_report,
    report_from_dict,
    report_to_dict,
)

WHEN = datetime(2026, 10, 20, 15, 30)


def make(values=None, metas=None):
    return build_report("L062", date(2026, 10, 20), WHEN, values or {}, metas or {})


def test_gap_is_realizado_minus_meta():
    report = make(
        values={"560-": 100.0},
        metas={"oculos_biju": 250.0},
    )
    result = next(r for r in report.results if r.department.key == "oculos_biju")
    assert result.realizado == 100.0
    assert result.gap == -150.0
    assert result.status == STATUS_BELOW


def test_status_boundaries():
    meta = 100.0
    for realizado, expected in (
        (99.99, STATUS_BELOW),
        (100.0, STATUS_NEAR),
        (105.0, STATUS_NEAR),
        (105.01, STATUS_ABOVE),
    ):
        report = make(values={"572-": realizado}, metas={"basket": meta})
        result = next(r for r in report.results if r.department.key == "basket")
        assert result.status == expected, realizado


def test_no_meta_configured():
    report = make(values={"550-": 10.0})
    result = next(r for r in report.results if r.department.key == "relogios")
    assert result.meta == 0.0
    assert result.status == STATUS_NO_META
    assert result.percent is None


def test_department_aggregates_all_its_dco_codes():
    report = make(values={"280-": 10.0, "285-": 5.5, "289-": 4.5})
    result = next(r for r in report.results if r.department.key == "beleza")
    assert result.realizado == 20.0


def test_store_total_matches_departments():
    report = make(
        values={"280-": 10.0, "572-": 40.0},
        metas={"beleza": 25.0, "basket": 100.0},
    )
    assert report.total_realizado == sum(r.realizado for r in report.results)
    assert report.total_meta == sum(r.meta for r in report.results)
    assert report.total_gap == report.total_realizado - report.total_meta
    assert report.departments_below_meta == 2


def test_snapshot_roundtrip():
    report = make(
        values={DEPARTMENTS_BY_KEY["feminino"].dco_codes[0]: 33.33},
        metas={"feminino": 100.0},
    )
    restored = report_from_dict(report_to_dict(report, source="x.txt"))
    assert restored == report

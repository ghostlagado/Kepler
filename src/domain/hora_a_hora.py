"""Modelo de domínio do relatório Hora a Hora — sem nenhuma dependência de UI.

Regras idênticas ao PDV_V2: gap = realizado − meta; um departamento está
"abaixo" com menos de 100% da meta, "próximo" entre 100% e 105%, e "acima"
de 105% em diante.
"""

from dataclasses import dataclass
from datetime import date, datetime

from domain.departments import DEPARTMENTS, Department

STATUS_BELOW = "below"
STATUS_NEAR = "near"
STATUS_ABOVE = "above"
STATUS_NO_META = "no_meta"

# Departamentos entre a meta e 5% acima são considerados "próximos da meta".
_NEAR_UP_TO = 1.05


@dataclass(frozen=True)
class DepartmentResult:
    """Desempenho de um departamento no dia: meta × realizado."""

    department: Department
    meta: float
    realizado: float

    @property
    def gap(self) -> float:
        return self.realizado - self.meta

    @property
    def percent(self) -> float | None:
        if self.meta <= 0:
            return None
        return self.realizado / self.meta

    @property
    def status(self) -> str:
        percent = self.percent
        if percent is None:
            return STATUS_NO_META
        if percent < 1:
            return STATUS_BELOW
        if percent <= _NEAR_UP_TO:
            return STATUS_NEAR
        return STATUS_ABOVE


@dataclass(frozen=True)
class HourlyReport:
    """Fotografia de uma loja em uma coleta: um resultado por departamento."""

    store: str
    report_date: date
    collected_at: datetime
    results: tuple[DepartmentResult, ...]

    @property
    def total_meta(self) -> float:
        return sum(r.meta for r in self.results)

    @property
    def total_realizado(self) -> float:
        return sum(r.realizado for r in self.results)

    @property
    def total_gap(self) -> float:
        return self.total_realizado - self.total_meta

    @property
    def departments_below_meta(self) -> int:
        return sum(1 for r in self.results if r.status == STATUS_BELOW)


def build_report(
    store: str,
    report_date: date,
    collected_at: datetime,
    values_by_code: dict[str, float],
    metas_by_dept: dict[str, float],
) -> HourlyReport:
    """Agrega os valores por DCO nos departamentos correspondentes."""
    results = []
    for dept in DEPARTMENTS:
        realizado = sum(values_by_code.get(code, 0.0) for code in dept.dco_codes)
        results.append(
            DepartmentResult(
                department=dept,
                meta=float(metas_by_dept.get(dept.key, 0.0)),
                realizado=round(realizado, 2),
            )
        )
    return HourlyReport(store, report_date, collected_at, tuple(results))


def report_to_dict(report: HourlyReport, source: str | None = None) -> dict:
    return {
        "store": report.store,
        "date": report.report_date.isoformat(),
        "collected_at": report.collected_at.isoformat(timespec="seconds"),
        "source": source,
        "results": [
            {
                "key": r.department.key,
                "label": r.department.label,
                "meta": r.meta,
                "realizado": r.realizado,
                "gap": round(r.gap, 2),
                "status": r.status,
            }
            for r in report.results
        ],
    }


def report_from_dict(data: dict) -> HourlyReport:
    from domain.departments import DEPARTMENTS_BY_KEY

    results = tuple(
        DepartmentResult(
            department=DEPARTMENTS_BY_KEY[item["key"]],
            meta=item["meta"],
            realizado=item["realizado"],
        )
        for item in data["results"]
    )
    return HourlyReport(
        store=data["store"],
        report_date=date.fromisoformat(data["date"]),
        collected_at=datetime.fromisoformat(data["collected_at"]),
        results=results,
    )

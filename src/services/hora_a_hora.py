"""Pipeline Hora a Hora: coleta bruta -> parser -> metas -> snapshot válido.

Um processamento com erros nunca sobrescreve o último resultado válido.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from core import config
from domain.departments import DEPARTMENTS
from domain.hora_a_hora import (
    DepartmentResult,
    HourlyReport,
    build_report,
    report_from_dict,
    report_to_dict,
)
from domain.metas import MetasError, load_daily_metas
from parsers.dco_text import parse_dco_text
from domain.departments import ALL_DCO_CODES


@dataclass
class RunOutcome:
    """Resultado de um processamento: relatório válido ou lista de erros."""
    ok: bool
    report: HourlyReport | None = None
    errors: list[str] = field(default_factory=list)
    raw_path: Path | None = None
    snapshot_path: Path | None = None


def _save_raw(text: str, when: datetime, raw_dir: Path, store: str) -> Path:
    """Arquiva a coleta bruta (auditoria); o nome inclui loja e timestamp."""
    target_dir = raw_dir / "hora_a_hora"
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{when:%Y%m%d_%H%M%S}_{store}.txt"
    path.write_text(text, encoding="utf-8")
    return path


def _save_snapshot(payload: dict, snapshot_path: Path) -> None:
    """Escrita atômica (tmp + os.replace) para nunca deixar JSON truncado."""
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = snapshot_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, snapshot_path)


def _append_history(report: HourlyReport, history_path: Path) -> None:
    """Acrescenta uma linha ao JSONL de histórico (base da curva do Dashboard)."""
    history_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "store": report.store,
        "date": report.report_date.isoformat(),
        "collected_at": report.collected_at.isoformat(timespec="seconds"),
        "total_meta": round(report.total_meta, 2),
        "total_realizado": round(report.total_realizado, 2),
        "departments": {
            r.department.key: round(r.realizado, 2) for r in report.results
        },
    }
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run(
    store: str,
    raw_text: str,
    report_date: date | None = None,
    collected_at: datetime | None = None,
    metas_path: Path | None = None,
    data_dir: Path | None = None,
) -> RunOutcome:
    """Processa uma coleta completa. Em caso de erro, nada em disco é alterado.

    Ordem: valida entrada -> carrega metas do dia -> parseia DCOs -> monta o
    relatório -> só então grava raw/snapshot/histórico.
    """
    report_date = report_date or date.today()
    collected_at = collected_at or datetime.now()
    data_dir = Path(data_dir or config.DATA_DIR)
    metas_path = Path(metas_path or config.METAS_FILE)
    snapshot_path = data_dir / "hora_a_hora_snapshot.json"

    if not raw_text.strip():
        return RunOutcome(ok=False, errors=["coleta vazia: nada foi processado"])

    try:
        metas = load_daily_metas(metas_path, store, report_date)
    except MetasError as exc:
        return RunOutcome(ok=False, errors=[
            f"metas indisponíveis ({exc}); último resultado válido mantido",
        ])
    if not metas:
        return RunOutcome(ok=False, errors=[
            f"nenhuma meta encontrada para {store} em {report_date:%d/%m/%Y}; "
            "atualize a planilha de metas antes de processar",
        ])

    parsed = parse_dco_text(raw_text, ALL_DCO_CODES)
    if parsed.issues:
        return RunOutcome(ok=False, errors=[
            f"linha {issue.line_number}: {issue.reason}; último resultado válido mantido"
            for issue in parsed.issues
        ])

    report = build_report(store, report_date, collected_at, parsed.values_by_code, metas)
    raw_path = _save_raw(raw_text, collected_at, data_dir / "raw", store)
    payload = report_to_dict(report, source=str(raw_path))
    snapshot_path = data_dir / "hora_a_hora_snapshot.json"
    _save_snapshot(payload, snapshot_path)
    _append_history(report, data_dir / "hora_a_hora_history.jsonl")
    return RunOutcome(ok=True, report=report, raw_path=raw_path, snapshot_path=snapshot_path)


def load_history(
    data_dir: Path | None = None,
    store: str | None = None,
    on_date: date | None = None,
) -> list[dict]:
    """Lê o JSONL filtrando loja/data; linhas corrompidas são descartadas."""
    path = Path(data_dir or config.DATA_DIR) / "hora_a_hora_history.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if store and entry.get("store") != store:
            continue
        if on_date and entry.get("date") != on_date.isoformat():
            continue
        entries.append(entry)
    entries.sort(key=lambda e: e.get("collected_at", ""))
    return entries


def load_snapshot(data_dir: Path | None = None) -> HourlyReport | None:
    """Último relatório válido persistido; None se não existe ou está corrompido."""
    path = Path(data_dir or config.DATA_DIR) / "hora_a_hora_snapshot.json"
    if not path.exists():
        return None
    try:
        return report_from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return None


def load_dashboard_report(
    store: str,
    on_date: date | None = None,
    metas_path: Path | None = None,
    data_dir: Path | None = None,
) -> HourlyReport | None:
    """Relatório do dia de qualquer loja: último realizado do histórico + metas."""
    on_date = on_date or date.today()
    entries = load_history(data_dir, store=store, on_date=on_date)
    if not entries:
        snapshot = load_snapshot(data_dir)
        if snapshot and snapshot.store == store and snapshot.report_date == on_date:
            return snapshot
        return None
    latest = entries[-1]
    try:
        metas = load_daily_metas(
            Path(metas_path or config.METAS_FILE), store, on_date
        )
    except MetasError:
        metas = {}
    realized = latest.get("departments", {})
    results = tuple(
        DepartmentResult(
            department=dept,
            meta=float(metas.get(dept.key, 0.0)),
            realizado=float(realized.get(dept.key, 0.0)),
        )
        for dept in DEPARTMENTS
    )
    return HourlyReport(
        store=store,
        report_date=on_date,
        collected_at=datetime.fromisoformat(latest["collected_at"]),
        results=results,
    )

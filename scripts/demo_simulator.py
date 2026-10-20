#!/usr/bin/env python3
"""Simulador DEMO do Kepler — gera metas e coletas Hora a Hora fictícias.

Uso (a partir da raiz do projeto):

    venv/bin/python scripts/demo_simulator.py --backfill   # dia completo até agora
    venv/bin/python scripts/demo_simulator.py              # uma coleta (hora atual)
    venv/bin/python scripts/demo_simulator.py --loop       # roda para sempre, 1 coleta/hora

Os números são 100% fictícios, determinísticos por (data, hora): cada hora
adiciona um incremento de vendas seguindo curva intradiária de shopping
(movimento no almoço e fim da tarde), com fator próprio por departamento —
alguns terminam o dia acima da meta, outros abaixo.
"""

import argparse
import random
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core import config  # noqa: E402
from domain.departments import DEPARTMENTS  # noqa: E402
from services import hora_a_hora  # noqa: E402

OPEN_HOUR, CLOSE_HOUR = 9, 21

# Peso de cada faixa horária (9h..21h) na venda do dia — soma = 1.
HOUR_WEIGHTS = [0.02, 0.05, 0.08, 0.11, 0.13, 0.14, 0.13, 0.11, 0.10, 0.06, 0.03, 0.02, 0.02]

# Metas-base de L062 (valores históricos de pln/horaxhora.xlsx do PDV_V2).
BASE_METAS = {
    "beleza": 2078.82,
    "calcados": 1137.98,
    "tecnologia": 2225.30,
    "feminino": 16998.51,
    "infantil": 3783.41,
    "masculino": 9038.50,
    "moda_casa": 2070.86,
    "oculos_biju": 295.90,
    "basket": 363.29,
    "relogios": 399.58,
}

_FILLERS = ["T2", "CTB", "VENDA", "PR", "LOJA", "AC", "ITEM", "TOTAL", "REG", "PISO", "FRENTE"]


def _fmt(value: float) -> str:
    """Formata em padrão brasileiro (1.234,56), igual ao relatório corporativo."""
    return f"{value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def store_scale(store: str) -> float:
    """Fator de tamanho da loja (L062=1.0; demais determinístico por loja)."""
    if store == "L062":
        return 1.0
    return random.Random(f"scale-{store}").uniform(0.3, 1.2)


def generate_metas(path: Path, day: date, stores: list[str]) -> None:
    """Escreve metas/metas.xlsx fictícias no formato da planilha corporativa."""
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["Filtros aplicados (DEMO)", "", "", ""])
    ws.append(["Data", "Local", "Grupo Operações", "Soma de Meta Total Loja"])
    ws.append(["", "", "", ""])
    stamp = datetime(day.year, day.month, day.day)
    for store in stores:
        scale = store_scale(store)
        for dept in DEPARTMENTS:
            ws.append([stamp, store, dept.meta_group, round(BASE_METAS[dept.key] * scale, 2)])
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def department_factor(day: date, store: str, dept_key: str) -> float:
    return random.Random(f"factor-{day}-{store}-{dept_key}").uniform(0.55, 1.35)


def code_share(day: date, code: str) -> float:
    return random.Random(f"share-{day}-{code}").uniform(0.3, 2.0)


def cumulative_by_code(day: date, store: str, hour: int) -> dict[str, float]:
    """Venda acumulada por DCO até o fim da faixa horária `hour` (inclusive)."""
    if hour < OPEN_HOUR:
        return {}
    scale = store_scale(store)
    weights: dict[str, float] = {}
    totals: dict[str, float] = {}
    for dept in DEPARTMENTS:
        factor = department_factor(day, store, dept.key) * scale
        shares = {code: code_share(day, code) for code in dept.dco_codes}
        total_share = sum(shares.values())
        for hour_slot in range(OPEN_HOUR, min(hour, CLOSE_HOUR) + 1):
            weight = HOUR_WEIGHTS[hour_slot - OPEN_HOUR]
            noise = random.Random(f"noise-{day}-{dept.key}-{hour_slot}").uniform(0.85, 1.25)
            increment = BASE_METAS[dept.key] * factor * weight * noise
            for code in dept.dco_codes:
                weights[code] = shares[code] / total_share
                totals[code] = totals.get(code, 0.0) + increment * weights[code]
    return {code: round(value, 2) for code, value in totals.items() if value >= 0.01}


def build_report_text(day: date, store: str, hour: int, values: dict[str, float]) -> str:
    """Monta o texto bruto no formato do relatório de DCOs.

    Cada linha recebe um número de palavras aleatório (10..17); o valor é
    posicionado no índice que o parser legado espera para aquela contagem.
    """
    rng = random.Random(f"lines-{day}-{store}-{hour}")
    lines = [
        "RELATORIO PARCIAL DE VENDAS POR DCO (DEMO)",
        f"DATA {day:%d/%m/%Y}  ATUALIZADO {hour:02d}:00",
        "",
    ]
    for code, value in sorted(values.items()):
        word_count = rng.choice([10, 11, 12, 13, 14, 15, 16, 17])
        index = {10: 5, 11: 6, 12: 7, 13: 8, 14: 5, 15: 6, 16: 7, 17: 8}[word_count]
        tokens = [rng.choice(_FILLERS) for _ in range(word_count)]
        tokens[1] = f"{code}01"
        tokens[index] = _fmt(value)
        lines.append(" ".join(tokens))
    return "\n".join(lines)


def run_tick(day: date, hour: int, verbose: bool = True) -> bool:
    """Gera a coleta dessa hora para TODAS as lojas (padrão por último para ficar no snapshot)."""
    stores = sorted(config.E_STORE_STORES, key=lambda s: s == config.DEFAULT_STORE)
    ok = False
    for store in stores:
        values = cumulative_by_code(day, store, hour)
        text = build_report_text(day, store, hour, values)
        outcome = hora_a_hora.run(
            store,
            text,
            report_date=day,
            collected_at=datetime(day.year, day.month, day.day, min(hour, 23), 0),
        )
        ok = ok or outcome.ok
        if verbose and store == config.DEFAULT_STORE:
            if outcome.ok:
                r = outcome.report
                pct = r.total_realizado / r.total_meta * 100 if r.total_meta else 0
                print(
                    f"[demo] {day:%d/%m} {hour:02d}:00  loja {store}  "
                    f"realizado R$ {r.total_realizado:,.2f}"
                    f"  meta R$ {r.total_meta:,.2f}  ({pct:.1f}% da meta,"
                    f" {r.departments_below_meta} depto(s) abaixo)"
                )
            else:
                print("[demo] falha:", " · ".join(outcome.errors))
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backfill", action="store_true",
                        help="gera todas as coletas do dia até a hora atual")
    parser.add_argument("--loop", action="store_true",
                        help="mantém rodando e gera uma coleta nova a cada hora")
    parser.add_argument("--date", type=lambda s: date.fromisoformat(s), default=date.today())
    parser.add_argument("--metas-only", action="store_true", help="apenas (re)gera metas.xlsx")
    args = parser.parse_args()

    metas_path = config.METAS_FILE
    if args.metas_only or not metas_path.exists():
        generate_metas(metas_path, args.date, config.E_STORE_STORES)
        print(f"[demo] metas fictícias geradas em {metas_path}")
        if args.metas_only:
            return

    now = datetime.now()
    day = args.date
    current_hour = now.hour if day == now.date() else CLOSE_HOUR

    if args.backfill:
        for hour in range(OPEN_HOUR, current_hour + 1):
            run_tick(day, hour)
    else:
        run_tick(day, max(current_hour, OPEN_HOUR))

    if args.loop:
        print("[demo] modo contínuo: próxima coleta no início da próxima hora (Ctrl+C para sair)")
        last_done = None
        while True:
            now = datetime.now()
            if now.hour != last_done and OPEN_HOUR <= now.hour <= CLOSE_HOUR:
                generate_metas(metas_path, now.date(), config.E_STORE_STORES)
                run_tick(now.date(), now.hour)
                last_done = now.hour
            time.sleep(30)


if __name__ == "__main__":
    main()

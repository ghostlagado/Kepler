"""Formatação numérica em padrão brasileiro para a interface."""


def brl(value: float) -> str:
    """1234567.89 -> 'R$ 1.234.567,89' (ponto = milhar, vírgula = decimal)."""
    text = f"{value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
    return f"R$ {text}"


def percent(value: float | None) -> str:
    """0.136 -> '13,6%'; None vira um traço (sem meta cadastrada)."""
    if value is None:
        return "—"
    return f"{value * 100:.1f}%".replace(".", ",")

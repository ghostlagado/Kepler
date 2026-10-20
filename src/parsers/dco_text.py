"""Parser do relatório bruto de DCOs (colado do sistema corporativo).

Regra herdada do legado (hxh.py): em uma linha que contém o código do DCO,
a posição do valor monetário depende da quantidade de palavras da linha.
"""

from dataclasses import dataclass, field

_INDEX_BY_WORD_COUNT = {
    10: 5, 11: 6, 12: 7, 13: 8,
    14: 5, 15: 6, 16: 7, 17: 8,
}


@dataclass
class ParseIssue:
    line_number: int
    reason: str
    raw_line: str


@dataclass
class ParseResult:
    values_by_code: dict[str, float] = field(default_factory=dict)
    matched_lines: int = 0
    issues: list[ParseIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues


def normalize_money(token: str) -> float:
    """Converte '1.234,56' (padrão pt-BR do sistema corporativo) em float."""
    value = token.replace(".", "").replace(",", ".")
    return float(value)


def parse_dco_text(text: str, codes: list[str] | tuple[str, ...]) -> ParseResult:
    """Linha a linha: ignora o que não é DCO conhecido, acumula o valor no código.

    Uma linha pode conter mais de um código (ex.: "530-" dentro de "1530-");
    o valor é somado em todos os códigos encontrados, como no legado.
    """
    result = ParseResult()
    for line_number, line in enumerate(text.splitlines(), start=1):
        found = [code for code in codes if code in line]
        if not found:
            continue
        result.matched_lines += 1
        tokens = line.split()
        word_count = len(tokens)
        index = _INDEX_BY_WORD_COUNT.get(word_count)
        if index is None or index >= word_count:
            result.issues.append(ParseIssue(
                line_number,
                f"formato de linha não reconhecido ({word_count} palavras)",
                line,
            ))
            continue
        try:
            value = normalize_money(tokens[index])
        except ValueError:
            result.issues.append(ParseIssue(
                line_number,
                f"valor monetário inválido: {tokens[index]!r}",
                line,
            ))
            continue
        for code in found:
            result.values_by_code[code] = (
                result.values_by_code.get(code, 0.0) + value
            )
    return result

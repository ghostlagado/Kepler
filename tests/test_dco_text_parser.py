from parsers.dco_text import normalize_money, parse_dco_text

CODES = ("100-", "560-", "530-E")


def line(count: int, value_token: str) -> str:
    """Monta uma linha com `count` palavras, valor na posição esperada."""
    index = {10: 5, 11: 6, 12: 7, 13: 8, 14: 5, 15: 6, 16: 7, 17: 8}[count]
    tokens = [f"t{i}" for i in range(count)]
    tokens[index] = value_token
    tokens[1] = "100-01"
    return " ".join(tokens)


def test_thousand_separator_and_decimal_comma():
    result = parse_dco_text(line(10, "1.234,56"), CODES)
    assert result.ok
    assert result.values_by_code == {"100-": 1234.56}


def test_value_positions_by_word_count():
    text = "\n".join(
        [line(10, "10,00"), line(13, "20,00"), line(14, "30,00"), line(17, "40,00")]
    )
    result = parse_dco_text(text, ("100-",))
    assert result.ok
    assert result.values_by_code["100-"] == 100.00


def test_multiple_lines_same_code_are_summed():
    result = parse_dco_text("\n".join([line(10, "5,50"), line(10, "4,50")]), CODES)
    assert result.values_by_code["100-"] == 10.0


def test_unsupported_word_count_becomes_issue():
    result = parse_dco_text("100-01 a b c d e f g", CODES)
    assert not result.ok
    assert "não reconhecido" in result.issues[0].reason


def test_invalid_money_becomes_issue():
    result = parse_dco_text(line(10, "abc,de"), CODES)
    assert not result.ok
    assert "inválido" in result.issues[0].reason


def test_lines_without_codes_are_ignored():
    result = parse_dco_text("RELATORIO DE VENDAS\nDATA 08/01/2023", CODES)
    assert result.ok
    assert result.matched_lines == 0
    assert result.values_by_code == {}


def test_normalize_money():
    assert normalize_money("2.500,75") == 2500.75
    assert normalize_money("54,99") == 54.99
    assert normalize_money("1000") == 1000.0

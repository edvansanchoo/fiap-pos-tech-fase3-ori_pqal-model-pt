from tools.parse_input import parse_data, parse_int_id, parse_limite


def test_parse_int_id_from_messy_string():
    assert parse_int_id("1234 (ID do paciente João)") == 1234


def test_parse_int_id_pure_number():
    assert parse_int_id("42") == 42


def test_parse_limite_default():
    assert parse_limite("") == 5


def test_parse_data_iso():
    assert str(parse_data("1980-05-15")) == "1980-05-15"


def test_parse_data_br():
    assert str(parse_data("15/05/1980")) == "1980-05-15"

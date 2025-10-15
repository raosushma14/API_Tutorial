def format_money(v):
    return f"${v:,.2f}" if v is not None else "-"

def test_format_money():
    assert format_money(1234.5) == "$1,234.50"
    assert format_money(None) == "-"

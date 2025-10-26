import togura.html as html


def test_filename():
    assert html.filename("https://example.jp/12345") == "12345"

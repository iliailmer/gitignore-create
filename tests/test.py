from ignore.make_request import make_request


def test_language(lang: str) -> None:
    response = make_request()
    assert response.status_code == 200
    pass

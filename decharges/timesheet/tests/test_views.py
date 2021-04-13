def test_tests(client):
    res = client.get("/")
    assert res.status_code == 200

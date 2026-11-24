
def test_home_page(client):

    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["application"] == "SIGCA"

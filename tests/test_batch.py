def test_batch_screen_requires_auth(client):
    response = client.post("/screen/batch", json={"customer_ids": []})
    assert response.status_code in [401, 403]


def test_screen_single_customer(client, auth_headers):
    response = client.post(
        "/screen?customer_id=e506847c-ea3b-4630-b229-fd5c85f10535",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "weighted_score" in data
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_screen_missing_customer(client, auth_headers):
    response = client.post(
        "/screen?customer_id=00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
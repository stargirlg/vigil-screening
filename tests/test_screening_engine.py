def test_screen_customer(client, auth_headers):
    response = client.post(
        "/screen?customer_id=e506847c-ea3b-4630-b229-fd5c85f10535",
        headers=auth_headers
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200

    data = response.json()
    assert data["weighted_score"] >= 0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
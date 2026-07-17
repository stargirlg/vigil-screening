def test_list_alerts(client, auth_headers):
    response = client.get("/alerts", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_alert_not_found(client, auth_headers):
    response = client.get(
        "/alerts/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert response.status_code == 404
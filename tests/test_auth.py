def test_login_success(client):
    response = client.post("/auth/login", json={
        "email": "admin@vigil.com",
        "password": "Admin@123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    response = client.post("/auth/login", json={
        "email": "admin@vigil.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@vigil.com"
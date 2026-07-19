import io


def test_csv_upload_success(client, auth_headers):
    csv_content = """full_name,dob,pan,nationality,occupation,source
John Test,1990-01-01,TESTX1234Y,Indian,Engineer,TEST
Jane Test,1985-06-15,TESTY5678Z,Indian,Accountant,TEST"""

    csv_file = io.BytesIO(csv_content.encode())
    response = client.post(
        "/customers/upload-csv",
        files={"file": ("test.csv", csv_file, "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] >= 1


def test_csv_upload_invalid_file(client, auth_headers):
    response = client.post(
        "/customers/upload-csv",
        files={"file": ("test.txt", b"not a csv", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code in [400, 422]


def test_csv_upload_unauthenticated(client):
    csv_content = b"full_name,dob\nTest,1990-01-01"
    response = client.post(
        "/customers/upload-csv",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )
    assert response.status_code in [401, 403]
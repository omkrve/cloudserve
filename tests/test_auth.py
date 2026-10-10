
def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_user_can_login(client, user):
    response = client.post(
        "/login",
        data={
            "email": "user@example.com",
            "password": "TestPassword123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Demo User" in response.data


def test_invalid_password_is_rejected(client, user):
    response = client.post(
        "/login",
        data={
            "email": "user@example.com",
            "password": "wrong-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_registration_creates_account(client):
    response = client.post(
        "/register",
        data={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "NewStrongPassword123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"New User" in response.data


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_user_can_create_ticket(client, user):
    login(client, "user@example.com", "TestPassword123!")

    response = client.post(
        "/tickets",
        data={
            "title": "Laptop issue",
            "description": "Laptop does not start",
            "category": "Hardware",
            "priority": "High",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Laptop issue" in response.data


def test_user_cannot_update_ticket(client, app, user, admin):
    from app.models import db, Ticket

    with app.app_context():
        ticket = Ticket(
            title="Admin ticket",
            description="Test ticket",
            category="Hardware",
            priority="Medium",
            status="Open",
            user_id=admin,
        )
        db.session.add(ticket)
        db.session.commit()
        ticket_id = ticket.id

    login(client, "user@example.com", "TestPassword123!")

    response = client.post(
        f"/tickets/{ticket_id}/update",
        data={"status": "Resolved", "priority": "Low"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Administrator access is required." in response.data

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        assert ticket.status == "Open"
        assert ticket.priority == "Medium"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["database"] == "connected"


from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Ticket, db

main = Blueprint("main", __name__)

VALID_STATUSES = {"Open", "In Progress", "Resolved"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


@main.get("/")
@login_required
def dashboard():
    if current_user.role == "admin":
        tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    else:
        tickets = (
            Ticket.query.filter_by(user_id=current_user.id)
            .order_by(Ticket.id.desc()).all()
        )

    stats = {
        "total": len(tickets),
        "open": sum(t.status == "Open" for t in tickets),
        "progress": sum(t.status == "In Progress" for t in tickets),
        "resolved": sum(t.status == "Resolved" for t in tickets),
    }

    return render_template(
        "dashboard.html", tickets=tickets, stats=stats
    )


@main.post("/tickets")
@login_required
def create_ticket():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    priority = request.form.get("priority", "Medium")

    if not title or not description or not category:
        flash("Please complete all required fields.", "error")
    elif len(title) > 150 or len(description) > 5000:
        flash("The title or description is too long.", "error")
    elif category not in {"Hardware", "Software", "Network", "Other"}:
        flash("Please choose a valid category.", "error")
    elif priority not in VALID_PRIORITIES:
        flash("Please choose a valid priority.", "error")
    else:
        ticket = Ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            user_id=current_user.id,
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Service ticket created successfully.", "success")

    return redirect(url_for("main.dashboard"))


@main.post("/tickets/<int:ticket_id>/update")
@login_required
def update_ticket(ticket_id):
    if current_user.role != "admin":
        flash("Administrator access is required.", "error")
        return redirect(url_for("main.dashboard"))

    ticket = db.get_or_404(Ticket, ticket_id)
    status = request.form.get("status", "")
    priority = request.form.get("priority", "")

    if status not in VALID_STATUSES or priority not in VALID_PRIORITIES:
        flash("Invalid status or priority.", "error")
    else:
        ticket.status = status
        ticket.priority = priority
        db.session.commit()
        flash(f"Ticket #{ticket.id} updated.", "success")

    return redirect(url_for("main.dashboard"))


@main.get("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}, 200
    except Exception:
        db.session.rollback()
        return {"status": "unhealthy", "database": "unavailable"}, 503

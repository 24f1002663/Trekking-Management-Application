from celery import shared_task
from flask_mail import Message
from mail_service import mail
from datetime import date, timedelta


@shared_task(name="scheduler.send_daily_reminders")
def send_daily_reminders():
    """Email users whose booked trek starts within 3 days."""
    from model import booking

    target = date.today() + timedelta(days=3)
    bookings = booking.query.filter_by(status="Booked").all()

    for b in bookings:
        if b.trek.startdate <= target:
            try:
                msg = Message(
                    subject="Upcoming Trek Reminder",
                    recipients=[b.user.email]
                )
                msg.body = f"""
Hello {b.user.name},

Your trek "{b.trek.trekname}" starts on {b.trek.startdate}.

Please check your dashboard for details.

Thank you.
"""
                mail.send(msg)

            except Exception:
                pass


# Staff Reminder
@shared_task(name="scheduler.send_staff_reminders")
def send_staff_reminders():
    """Email staff assigned to treks starting in 2 days."""
    from model import trek, user

    target = date.today() + timedelta(days=2)
    treks = trek.query.filter_by(status="Open").all()

    for t in treks:
        if t.startdate != target:
            continue
        staff = user.query.get(t.assignedstaffid)
        if not staff:
            continue
        try:
            msg = Message(
                subject="Assigned Trek Reminder",
                recipients=[staff.email]
            )
            msg.body = f"""
Hello {staff.name},

Your assigned trek "{t.trekname}" starts in 2 days.

Please login and prepare.

Thank you.
"""
            mail.send(msg)

        except Exception:
            pass


# Monthly Admin Report
@shared_task(name="scheduler.send_monthly_report")
def send_monthly_report():
    """Email the admin a monthly summary report and post a completion notice."""
    from model import db, user, trek, booking, notification
    from sqlalchemy import func

    admin = user.query.filter_by(role="admin").first()

    if not admin:
        return

    total_users = user.query.filter_by(role="user").count()
    total_staff = user.query.filter_by(role="staff").count()
    total_treks = trek.query.count()
    total_bookings = booking.query.count()

    # Treks actually conducted (completed) and total participants enrolled.
    treks_conducted = trek.query.filter_by(status="Completed").count()
    total_participants = booking.query.filter(booking.status != "Cancelled").count()

    # Most-booked treks (top 3 by number of non-cancelled bookings).
    popular = (
        db.session.query(trek.trekname, func.count(booking.bookingid).label("cnt"))
        .join(booking, booking.trekid == trek.trekid)
        .filter(booking.status != "Cancelled")
        .group_by(trek.trekid)
        .order_by(func.count(booking.bookingid).desc())
        .limit(3)
        .all()
    )

    popular_rows = "".join(
        f"<li>{name} — {cnt} booking(s)</li>" for name, cnt in popular
    ) or "<li>No bookings yet</li>"

    try:
        msg = Message(
            subject="Monthly Trek Report",
            recipients=[admin.email]
        )

        msg.html = f"""
        <h2>Monthly Report</h2>

        <p>Total Users : {total_users}</p>
        <p>Total Staff : {total_staff}</p>
        <p>Total Treks : {total_treks}</p>
        <p>Treks Conducted (Completed) : {treks_conducted}</p>
        <p>Total Bookings : {total_bookings}</p>
        <p>Total Participants : {total_participants}</p>

        <h3>Most Booked Treks</h3>
        <ul>{popular_rows}</ul>
        """

        mail.send(msg)

    except Exception:
        pass

    # Completion notification for the async batch job (in-app, for the admin).
    try:
        note = notification(
            userid=admin.userid,
            title="Monthly Report Generated",
            message=(
                f"Monthly report ready: {total_users} users, {total_staff} staff, "
                f"{total_treks} treks, {treks_conducted} completed, "
                f"{total_bookings} bookings."
            ),
        )
        db.session.add(note)
        db.session.commit()
    except Exception:
        db.session.rollback()
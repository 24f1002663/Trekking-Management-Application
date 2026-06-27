from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, user, trek, booking, trekimage
from routes.auth_helper import user_required
from datetime import datetime
from mail_service import mail
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io

user_bp = Blueprint("user", __name__)


def get_user_id():
    return int(get_jwt_identity())
# User Dashboard Stats
@user_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@user_required
def dashboard():
    userid = get_user_id()
    current_user = user.query.get(userid)
    active = booking.query.filter_by(userid=userid, status="Booked").count()
    completed = booking.query.filter_by(userid=userid, status="Completed").count()
    cancelled = booking.query.filter_by(userid=userid, status="Cancelled").count()
    recent = booking.query.filter_by(userid=userid).order_by(booking.bookingdate.desc()).limit(3).all()
    recent_list = [{
        "trekname": b.trek.trekname,
        "location": b.trek.location,
        "bookingdate": str(b.bookingdate.date()),
        "status": b.status,
        "trekstatus": b.trek.status
    } for b in recent]
    return jsonify({
        "success": True,
        "name": current_user.name,
        "active_bookings": active,
        "completed_treks": completed,
        "cancelled_bookings": cancelled,
        "recent": recent_list
    }), 200

#available treks
@user_bp.route("/treks", methods=["GET"])
@jwt_required()
@user_required
def available_treks():
    search = request.args.get("search", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")
    duration = request.args.get("duration", "")
    query = trek.query.filter_by(status="Open")
    if search:
        query = query.filter(trek.trekname.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(trek.location.ilike(f"%{location}%"))
    if duration:
        try:
            query = query.filter_by(durationdays=int(duration))
        except (ValueError, TypeError):
            pass
    treks = query.all()
    trek_list = []
    for t in treks:
        images = trekimage.query.filter_by(trekid=t.trekid).all()
        trek_list.append({
            "trekid": t.trekid,
            "trekname": t.trekname,
            "location": t.location,
            "difficulty": t.difficulty,
            "durationdays": t.durationdays,
            "price": t.price,
            "seats": t.seats,
            "bookedseats": t.bookedseats,
            "available_seats": t.seats - t.bookedseats,
            "startdate": str(t.startdate),
            "enddate": str(t.enddate),
            "description": t.description or "",
            "instructions": t.instructions or "",
            "allowedgender": t.allowedgender,
            "status": t.status,
            "images": [i.imageurl for i in images]
        })

    return jsonify({
        "success": True,
        "treks": trek_list
    }), 200
# Book a Trek
@user_bp.route("/book/<int:trekid>", methods=["POST"])
@jwt_required()
@user_required
def book_trek(trekid):

    userid = get_user_id()
    current_user = user.query.get(userid)

    current_trek = trek.query.get(trekid)

    if not current_trek:
        return jsonify({"success": False, "message": "Trek not found"}), 404
    if current_trek.status != "Open":
        return jsonify({
            "success": False,
            "message": "This trek is not open for booking"
        }), 400
    if current_trek.bookedseats >= current_trek.seats:
        return jsonify({
            "success": False,
            "message": "No seats available for this trek"
        }), 400
    if current_trek.allowedgender != "Coed":
        if current_user.gender != current_trek.allowedgender:
            return jsonify({
                "success": False,
                "message": f"This trek is only for {current_trek.allowedgender} trekkers"
            }), 400

    existing_booking = booking.query.filter_by(
        userid=userid,
        trekid=trekid,
        status="Booked"
    ).first()

    if existing_booking:
        return jsonify({
            "success": False,
            "message": "You have already booked this trek"
        }), 400

    new_booking = booking(
        userid=userid,
        trekid=trekid,
        status="Booked",
        paymentstatus="Pending"
    )

    db.session.add(new_booking)
    current_trek.bookedseats += 1
    db.session.commit()

    try:
        msg = Message(
            subject=f"Booking Confirmed: {current_trek.trekname}",
            recipients=[current_user.email]
        )
        msg.body = f"""Hello {current_user.name},

Your booking is confirmed!

Trek: {current_trek.trekname}
Location: {current_trek.location}
Start Date: {current_trek.startdate}
End Date: {current_trek.enddate}
Duration: {current_trek.durationdays} days
Difficulty: {current_trek.difficulty}
Price: Rs. {current_trek.price}
Booking ID: {new_booking.bookingid}

Instructions: {current_trek.instructions or 'None'}

Have a great trek!
Trek Management Team"""
        mail.send(msg)
    except Exception as e:
        print(f"[Email] Booking confirmation failed: {e}")

    return jsonify({
        "success": True,
        "message": "Trek booked successfully!",
        "bookingid": new_booking.bookingid
    }), 201
# Cancel a Booking
@user_bp.route("/bookings/<int:bookingid>/cancel", methods=["PUT"])
@jwt_required()
@user_required
def cancel_booking(bookingid):

    userid = get_user_id()

    b = booking.query.filter_by(bookingid=bookingid, userid=userid).first()

    if not b:
        return jsonify({"success": False, "message": "Booking not found"}), 404

    if b.status != "Booked":
        return jsonify({
            "success": False,
            "message": "Only active bookings can be cancelled"
        }), 400

    b.status = "Cancelled"

    current_trek = trek.query.get(b.trekid)

    if current_trek and current_trek.bookedseats > 0:
        current_trek.bookedseats -= 1

    # Create notifications for both user and admin
    from model import notification
    current_user = user.query.get(userid)
    
    user_note = notification(
        userid=userid,
        title="Booking Cancelled",
        message=f"You cancelled your booking (ID: {b.bookingid}) for trek '{current_trek.trekname}'."
    )
    db.session.add(user_note)

    admin_user = user.query.filter_by(role="admin").first()
    if admin_user:
        admin_note = notification(
            userid=admin_user.userid,
            title="Booking Cancelled by User",
            message=f"Booking (ID: {b.bookingid}) for user '{current_user.name}' on trek '{current_trek.trekname}' was cancelled by User."
        )
        db.session.add(admin_note)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Booking cancelled successfully"
    }), 200
# View My Bookings
@user_bp.route("/bookings", methods=["GET"])
@jwt_required()
@user_required
def my_bookings():

    userid = get_user_id()

    bookings = booking.query.filter_by(userid=userid).order_by(
        booking.bookingdate.desc()
    ).all()

    booking_list = []

    for b in bookings:
        booking_list.append({
            "bookingid": b.bookingid,
            "trekid": b.trekid,
            "trekname": b.trek.trekname,
            "location": b.trek.location,
            "startdate": str(b.trek.startdate),
            "enddate": str(b.trek.enddate),
            "bookingdate": str(b.bookingdate.date()),
            "status": b.status,
            "paymentstatus": b.paymentstatus,
            "trekstatus": b.trek.status
        })

    return jsonify({
        "success": True,
        "bookings": booking_list
    }), 200

# Get Profile

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@user_required
def get_profile():

    userid = get_user_id()
    current_user = user.query.get(userid)

    return jsonify({
        "success": True,
        "profile": {
            "userid": current_user.userid,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "gender": current_user.gender,
            "status": current_user.status
        }
    }), 200
# Edit Profile
@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
@user_required
def edit_profile():

    userid = get_user_id()
    current_user = user.query.get(userid)

    data = request.get_json()

    if data.get("name"):
        current_user.name = data["name"]

    if data.get("phone"):
        current_user.phone = data["phone"]

    if data.get("gender") in ["Male", "Female", "Other"]:
        current_user.gender = data["gender"]

    if data.get("password"):
        current_user.password = generate_password_hash(data["password"])

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully"
    }), 200


@user_bp.route("/export", methods=["GET"])
@jwt_required()
@user_required
def export_bookings():

    userid = get_user_id()
    bookings = booking.query.filter_by(userid=userid).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Trek",
        "Location",
        "Booking Date",
        "Status"
    ])

    for b in bookings:
        writer.writerow([
            b.trek.trekname,
            b.trek.location,
            b.bookingdate.date(),
            b.status
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=bookings.csv"
        }
    )

# User Notifications
@user_bp.route("/notifications", methods=["GET"])
@jwt_required()
@user_required
def get_notifications():
    from model import notification
    userid = get_user_id()
    notes = notification.query.filter_by(userid=userid).order_by(notification.created_at.desc()).all()
    return jsonify({"success": True, "notifications": [{
        "notificationid": n.notificationid,
        "title": n.title,
        "message": n.message,
        "isread": n.isread,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
    } for n in notes]}), 200

@user_bp.route("/notifications/<int:nid>/read", methods=["PUT"])
@jwt_required()
@user_required
def mark_notification_read(nid):
    from model import notification
    userid = get_user_id()
    n = notification.query.filter_by(notificationid=nid, userid=userid).first()
    if not n:
        return jsonify({"success": False, "message": "Notification not found"}), 404
    n.isread = True
    db.session.commit()
    return jsonify({"success": True}), 200
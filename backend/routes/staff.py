from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from model import db, user, trek, booking
from routes.auth_helper import staff_required

staff_bp = Blueprint("staff", __name__)

def get_staff_id():
    return int(get_jwt_identity())

#Staffdashboard

@staff_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@staff_required
def staff_dashboard():

    staffid = get_staff_id()

    assigned_treks = trek.query.filter_by(assignedstaffid=staffid).all()

    trek_data = []

    for t in assigned_treks:

        participant_count = booking.query.filter_by(
            trekid=t.trekid, status="Booked"
        ).count()

        trek_data.append({
            "trekid": t.trekid,
            "trekname": t.trekname,
            "location": t.location,
            "status": t.status,
            "startdate": str(t.startdate),
            "enddate": str(t.enddate),
            "seats": t.seats,
            "bookedseats": t.bookedseats,
            "participants": participant_count
        })

    return jsonify({
        "success": True,
        "treks": trek_data
    }), 200


@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
@staff_required
def view_assigned_treks():

    staffid = get_staff_id()

    assigned_treks = trek.query.filter_by(assignedstaffid=staffid).all()

    trek_list = []

    for t in assigned_treks:

        trek_list.append({
            "trekid": t.trekid,
            "trekname": t.trekname,
            "location": t.location,
            "difficulty": t.difficulty,
            "durationdays": t.durationdays,
            "price": t.price,
            "seats": t.seats,
            "bookedseats": t.bookedseats,
            "status": t.status,
            "startdate": str(t.startdate),
            "enddate": str(t.enddate)
        })

    return jsonify({
        "success": True,
        "treks": trek_list
    }), 200

# Update Trek Status
@staff_bp.route("/treks/<int:trekid>/status", methods=["PUT"])
@jwt_required()
@staff_required
def update_trek_status(trekid):

    staffid = get_staff_id()

    current_trek = trek.query.filter_by(
        trekid=trekid,
        assignedstaffid=staffid
    ).first()

    if not current_trek:
        return jsonify({
            "success": False,
            "message": "Trek not found or not assigned to you"
        }), 404

    data = request.get_json()
    new_status = data.get("status")

    allowed_statuses = ["Open", "Closed", "Started", "Completed"]

    if new_status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Allowed: {allowed_statuses}"
        }), 400

    if new_status == "Completed":
        bookings = booking.query.filter_by(trekid=trekid, status="Booked").all()
        for b in bookings:
            b.status = "Completed"

    current_trek.status = new_status
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Trek status updated to {new_status}"
    }), 200

# Update Trek Slots
@staff_bp.route("/treks/<int:trekid>/slots", methods=["PUT"])
@jwt_required()
@staff_required
def update_trek_slots(trekid):

    staffid = get_staff_id()

    current_trek = trek.query.filter_by(
        trekid=trekid,
        assignedstaffid=staffid
    ).first()

    if not current_trek:
        return jsonify({
            "success": False,
            "message": "Trek not found or not assigned to you"
        }), 404

    data = request.get_json()
    new_seats = data.get("seats")

    if new_seats is None or int(new_seats) < current_trek.bookedseats:
        return jsonify({
            "success": False,
            "message": "Seats cannot be less than already booked seats"
        }), 400

    current_trek.seats = int(new_seats)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Seats updated successfully"
    }), 200


# view participants
@staff_bp.route("/treks/<int:trekid>/participants", methods=["GET"])
@jwt_required()
@staff_required
def view_participants(trekid):

    staffid = get_staff_id()

    current_trek = trek.query.filter_by(
        trekid=trekid,
        assignedstaffid=staffid
    ).first()

    if not current_trek:
        return jsonify({
            "success": False,
            "message": "Trek not found or not assigned to you"
        }), 404

    bookings = booking.query.filter_by(trekid=trekid).all()

    participants = []

    for b in bookings:
        participants.append({
            "bookingid": b.bookingid,
            "userid": b.userid,
            "name": b.user.name,
            "email": b.user.email,
            "phone": b.user.phone,
            "gender": b.user.gender,
            "bookingdate": str(b.bookingdate.date()),
            "status": b.status,
            "paymentstatus": b.paymentstatus
        })

    return jsonify({
        "success": True,
        "trekname": current_trek.trekname,
        "participants": participants
    }), 200

# Reject Trek Assignment
@staff_bp.route("/treks/<int:trekid>/reject", methods=["POST"])
@jwt_required()
@staff_required
def reject_trek(trekid):

    staffid = get_staff_id()

    current_trek = trek.query.filter_by(
        trekid=trekid,
        assignedstaffid=staffid
    ).first()

    if not current_trek:
        return jsonify({"success": False, "message": "Trek not found or not assigned to you"}), 404

    data = request.get_json()
    reason = data.get("reason", "").strip()

    if not reason:
        return jsonify({"success": False, "message": "Please provide a rejection reason"}), 400

    staff_member = user.query.get(staffid)

    from model import notification
    admin = user.query.filter_by(role="admin").first()

    if admin:
        note = notification(
            userid=admin.userid,
            title="Trek Assignment Rejected",
            message=f"Staff '{staff_member.name}' has rejected the assignment for trek '{current_trek.trekname}'.\n\nReason: {reason}\n\nPlease log in and assign another staff member."
        )
        db.session.add(note)
        db.session.commit()

    return jsonify({"success": True, "message": "Rejection submitted. Admin has been notified."}), 200
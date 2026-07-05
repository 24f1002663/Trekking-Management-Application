from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from model import db, user, trek, booking, trekimage, payment
from routes.auth_helper import admin_required
from extensions import cache
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from mail_service import mail
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import os
admin_bp = Blueprint("admin", __name__)
#dashboard
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@admin_required
def dashboard():
    total_users = user.query.filter_by(role="user").count()
    total_staff = user.query.filter_by(role="staff").count()
    total_treks = trek.query.count()
    total_bookings = booking.query.count()
    return jsonify({
        "success": True,
        "dashboard": {
            "total_users": total_users,
            "total_staff": total_staff,
            "total_treks": total_treks,
            "total_bookings": total_bookings
        }
    }), 200
#addstaff
@admin_bp.route("/staff", methods=["POST"])
@jwt_required()
@admin_required
def add_staff():
    data = request.get_json()
    if user.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400
    staff = user(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        phone=data["phone"],
        gender=data["gender"],
        role="staff",
        status="active"
    )

    db.session.add(staff)
    db.session.commit()

    try:
        msg = Message(
            "Staff Account",
            recipients=[staff.email]
        )

        msg.body = f"""
Email : {staff.email}

Password : {data["password"]}
"""

        mail.send(msg)

    except:
        pass

    return jsonify({"success": True, "message": "Staff added"})
#toviewalthestaffs
@admin_bp.route("/staff", methods=["GET"])
@jwt_required()
@admin_required
def view_staff():
    staff_members = user.query.filter_by(role="staff").all()
    staff_list = [{
        "userid": s.userid,
        "name": s.name,
        "email": s.email,
        "phone": s.phone,
        "gender": s.gender,
        "status": s.status
    } for s in staff_members]
    return jsonify({"success": True, "staff": staff_list}), 200
#updatestaff
@admin_bp.route("/staff/<int:staffid>", methods=["PUT"])
@jwt_required()
@admin_required
def update_staff(staffid):
    staff = user.query.filter_by(userid=staffid, role="staff").first()
    if not staff:
        return jsonify({"success": False, "message": "Staff not found"}), 404
    data = request.get_json()
    staff.name = data.get("name", staff.name)
    staff.email = data.get("email", staff.email)
    staff.phone = data.get("phone", staff.phone)
    staff.gender = data.get("gender", staff.gender)
    if data.get("password"):
        staff.password = generate_password_hash(data.get("password"))
    db.session.commit()
    return jsonify({"success": True, "message": "Staff updated"}), 200
#deletestaff
@admin_bp.route("/staff/<int:staffid>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_staff(staffid):
    staff = user.query.filter_by(userid=staffid, role="staff").first()
    if not staff:
        return jsonify({"success": False, "message": "Staff not found"}), 404
    assigned_treks = trek.query.filter_by(assignedstaffid=staffid).count()
    if assigned_treks > 0:
        return jsonify({"success": False, "message": f"Cannot delete: staff is assigned to {assigned_treks} trek(s)"}), 400
    try:
        db.session.delete(staff)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Cannot delete staff because related records still exist"}), 400
    return jsonify({"success": True, "message": "Staff deleted"}), 200
#blackliststaff
@admin_bp.route("/staff/<int:staffid>/blacklist", methods=["PUT"])
@jwt_required()
@admin_required
def blacklist_staff(staffid):
    staff = user.query.filter_by(userid=staffid, role="staff").first()
    if not staff:
        return jsonify({"success": False, "message": "Staff not found"}), 404
    staff.status = "blacklisted"
    db.session.commit()
    return jsonify({"success": True, "message": "Staff blacklisted"}), 200
#activatestaff
@admin_bp.route("/staff/<int:staffid>/unblacklist", methods=["PUT"])
@jwt_required()
@admin_required
def unblacklist_staff(staffid):
    staff = user.query.filter_by(userid=staffid, role="staff").first()
    if not staff:
        return jsonify({"success": False, "message": "Staff not found"}), 404
    staff.status = "active"
    db.session.commit()
    return jsonify({"success": True, "message": "Staff activated"}), 200
#viewusers
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def view_users():
    users = user.query.filter_by(role="user").all()
    user_list = [{
        "userid": u.userid,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "gender": u.gender,
        "status": u.status
    } for u in users]
    return jsonify({"success": True, "users": user_list}), 200
#blacklist/activateusers
@admin_bp.route("/users/<int:userid>/blacklist", methods=["PUT"])
@jwt_required()
@admin_required
def blacklist_user(userid):
    u = user.query.filter_by(userid=userid, role="user").first()
    if not u:
        return jsonify({"success": False, "message": "User not found"}), 404
    u.status = "blacklisted"
    db.session.commit()
    return jsonify({"success": True, "message": "User blacklisted"}), 200
@admin_bp.route("/users/<int:userid>/unblacklist", methods=["PUT"])
@jwt_required()
@admin_required
def unblacklist_user(userid):
    u = user.query.filter_by(userid=userid, role="user").first()
    if not u:
        return jsonify({"success": False, "message": "User not found"}), 404
    u.status = "active"
    db.session.commit()
    return jsonify({"success": True, "message": "User activated"}), 200
# Create Trek
@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
@admin_required
def create_trek():
    data = request.get_json()
    from flask_jwt_extended import get_jwt_identity
    admin_id = int(get_jwt_identity())
    start_date = datetime.strptime(data.get("startdate"), "%Y-%m-%d").date()
    end_date = datetime.strptime(data.get("enddate"), "%Y-%m-%d").date()
    if end_date < start_date:
        return jsonify({"success": False, "message": "End date cannot be before start date"}), 400
    new_trek = trek(
        trekname=data.get("trekname"),
        location=data.get("location"),
        difficulty=data.get("difficulty"),
        durationdays=data.get("durationdays"),
        price=data.get("price"),
        seats=data.get("seats"),
        assignedstaffid=admin_id,
        startdate=start_date,
        enddate=end_date,
        description=data.get("description"),
        instructions=data.get("instructions"),
        allowedgender=data.get("allowedgender") or "Coed",
        status="Open"
    )
    db.session.add(new_trek)
    db.session.commit()
    cache.clear()  # trek listing changed
    return jsonify({"success": True, "message": "Trek created. Use 'Assign Staff' to assign a staff member."}), 201
#viewalltreks
@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
@admin_required
def view_treks():
    treks = trek.query.all()
    trek_list = [{
        "trekid": t.trekid,
        "trekname": t.trekname,
        "location": t.location,
        "difficulty": t.difficulty,
        "durationdays": t.durationdays,
        "price": t.price,
        "seats": t.seats,
        "bookedseats": t.bookedseats,
        "assignedstaffid": t.assignedstaffid,
        "allowedgender": t.allowedgender,
        "startdate": str(t.startdate),
        "enddate": str(t.enddate),
        "description": t.description or "",
        "instructions": t.instructions or "",
        "status": t.status
    } for t in treks]
    return jsonify({"success": True, "treks": trek_list}), 200
# Update Trek
@admin_bp.route("/treks/<int:trekid>", methods=["PUT"])
@jwt_required()
@admin_required
def update_trek(trekid):
    t = trek.query.get(trekid)
    if not t:
        return jsonify({"success": False, "message": "Trek not found"}), 404
    data = request.get_json()
    t.trekname = data.get("trekname") or t.trekname
    t.location = data.get("location") or t.location
    t.difficulty = data.get("difficulty") or t.difficulty
    t.durationdays = data.get("durationdays") or t.durationdays
    t.price = data.get("price") or t.price
    new_seats = data.get("seats")
    if new_seats is not None and int(new_seats) < t.bookedseats:
        return jsonify({"success": False, "message": "Seats cannot be less than already booked seats"}), 400
    t.seats = int(new_seats) if new_seats is not None else t.seats
    t.description = data.get("description", t.description)
    t.instructions = data.get("instructions", t.instructions)
    if data.get("allowedgender") in ["Male", "Female", "Coed"]:
        t.allowedgender = data.get("allowedgender")
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Update failed: " + str(e)}), 500
    cache.clear()  # trek listing changed
    return jsonify({"success": True, "message": "Trek updated"}), 200
# Delete Trek
@admin_bp.route("/treks/<int:trekid>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_trek(trekid):
    t = trek.query.get(trekid)
    if not t:
        return jsonify({"success": False, "message": "Trek not found"}), 404
    related_bookings = booking.query.filter_by(trekid=trekid).count()
    if related_bookings > 0:
        return jsonify({"success": False, "message": f"Cannot delete: {related_bookings} booking(s) exist"}), 400
    try:
        trekimage.query.filter_by(trekid=trekid).delete(synchronize_session=False)
        db.session.delete(t)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Cannot delete trek because related records still exist"}), 400
    cache.clear()  # trek listing changed
    return jsonify({"success": True, "message": "Trek deleted"}), 200
# Update Trek Status
@admin_bp.route("/treks/<int:trekid>/status", methods=["PUT"])
@jwt_required()
@admin_required
def update_trek_status(trekid):
    t = trek.query.get(trekid)
    if not t:
        return jsonify({"success": False, "message": "Trek not found"}), 404
    data = request.get_json()
    new_status = data.get("status")
    valid = ["Pending", "Approved", "Open", "Closed", "Started", "Completed"]
    if new_status not in valid:
        return jsonify({"success": False, "message": "Invalid status"}), 400
    if new_status == "Completed":
        booking.query.filter_by(trekid=trekid, status="Booked").update(
            {booking.status: "Completed"},
            synchronize_session=False,
        )
    t.status = new_status
    db.session.commit()
    cache.clear()  # trek visibility/status changed
    return jsonify({"success": True, "message": f"Status updated to {new_status}"}), 200
# Assign Staff to Trek
@admin_bp.route("/treks/<int:trekid>/assign", methods=["PUT"])
@jwt_required()
@admin_required
def assign_staff(trekid):
    t = trek.query.get(trekid)
    if not t:
        return jsonify({"success": False, "message": "Trek not found"}), 404
    data = request.get_json()
    staff_member = user.query.filter_by(userid=data.get("staffid"), role="staff").first()
    if not staff_member:
        return jsonify({"success": False, "message": "Staff not found"}), 404
    overlapping = trek.query.filter(
        trek.assignedstaffid == staff_member.userid,
        trek.trekid != trekid,
        trek.startdate <= t.enddate,
        trek.enddate >= t.startdate
    ).first()
    if overlapping:
        return jsonify({
            "success": False,
            "message": f"Staff is not available for the selected dates. Already assigned to '{overlapping.trekname}' ({overlapping.startdate} – {overlapping.enddate})."
        }), 400

    t.assignedstaffid = staff_member.userid
    db.session.commit()

    try:
        msg = Message(
            subject=f"Trek Assignment: {t.trekname}",
            recipients=[staff_member.email]
        )
        msg.body = f"""Hello {staff_member.name},

You have been assigned to lead a trek!

Trek: {t.trekname}
Location: {t.location}
Start Date: {t.startdate}
End Date: {t.enddate}
Duration: {t.durationdays} days
Difficulty: {t.difficulty}
Total Seats: {t.seats}

Please log in to your dashboard to manage this trek.

Best regards,
Trek Management Admin"""
        mail.send(msg)
    except Exception as e:
        print(f"[Email] Assignment email failed: {e}")

    return jsonify({"success": True, "message": "Staff assigned successfully"}), 200
# Trek Images
@admin_bp.route("/treks/<int:trekid>/images", methods=["GET"])
@jwt_required()
@admin_required
def get_trek_images(trekid):
    images = trekimage.query.filter_by(trekid=trekid).all()
    return jsonify({
        "success": True,
        "images": [{"imageid": i.imageid, "imageurl": i.imageurl} for i in images]
    }), 200
# Trek Images(upload)
@admin_bp.route("/treks/<int:trekid>/images", methods=["POST"])
@jwt_required()
@admin_required
def upload_trek_image(trekid):
    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image file provided"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filename = f"trek_{trekid}_{filename}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file.save(os.path.join(upload_folder, filename))

    imageurl = "/static/uploads/" + filename
    new_image = trekimage(trekid=trekid, imageurl=imageurl)
    db.session.add(new_image)
    db.session.commit()
    cache.clear()  # trek images shown in listing changed

    return jsonify({
        "success": True,
        "image": {"imageid": new_image.imageid, "imageurl": imageurl}
    }), 201
# Trek Images(todelete)
@admin_bp.route("/treks/<int:trekid>/images/<int:imageid>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_trek_image(trekid, imageid):
    image = trekimage.query.filter_by(imageid=imageid, trekid=trekid).first()
    if not image:
        return jsonify({"success": False, "message": "Image not found"}), 404
    # Remove from disk
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.basename(image.imageurl))
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(image)
    db.session.commit()
    cache.clear()  # trek images shown in listing changed
    return jsonify({"success": True, "message": "Image deleted"}), 200
# Search Users
@admin_bp.route("/users/search/<string:keyword>", methods=["GET"])
@jwt_required()
@admin_required
def search_users(keyword):
    users = user.query.filter(user.role == "user", user.name.ilike(f"%{keyword}%")).all()
    return jsonify({"success": True, "users": [{
        "userid": u.userid, "name": u.name, "email": u.email,
        "phone": u.phone, "gender": u.gender, "status": u.status
    } for u in users]}), 200
# Search Staff
@admin_bp.route("/staff/search/<string:keyword>", methods=["GET"])
@jwt_required()
@admin_required
def search_staff(keyword):
    staff = user.query.filter(user.role == "staff", user.name.ilike(f"%{keyword}%")).all()
    return jsonify({"success": True, "staff": [{
        "userid": s.userid, "name": s.name, "email": s.email, "status": s.status
    } for s in staff]}), 200
# All Bookings
@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
@admin_required
def booking_history():
    bookings = booking.query.all()
    return jsonify({"success": True, "bookings": [{
        "bookingid": b.bookingid,
        "user": b.user.name,
        "trek": b.trek.trekname,
        "bookingdate": b.bookingdate.strftime("%Y-%m-%d"),
        "status": b.status,
        "paymentstatus": b.paymentstatus
    } for b in bookings]}), 200
#reports
@admin_bp.route("/reports", methods=["GET"])
@jwt_required()
@admin_required
def reports():
    return jsonify({"success": True, "report": {
        "total_users": user.query.filter_by(role="user").count(),
        "total_staff": user.query.filter_by(role="staff").count(),
        "total_treks": trek.query.count(),
        "total_bookings": booking.query.count(),
        "completed_bookings": booking.query.filter_by(status="Completed").count(),
        "cancelled_bookings": booking.query.filter_by(status="Cancelled").count(),
        "pending_payments": booking.query.filter(booking.paymentstatus == "Pending", booking.status != "Cancelled").count(),
        "completed_payments": booking.query.filter(booking.paymentstatus == "Completed", booking.status != "Cancelled").count(),
        # alias consumed by the reports UI ("Successful Payments" card)
        "successful_payments": booking.query.filter(booking.paymentstatus == "Completed", booking.status != "Cancelled").count()
    }}), 200
#Notifications
@admin_bp.route("/notifications", methods=["GET"])
@jwt_required()
@admin_required
def get_notifications():
    from model import notification
    from flask_jwt_extended import get_jwt_identity
    admin_id = int(get_jwt_identity())
    notes = notification.query.filter_by(userid=admin_id).order_by(notification.created_at.desc()).all()
    return jsonify({"success": True, "notifications": [{
        "notificationid": n.notificationid,
        "title": n.title,
        "message": n.message,
        "isread": n.isread,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
    } for n in notes]}), 200

@admin_bp.route("/notifications/<int:nid>/read", methods=["PUT"])
@jwt_required()
@admin_required
def mark_notification_read(nid):
    from model import notification
    n = notification.query.get(nid)
    if not n:
        return jsonify({"success": False, "message": "Not found"}), 404
    n.isread = True
    db.session.commit()
    return jsonify({"success": True}), 200

# Cancel a Booking (by Admin)
@admin_bp.route("/bookings/<int:bookingid>/cancel", methods=["PUT"])
@jwt_required()
@admin_required
def admin_cancel_booking(bookingid):
    from flask_jwt_extended import get_jwt_identity
    admin_id = int(get_jwt_identity())
    
    b = booking.query.get(bookingid)
    if not b:
        return jsonify({"success": False, "message": "Booking not found"}), 404
        
    if b.status != "Booked":
        return jsonify({"success": False, "message": "Only active bookings can be cancelled"}), 400
        
    data = request.get_json() or {}
    reason = data.get("reason", "").strip()
    if not reason:
        return jsonify({"success": False, "message": "Cancellation reason is required"}), 400
        
    b.status = "Cancelled"
    
    current_trek = trek.query.get(b.trekid)
    if current_trek and current_trek.bookedseats > 0:
        current_trek.bookedseats -= 1
        
    # Notify User
    from model import notification
    user_note = notification(
        userid=b.userid,
        title="Booking Cancelled by Admin",
        message=f"Your booking (ID: {b.bookingid}) for trek '{b.trek.trekname}' was cancelled by Administrator. Reason: {reason}"
    )
    db.session.add(user_note)
    
    # Notify Admin
    admin_note = notification(
        userid=admin_id,
        title="Booking Cancelled",
        message=f"You cancelled booking ID {b.bookingid} for user '{b.user.name}' on trek '{b.trek.trekname}'. Reason: {reason}"
    )
    db.session.add(admin_note)

    db.session.commit()
    cache.clear()  # seat freed -> refresh cached trek listing
    return jsonify({"success": True, "message": "Booking cancelled successfully"}), 200

# Update Payment Status (by Admin)
@admin_bp.route("/bookings/<int:bookingid>/payment", methods=["PUT"])
@jwt_required()
@admin_required
def admin_update_payment(bookingid):
    b = booking.query.get(bookingid)
    if not b:
        return jsonify({"success": False, "message": "Booking not found"}), 404
        
    if b.status == "Cancelled":
        return jsonify({"success": False, "message": "Cannot update payment status of a cancelled booking"}), 400
        
    data = request.get_json() or {}
    paymentstatus = data.get("paymentstatus")
    if paymentstatus not in ["Pending", "Completed"]:
        return jsonify({"success": False, "message": "Invalid payment status"}), 400
        
    b.paymentstatus = paymentstatus
    db.session.commit()
    return jsonify({"success": True, "message": "Payment status updated successfully"}), 200
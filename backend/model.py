from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class user(db.Model):
    __tablename__ = "users"
    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    role = db.Column(db.Enum("admin", "staff", "user", name="role_enum"),nullable=False)
    status = db.Column(db.Enum("active", "blacklisted", name="user_status_enum"),nullable=False,default="active")
    gender = db.Column(db.Enum("Male","Female","Other",name="gender_enum"),nullable=False)


class trek(db.Model):
    __tablename__ = "treks"
    trekid = db.Column(db.Integer, primary_key=True)
    trekname = db.Column(db.String(100),nullable=False)
    location = db.Column(db.String(100),nullable=False)
    difficulty = db.Column(db.Enum("Easy","Medium","Hard",name="difficulty_enum"),nullable=False)
    durationdays = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Float,nullable=False)
    seats = db.Column(db.Integer,nullable=False)
    bookedseats = db.Column(db.Integer,nullable=False,default=0)
    assignedstaffid = db.Column(db.Integer,db.ForeignKey("users.userid"),nullable=False)
    startdate = db.Column(db.Date,nullable=False)
    enddate = db.Column(db.Date,nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    status = db.Column(db.Enum("Pending","Approved","Open","Closed","Started","Completed",name="trek_status_enum"),nullable=False,default="Pending")
    assignedstaff = db.relationship("user",backref=db.backref("assignedtreks",lazy=True))
    allowedgender = db.Column(
    db.Enum("Male","Female","Coed",name="allowed_gender_enum"),nullable=False,default="Coed")

class trekimage(db.Model):
    __tablename__ = "trekimages"
    imageid = db.Column(db.Integer,primary_key=True)
    trekid = db.Column(db.Integer,db.ForeignKey("treks.trekid"),nullable=False)
    imageurl = db.Column(db.String(255),nullable=False)

class booking(db.Model):
    __tablename__ = "bookings"
    bookingid = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey("users.userid"),nullable=False)
    trekid = db.Column(db.Integer,db.ForeignKey("treks.trekid"),nullable=False)
    bookingdate = db.Column(db.DateTime,default=datetime.utcnow)
    status = db.Column(db.Enum("Booked","Cancelled","Completed",name="booking_status_enum"),nullable=False,default="Booked")
    paymentstatus = db.Column(db.Enum("Pending","Completed",name="payment_status_enum"),nullable=False,default="Pending")
    user = db.relationship("user",backref=db.backref("bookings",lazy=True))
    trek = db.relationship("trek",backref=db.backref("bookings",lazy=True))


class payment(db.Model):
    __tablename__ = "payments"
    paymentid = db.Column(db.Integer,primary_key=True)
    bookingid = db.Column(db.Integer,db.ForeignKey("bookings.bookingid"),nullable=False,unique=True)
    amount = db.Column(db.Float,nullable=False)
    paymentdate = db.Column(db.DateTime,default=datetime.utcnow)
    transactionid = db.Column(db.String(100),unique=True)
    status = db.Column(db.Enum("Success","Failed","Pending",name="transaction_status_enum"),nullable=False,default="Success")
    booking = db.relationship("booking",backref=db.backref("payment",uselist=False))


class notification(db.Model):
    __tablename__ = "notifications"
    notificationid = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey("users.userid"),nullable=False)
    title = db.Column(db.String(200),nullable=False)
    message = db.Column(db.Text,nullable=False)
    isread = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    user = db.relationship("user",backref=db.backref("notifications",lazy=True))
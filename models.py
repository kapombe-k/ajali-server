from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)



class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    serialize_rules = ("-reports", "-emergency_contacts", "-password")

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.VARCHAR, nullable=True)
    phone_number = db.Column(db.String, unique=True, nullable=False)

    created_at = db.Column(db.TIMESTAMP)
    
    role = db.Column(db.String, default="user") 
    @property
    def is_admin(self):
        return self.role == "admin"

    reports = db.relationship("Report", back_populates="user", cascade="all, delete")

    emergency_contacts = db.relationship( "EmergencyContact", back_populates="user", cascade="all, delete" )
    # status_updates = db.relationship('StatusUpdates', back_populates='admin', cascade='all, delete')


class Report(db.Model, SerializerMixin):
    __tablename__ = "reports"
    serialize_rules = ("-user", "-status_updates", "-media_attachments", "-location")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    incident = db.Column(db.String, nullable=False)
    details = db.Column(db.Text, nullable=False)



    latitude = db.Column(db.Float, nullable=False, server_default="0")
    longitude = db.Column(db.Float, nullable=False, server_default="0")
   


    created_at = db.Column(db.TIMESTAMP)

    user = db.relationship("User", back_populates="reports")

    location = db.relationship( "Location", back_populates="report", uselist=False, cascade="all, delete" )
    media_attachments = db.relationship(  "MediaAttachment", back_populates="report", cascade="all, delete" )
  
    status_updates = db.relationship('StatusUpdate', back_populates='report', cascade='all, delete')


class EmergencyContact(db.Model, SerializerMixin):
    __tablename__ = "emergency_contacts"
    serialize_rules = ("-user.reports", "-user.emergency_contacts")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    relationship = db.Column(db.String, nullable=False) 
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    address = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="emergency_contacts")


class MediaAttachment(db.Model, SerializerMixin):
    __tablename__ = "media_attachments"

    id = db.Column(db.Integer, primary_key=True)
    file_url = db.Column(db.String, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.TIMESTAMP)

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    report = db.relationship("Report", back_populates="media_attachments")


# class StatusReport(db.Model, SerializerMixin):
#     __tablename__ = "status_reports"

#     id = db.Column(db.Integer, primary_key=True)
#     previous_status = db.Column(db.String, nullable=False)
#     new_status = db.Column(db.String, nullable=False)
#     changed_at = db.Column(db.TIMESTAMP)

#     report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
#     # changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

#     report = db.relationship('Report', back_populates='status_reports')
#     # admin = db.relationship('User', back_populates='status_reports_changed')


class Location(db.Model, SerializerMixin):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String)

    created_at = db.Column(db.TIMESTAMP)

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    report = db.relationship("Report", back_populates="location")


class StatusUpdate(db.Model):
    __tablename__ = "status_updates"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    updated_by = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    report = db.relationship('Report', back_populates='status_updates')

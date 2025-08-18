from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime

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
    """
    User model representing a user in the system.
    
    Attributes:
        id (int): Unique identifier for the user
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address (unique)
        password (str): Hashed password
        phone_number (str): User's phone number (unique)
        created_at (datetime): Timestamp when user was created
        role (str): User's role (user or admin)
    """
    __tablename__ = "users"
    serialize_rules = ("-reports", "-emergency_contacts", "-password")

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.VARCHAR, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = db.Column(db.String, default="user")
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == "admin"

    reports = db.relationship("Report", back_populates="user", cascade="all, delete")
    emergency_contacts = db.relationship( "EmergencyContact", back_populates="user", cascade="all, delete" )
    # status_updates = db.relationship('StatusUpdates', back_populates='admin', cascade='all, delete')


class Report(db.Model, SerializerMixin):
    """
    Report model representing an emergency report.
    
    Attributes:
        id (int): Unique identifier for the report
        user_id (int): Foreign key to the user who created the report
        incident (str): Type of incident
        details (str): Detailed description of the incident
        latitude (float): Latitude coordinate of the incident
        longitude (float): Longitude coordinate of the incident
        created_at (datetime): Timestamp when report was created
    """
    __tablename__ = "reports"
    serialize_rules = ("-user", "-status_updates", "-media_attachments", "-location")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    incident = db.Column(db.String, nullable=False)
    details = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False, server_default="0")
    longitude = db.Column(db.Float, nullable=False, server_default="0")
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="reports")
    location = db.relationship( "Location", back_populates="report", uselist=False, cascade="all, delete" )
    media_attachments = db.relationship(  "MediaAttachment", back_populates="report", cascade="all, delete" )
    status_updates = db.relationship('StatusUpdate', back_populates='report', cascade='all, delete')

class EmergencyContact(db.Model, SerializerMixin):
    """
    EmergencyContact model representing a user's emergency contact.
    
    Attributes:
        id (int): Unique identifier for the emergency contact
        name (str): Contact's name
        relationship (str): Relationship to the user
        phone_number (str): Contact's phone number
        email (str): Contact's email address (optional)
        address (str): Contact's address (optional)
        user_id (int): Foreign key to the user who owns this contact
    """
    __tablename__ = "emergency_contacts"
    serialize_rules = ("-user.reports", "-user.emergency_contacts")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    relationship = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    address = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="emergency_contacts")


class MediaAttachment(db.Model, SerializerMixin):
    """
    MediaAttachment model representing media files attached to reports.
    
    Attributes:
        id (int): Unique identifier for the media attachment
        file_url (str): URL or path to the media file
        media_type (str): MIME type of the media file
        uploaded_at (datetime): Timestamp when media was uploaded
        report_id (int): Foreign key to the report this media belongs to
    """
    __tablename__ = "media_attachments"

    id = db.Column(db.Integer, primary_key=True)
    file_url = db.Column(db.String, nullable=False)
    media_type = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    """
    Location model representing the location of a report.
    
    Attributes:
        id (int): Unique identifier for the location
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        address (str): Human-readable address (optional)
        created_at (datetime): Timestamp when location was created
        report_id (int): Foreign key to the report this location belongs to
    """
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    report = db.relationship("Report", back_populates="location")


class StatusUpdate(db.Model):
    """
    StatusUpdate model representing status updates for reports.
    
    Attributes:
        id (int): Unique identifier for the status update
        updated_by (str): Identifier of who updated the status
        status (str): Current status of the report
        timestamp (datetime): When the status was updated
        report_id (int): Foreign key to the report this status update belongs to
    """
    __tablename__ = "status_updates"

    id = db.Column(db.Integer, primary_key=True)
    updated_by = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    report = db.relationship('Report', back_populates='status_updates')

class TokenBlocklist(db.Model):
    """
    TokenBlocklist model for storing revoked JWT tokens.
    
    Attributes:
        id (int): Unique identifier for the blocklist entry
        jti (str): JWT token identifier
        created_at (datetime): When the token was revoked
    """
    __tablename__ = "token_blocklist"
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

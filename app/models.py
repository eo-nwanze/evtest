from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import ENUM
from app import db, login_manager
from datetime import datetime
from enum import Enum
import mimetypes
import os  # Add this line to import the os module



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    suburb = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(200))

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class FileType(Enum):
    # Existing file types
    IMAGE = "Image",
    VIDEO = "Video",
    DOCS = "Docs",
    MUSIC = "Music",
    DOWNLOADS = "Downloads",
    ARCHIVES = "Archives",
    PDF = "Pdf",
    DOCX = "Docx",
    ZIP = "Zip",
    JPG = "Jpg",
    PNG = "Png",
    # New file types
    CSV = "Csv",
    XLSX = "Xlsx",
    GIF = "Gif",
    OTHER = "Other",  # Added an "Other" category for unknown file types

# Define a mapping of file extensions to file types
file_extension_map = {
    'pdf': FileType.PDF,
    'docx': FileType.DOCX,
    'csv': FileType.CSV,
    'xlsx': FileType.XLSX,
    'jpg': FileType.JPG,
    'jpeg': FileType.JPG,
    'png': FileType.PNG,
    'gif': FileType.GIF,
    'mp4': FileType.VIDEO,
    'other': FileType.OTHER,
}



class SharedFile(db.Model):
    __tablename__ = 'shared_files'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)  # parent folder ID
    is_zipped = db.Column(db.Boolean, default=False)  # zip feature

    files = db.relationship('File', backref='folder', lazy=True)
    children = db.relationship("Folder")  # This sets up parent-child relationships between folders


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary)
    size = db.Column(db.Integer)  # size in bytes
    file_type = db.Column(db.Enum(FileType))  # file type
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # recycle bin feature

    shared_files = db.relationship('SharedFile', backref='file', lazy=True)

    def set_file_type(self):
        # Extract the file extension from the file name
        file_extension = os.path.splitext(self.name)[1][1:].lower()

        # Use the file_extension_map to set the file_type attribute
        self.file_type = file_extension_map.get(file_extension, FileType.OTHER)


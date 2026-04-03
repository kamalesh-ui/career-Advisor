# models/user_model.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ---------------------------
# USER MODEL
# ---------------------------
class User(db.Model):
    __tablename__ = "users"

    # ---------------------------
    # BASIC INFO
    # ---------------------------
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=True
    )

    # ---------------------------
    # PROFILE DATA
    # ---------------------------
    skills = db.Column(
        db.Text,
        default=""
    )

    interests = db.Column(
        db.Text,
        default=""
    )

    education = db.Column(
        db.String(150),
        nullable=True
    )

    # ---------------------------
    # STATUS
    # ---------------------------
    is_active = db.Column(
        db.Boolean,
        default=True
    )

    role = db.Column(
        db.String(50),
        default="user"
    )

    # ---------------------------
    # TIMESTAMPS
    # ---------------------------
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ---------------------------
    # AUTH METHODS
    # ---------------------------
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # ---------------------------
    # SKILLS METHODS
    # ---------------------------
    def set_skills(self, skills_list):
        if isinstance(skills_list, list):
            self.skills = ",".join(skills_list)

    def get_skills(self):
        return self.skills.split(",") if self.skills else []

    # ---------------------------
    # INTEREST METHODS
    # ---------------------------
    def set_interests(self, interests_list):
        if isinstance(interests_list, list):
            self.interests = ",".join(interests_list)

    def get_interests(self):
        return self.interests.split(",") if self.interests else []

    # ---------------------------
    # UPDATE PROFILE
    # ---------------------------
    def update_profile(self, data):
        self.name = data.get("name", self.name)
        self.education = data.get("education", self.education)

        if "skills" in data:
            self.set_skills(data["skills"])

        if "interests" in data:
            self.set_interests(data["interests"])

    # ---------------------------
    # SERIALIZE
    # ---------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "skills": self.get_skills(),
            "interests": self.get_interests(),
            "education": self.education,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<User {self.email}>"

# models/career_model.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user_model import db

# ---------------------------
# CAREER MODEL
# ---------------------------
class Career(db.Model):
    __tablename__ = "careers"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(120),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    domain = db.Column(
        db.String(100),
        nullable=True
    )

    skills_required = db.Column(
        db.Text,
        default=""
    )

    salary_range = db.Column(
        db.String(100),
        nullable=True
    )

    growth_rate = db.Column(
        db.String(50),
        nullable=True
    )

    demand_level = db.Column(
        db.String(50),
        default="Medium"
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
    # SKILLS METHODS
    # ---------------------------
    def set_skills(self, skills_list):
        if isinstance(skills_list, list):
            self.skills_required = ",".join(skills_list)

    def get_skills(self):
        return self.skills_required.split(",") if self.skills_required else []

    # ---------------------------
    # SERIALIZE
    # ---------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "skills_required": self.get_skills(),
            "salary_range": self.salary_range,
            "growth_rate": self.growth_rate,
            "demand_level": self.demand_level
        }

    def __repr__(self):
        return f"<Career {self.title}>"
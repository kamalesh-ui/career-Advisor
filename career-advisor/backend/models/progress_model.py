# models/progress_model.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user_model import db

# ---------------------------
# USER PROGRESS MODEL
# ---------------------------
class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    career_id = db.Column(
        db.Integer,
        db.ForeignKey("careers.id"),
        nullable=False
    )

    current_level = db.Column(
        db.String(50),
        default="Beginner"
    )

    completed_steps = db.Column(
        db.Text,
        default=""
    )

    progress_percent = db.Column(
        db.Float,
        default=0.0
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
    # METHODS
    # ---------------------------
    def set_completed_steps(self, steps):
        if isinstance(steps, list):
            self.completed_steps = ",".join(steps)

    def get_completed_steps(self):
        return self.completed_steps.split(",") if self.completed_steps else []

    def update_progress(self, steps_completed, total_steps):
        if total_steps == 0:
            self.progress_percent = 0
        else:
            self.progress_percent = (steps_completed / total_steps) * 100

    # ---------------------------
    # SERIALIZE
    # ---------------------------
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "career_id": self.career_id,
            "current_level": self.current_level,
            "completed_steps": self.get_completed_steps(),
            "progress_percent": self.progress_percent
        }

    def __repr__(self):
        return f"<Progress User:{self.user_id} Career:{self.career_id}>"
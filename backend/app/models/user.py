"""User model with learning statistics."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    password_legacy = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # 学习统计字段
    total_problems = db.Column(db.Integer, default=0)
    correct_problems = db.Column(db.Integer, default=0)
    total_study_time = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date, nullable=True)
    
    # 等级和经验值
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    
    # 个人信息
    avatar = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(500), nullable=True)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256")
        self.password_legacy = None

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def check_legacy_password(self, raw_password: str) -> bool:
        if not self.password_legacy:
            return False
        hashed = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
        return hashed == self.password_legacy

    def verify_and_upgrade_password(self, raw_password: str) -> bool:
        if self.check_password(raw_password):
            return True

        if self.check_legacy_password(raw_password):
            self.set_password(raw_password)
            return True

        return False

    def add_experience(self, points: int) -> bool:
        """Add experience points and check for level up."""
        self.experience += points
        leveled_up = False
        
        while self.experience >= self._get_next_level_exp():
            self.experience -= self._get_next_level_exp()
            self.level += 1
            leveled_up = True
        
        return leveled_up

    def _get_next_level_exp(self) -> int:
        """Calculate experience needed for next level."""
        return int(100 * (self.level ** 1.5))

    def update_study_streak(self) -> bool:
        """Update study streak. Returns True if streak continues."""
        from datetime import date
        today = date.today()
        
        if self.last_study_date is None:
            self.streak_days = 1
            self.last_study_date = today
            return True
        
        days_diff = (today - self.last_study_date).days
        
        if days_diff == 0:
            return True
        elif days_diff == 1:
            self.streak_days += 1
            self.last_study_date = today
            return True
        else:
            self.streak_days = 1
            self.last_study_date = today
            return False

    def record_problem(self, is_correct: bool, study_time: int = 0):
        """Record a problem attempt."""
        self.total_problems += 1
        if is_correct:
            self.correct_problems += 1
        self.total_study_time += study_time
        self.update_study_streak()

    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate."""
        if self.total_problems == 0:
            return 0.0
        return (self.correct_problems / self.total_problems) * 100

    @property
    def level_title(self) -> str:
        """Get title based on level."""
        if self.level < 5:
            return "初学者"
        elif self.level < 10:
            return "学习者"
        elif self.level < 20:
            return "进阶者"
        elif self.level < 30:
            return "高手"
        else:
            return "大师"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "createdAt": self._to_iso(self.created_at),
            "lastLoginAt": self._to_iso(self.last_login_at),
            "stats": {
                "totalProblems": self.total_problems,
                "correctProblems": self.correct_problems,
                "accuracyRate": round(self.accuracy_rate, 2),
                "totalStudyTime": self.total_study_time,
                "streakDays": self.streak_days,
            },
            "level": {
                "current": self.level,
                "title": self.level_title,
                "experience": self.experience,
                "nextLevelExp": self._get_next_level_exp(),
            },
            "profile": {
                "avatar": self.avatar,
                "bio": self.bio,
            }
        }

    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat(timespec="milliseconds") + "Z"


class Achievement(db.Model):
    """Achievement definition model."""
    __tablename__ = "achievements"

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(50), default="trophy")
    category = db.Column(db.String(20), default="general")
    condition_type = db.Column(db.String(50), nullable=False)
    condition_value = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "points": self.points,
        }


class UserAchievement(db.Model):
    """User achievement unlock record."""
    __tablename__ = "user_achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    achievement_id = db.Column(db.String(50), db.ForeignKey("achievements.id"), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("achievements", lazy="dynamic"))
    achievement = db.relationship("Achievement")

    def to_dict(self) -> dict:
        return {
            "achievement": self.achievement.to_dict(),
            "unlockedAt": self.unlocked_at.isoformat() + "Z",
        }


class StudyRecord(db.Model):
    """Daily study record for statistics."""
    __tablename__ = "study_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    problems_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    study_time = db.Column(db.Integer, default=0)
    experience_gained = db.Column(db.Integer, default=0)

    user = db.relationship("User", backref=db.backref("study_records", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="unique_user_date"),
    )

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "problemsCount": self.problems_count,
            "correctCount": self.correct_count,
            "studyTime": self.study_time,
            "experienceGained": self.experience_gained,
        }

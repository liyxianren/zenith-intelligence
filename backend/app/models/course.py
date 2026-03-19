"""Course and lesson models."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


class Course(db.Model):
    """Course model."""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.Integer, default=1)
    cover_image = db.Column(db.String(500), nullable=True)
    instructor = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chapters = db.relationship("Chapter", backref="course", lazy="dynamic", order_by="Chapter.order_index")

    def to_dict(self, include_chapters: bool = False) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "subject": self.subject,
            "difficulty": self.difficulty,
            "coverImage": self.cover_image,
            "instructor": self.instructor,
            "duration": self.duration,
            "isFeatured": self.is_featured,
            "orderIndex": self.order_index,
            "chapterCount": self.chapters.count(),
            "createdAt": self._to_iso(self.created_at),
            "updatedAt": self._to_iso(self.updated_at),
        }
        if include_chapters:
            result["chapters"] = [c.to_dict(include_lessons=True) for c in self.chapters.filter_by(is_active=True)]
        return result

    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat(timespec="milliseconds") + "Z"


class Chapter(db.Model):
    """Chapter model."""
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lessons = db.relationship("Lesson", backref="chapter", lazy="dynamic", order_by="Lesson.order_index")

    def to_dict(self, include_lessons: bool = False) -> dict:
        result = {
            "id": self.id,
            "courseId": self.course_id,
            "name": self.name,
            "description": self.description,
            "orderIndex": self.order_index,
            "lessonCount": self.lessons.count(),
        }
        if include_lessons:
            result["lessons"] = [l.to_dict() for l in self.lessons.filter_by(is_active=True)]
        return result


class Lesson(db.Model):
    """Lesson model."""
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    content_type = db.Column(db.String(20), default="markdown")
    video_url = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercises = db.relationship("Exercise", backref="lesson", lazy="dynamic")

    def to_dict(self, include_content: bool = False) -> dict:
        result = {
            "id": self.id,
            "chapterId": self.chapter_id,
            "name": self.name,
            "description": self.description,
            "contentType": self.content_type,
            "videoUrl": self.video_url,
            "duration": self.duration,
            "orderIndex": self.order_index,
            "isFree": self.is_free,
            "exerciseCount": self.exercises.count(),
        }
        if include_content:
            result["content"] = self.content
        return result


class Exercise(db.Model):
    """Exercise model."""
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exercise_type = db.Column(db.String(20), default="choice")
    difficulty = db.Column(db.Integer, default=1)
    initial_code = db.Column(db.Text, nullable=True)
    test_cases = db.Column(db.Text, nullable=True)
    hint = db.Column(db.Text, nullable=True)
    solution = db.Column(db.Text, nullable=True)
    options = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.String(500), nullable=True)
    points = db.Column(db.Integer, default=10)
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_solution: bool = False) -> dict:
        result = {
            "id": self.id,
            "lessonId": self.lesson_id,
            "title": self.title,
            "description": self.description,
            "exerciseType": self.exercise_type,
            "difficulty": self.difficulty,
            "initialCode": self.initial_code,
            "hint": self.hint,
            "points": self.points,
            "orderIndex": self.order_index,
        }
        if self.options:
            import json
            try:
                result["options"] = json.loads(self.options)
            except:
                result["options"] = []
        if include_solution:
            result["solution"] = self.solution
            result["correctAnswer"] = self.correct_answer
            result["testCases"] = self.test_cases
        return result


class UserCourseProgress(db.Model):
    """User course learning progress."""
    __tablename__ = "user_course_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    current_lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=True)
    completed_lessons = db.Column(db.Text, default="[]")
    progress_percent = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_access_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("course_progress", lazy="dynamic"))
    course = db.relationship("Course", backref=db.backref("user_progress", lazy="dynamic"))
    current_lesson = db.relationship("Lesson")

    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="unique_user_course"),
    )

    def to_dict(self) -> dict:
        import json
        completed = []
        try:
            completed = json.loads(self.completed_lessons or "[]")
        except:
            pass

        return {
            "courseId": self.course_id,
            "currentLessonId": self.current_lesson_id,
            "completedLessons": completed,
            "progressPercent": self.progress_percent,
            "startedAt": self._to_iso(self.started_at),
            "lastAccessAt": self._to_iso(self.last_access_at),
            "completedAt": self._to_iso(self.completed_at),
        }

    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat(timespec="milliseconds") + "Z"


class ExerciseSubmission(db.Model):
    """Exercise submission record."""
    __tablename__ = "exercise_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    result = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("submissions", lazy="dynamic"))
    exercise = db.relationship("Exercise", backref=db.backref("submissions", lazy="dynamic"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exerciseId": self.exercise_id,
            "isCorrect": self.is_correct,
            "timeSpent": self.time_spent,
            "submittedAt": self._to_iso(self.submitted_at),
        }

    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat(timespec="milliseconds") + "Z"

"""Course management API blueprint."""

from __future__ import annotations

import json
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.course import (
    Chapter,
    Course,
    Exercise,
    ExerciseSubmission,
    Lesson,
    UserCourseProgress,
)
from app.models.user import User

course_bp = Blueprint("course", __name__)


# ========================================
# Course API
# ========================================


@course_bp.route("/list", methods=["GET"])
def list_courses():
    """List all courses."""
    subject = request.args.get("subject")
    difficulty = request.args.get("difficulty", type=int)
    featured = request.args.get("featured")

    query = Course.query.filter_by(is_active=True)

    if subject:
        query = query.filter_by(subject=subject)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if featured is not None:
        query = query.filter_by(is_featured=featured.lower() == "true")

    query = query.order_by(Course.is_featured.desc(), Course.order_index, Course.id)

    courses = query.all()

    return jsonify({
        "success": True,
        "data": [c.to_dict() for c in courses]
    })


@course_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id: int):
    """Get a specific course with chapters."""
    course = db.session.get(Course, course_id)

    if not course or not course.is_active:
        return jsonify({"success": False, "error": "课程不存在"}), 404

    return jsonify({
        "success": True,
        "data": course.to_dict(include_chapters=True)
    })


@course_bp.route("/<int:course_id>/chapters", methods=["GET"])
def get_course_chapters(course_id: int):
    """Get all chapters of a course."""
    course = db.session.get(Course, course_id)

    if not course or not course.is_active:
        return jsonify({"success": False, "error": "课程不存在"}), 404

    chapters = (
        Chapter.query
        .filter_by(course_id=course_id, is_active=True)
        .order_by(Chapter.order_index)
        .all()
    )

    return jsonify({
        "success": True,
        "data": [c.to_dict(include_lessons=True) for c in chapters]
    })


# ========================================
# Chapter API
# ========================================


@course_bp.route("/chapter/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id: int):
    """Get a specific chapter."""
    chapter = db.session.get(Chapter, chapter_id)

    if not chapter or not chapter.is_active:
        return jsonify({"success": False, "error": "章节不存在"}), 404

    return jsonify({
        "success": True,
        "data": chapter.to_dict(include_lessons=True)
    })


# ========================================
# Lesson API
# ========================================


@course_bp.route("/lesson/<int:lesson_id>", methods=["GET"])
def get_lesson(lesson_id: int):
    """Get a specific lesson."""
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson or not lesson.is_active:
        return jsonify({"success": False, "error": "课时不存在"}), 404

    return jsonify({
        "success": True,
        "data": lesson.to_dict(include_content=True)
    })


@course_bp.route("/lesson/<int:lesson_id>/exercises", methods=["GET"])
def get_lesson_exercises(lesson_id: int):
    """Get exercises for a lesson."""
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson or not lesson.is_active:
        return jsonify({"success": False, "error": "课时不存在"}), 404

    exercises = (
        Exercise.query
        .filter_by(lesson_id=lesson_id, is_active=True)
        .order_by(Exercise.order_index)
        .all()
    )

    return jsonify({
        "success": True,
        "data": [e.to_dict() for e in exercises]
    })


# ========================================
# Exercise API
# ========================================


@course_bp.route("/exercise/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id: int):
    """Get a specific exercise."""
    exercise = db.session.get(Exercise, exercise_id)

    if not exercise or not exercise.is_active:
        return jsonify({"success": False, "error": "练习不存在"}), 404

    return jsonify({
        "success": True,
        "data": exercise.to_dict()
    })


@course_bp.route("/exercise/<int:exercise_id>/submit", methods=["POST"])
@jwt_required()
def submit_exercise(exercise_id: int):
    """Submit an exercise answer."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    exercise = db.session.get(Exercise, exercise_id)

    if not exercise or not exercise.is_active:
        return jsonify({"success": False, "error": "练习不存在"}), 404

    data = request.get_json() or {}
    answer = data.get("answer", "")
    time_spent = data.get("timeSpent", 0)

    is_correct = False
    result = ""

    if exercise.exercise_type == "choice":
        is_correct = answer == exercise.correct_answer
        result = "正确" if is_correct else f"错误，正确答案是: {exercise.correct_answer}"
    elif exercise.exercise_type == "code":
        is_correct = _check_code_answer(exercise, answer)
        result = "代码测试通过" if is_correct else "代码测试未通过"
    else:
        is_correct = answer.strip().lower() == (exercise.correct_answer or "").strip().lower()
        result = "正确" if is_correct else "错误"

    submission = ExerciseSubmission(
        user_id=user_id,
        exercise_id=exercise_id,
        answer=answer,
        is_correct=is_correct,
        result=result,
        time_spent=time_spent,
    )
    db.session.add(submission)

    if is_correct:
        user.add_experience(exercise.points)

    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "isCorrect": is_correct,
            "result": result,
            "points": exercise.points if is_correct else 0,
        }
    })


def _check_code_answer(exercise: Exercise, code: str) -> bool:
    """Check code answer against test cases."""
    if not exercise.test_cases:
        return True

    try:
        test_cases = json.loads(exercise.test_cases)
    except:
        return False

    for test_case in test_cases:
        input_data = test_case.get("input", "")
        expected_output = test_case.get("output", "")

        try:
            exec_globals = {}
            exec(code, exec_globals)

            if "solution" in exec_globals:
                result = exec_globals["solution"](input_data)
                if str(result).strip() != str(expected_output).strip():
                    return False
        except Exception:
            return False

    return True


@course_bp.route("/exercise/<int:exercise_id>/solution", methods=["GET"])
@jwt_required()
def get_exercise_solution(exercise_id: int):
    """Get exercise solution."""
    exercise = db.session.get(Exercise, exercise_id)

    if not exercise or not exercise.is_active:
        return jsonify({"success": False, "error": "练习不存在"}), 404

    submission = ExerciseSubmission.query.filter_by(
        user_id=get_jwt_identity(),
        exercise_id=exercise_id
    ).first()

    if not submission:
        return jsonify({"success": False, "error": "请先尝试解答"}), 403

    return jsonify({
        "success": True,
        "data": {
            "solution": exercise.solution,
            "correctAnswer": exercise.correct_answer,
            "testCases": exercise.test_cases,
        }
    })


# ========================================
# User Progress API
# ========================================


@course_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_user_courses_progress():
    """Get user's progress for all courses."""
    user_id = get_jwt_identity()

    progress_list = (
        UserCourseProgress.query
        .filter_by(user_id=user_id)
        .order_by(UserCourseProgress.last_access_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in progress_list]
    })


@course_bp.route("/<int:course_id>/progress", methods=["GET"])
@jwt_required()
def get_course_progress(course_id: int):
    """Get user's progress for a specific course."""
    user_id = get_jwt_identity()

    progress = UserCourseProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if not progress:
        course = db.session.get(Course, course_id)
        if not course or not course.is_active:
            return jsonify({"success": False, "error": "课程不存在"}), 404

        return jsonify({
            "success": True,
            "data": {
                "courseId": course_id,
                "currentLessonId": None,
                "completedLessons": [],
                "progressPercent": 0,
                "startedAt": None,
                "completedAt": None,
            }
        })

    return jsonify({
        "success": True,
        "data": progress.to_dict()
    })


@course_bp.route("/<int:course_id>/start", methods=["POST"])
@jwt_required()
def start_course(course_id: int):
    """Start a course."""
    user_id = get_jwt_identity()

    course = db.session.get(Course, course_id)
    if not course or not course.is_active:
        return jsonify({"success": False, "error": "课程不存在"}), 404

    progress = UserCourseProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if not progress:
        first_lesson = (
            Lesson.query
            .join(Chapter)
            .filter(Chapter.course_id == course_id, Lesson.is_active == True)
            .order_by(Chapter.order_index, Lesson.order_index)
            .first()
        )

        progress = UserCourseProgress(
            user_id=user_id,
            course_id=course_id,
            current_lesson_id=first_lesson.id if first_lesson else None,
        )
        db.session.add(progress)
        db.session.commit()

    return jsonify({
        "success": True,
        "data": progress.to_dict()
    })


@course_bp.route("/lesson/<int:lesson_id>/complete", methods=["POST"])
@jwt_required()
def complete_lesson(lesson_id: int):
    """Mark a lesson as completed."""
    user_id = get_jwt_identity()

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson or not lesson.is_active:
        return jsonify({"success": False, "error": "课时不存在"}), 404

    chapter = db.session.get(Chapter, lesson.chapter_id)
    course_id = chapter.course_id

    progress = UserCourseProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if not progress:
        return jsonify({"success": False, "error": "请先开始课程"}), 400

    completed = json.loads(progress.completed_lessons or "[]")
    if lesson_id not in completed:
        completed.append(lesson_id)
        progress.completed_lessons = json.dumps(completed)

    total_lessons = (
        Lesson.query
        .join(Chapter)
        .filter(Chapter.course_id == course_id, Lesson.is_active == True)
        .count()
    )

    progress.progress_percent = int((len(completed) / total_lessons) * 100) if total_lessons > 0 else 0

    next_lesson = (
        Lesson.query
        .join(Chapter)
        .filter(
            Chapter.course_id == course_id,
            Lesson.is_active == True,
            Lesson.order_index > lesson.order_index
        )
        .order_by(Chapter.order_index, Lesson.order_index)
        .first()
    )

    if next_lesson:
        progress.current_lesson_id = next_lesson.id
    else:
        progress.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "progress": progress.to_dict(),
            "nextLessonId": next_lesson.id if next_lesson else None,
        }
    })

"""Data statistics and analytics API blueprint."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.course import ExerciseSubmission, UserCourseProgress
from app.models.history import History
from app.models.user import StudyRecord, User

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_overview():
    """Get user's learning overview statistics."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    total_problems = History.query.filter_by(user_id=user_id).count()
    
    recent_7_days = date.today() - timedelta(days=7)
    recent_problems = (
        History.query
        .filter_by(user_id=user_id)
        .filter(History.created_at >= recent_7_days)
        .count()
    )

    total_study_time = user.total_study_time
    avg_daily_time = total_study_time // max(user.streak_days, 1)

    return jsonify({
        "success": True,
        "data": {
            "level": user.level,
            "levelTitle": user.level_title,
            "experience": user.experience,
            "nextLevelExp": user._get_next_level_exp(),
            "totalProblems": total_problems,
            "recentProblems": recent_problems,
            "accuracyRate": round(user.accuracy_rate, 2),
            "streakDays": user.streak_days,
            "totalStudyTime": total_study_time,
            "avgDailyTime": avg_daily_time,
        }
    })


@stats_bp.route("/daily", methods=["GET"])
@jwt_required()
def get_daily_stats():
    """Get daily learning statistics for charts."""
    user_id = get_jwt_identity()
    days = min(int(request.args.get("days", 30)), 90)

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= start_date)
        .filter(StudyRecord.date <= end_date)
        .order_by(StudyRecord.date)
        .all()
    )

    records_dict = {r.date: r for r in records}

    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date in records_dict:
            record = records_dict[current_date]
            daily_data.append({
                "date": current_date.isoformat(),
                "problemsCount": record.problems_count,
                "correctCount": record.correct_count,
                "studyTime": record.study_time,
                "experienceGained": record.experience_gained,
            })
        else:
            daily_data.append({
                "date": current_date.isoformat(),
                "problemsCount": 0,
                "correctCount": 0,
                "studyTime": 0,
                "experienceGained": 0,
            })
        current_date += timedelta(days=1)

    return jsonify({
        "success": True,
        "data": daily_data
    })


@stats_bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_subject_stats():
    """Get statistics by subject."""
    user_id = get_jwt_identity()

    history_records = History.query.filter_by(user_id=user_id).all()

    subject_stats = {}
    for record in history_records:
        parse_result = record.parse_result or {}
        subject = parse_result.get("subject", "其他")
        
        if subject not in subject_stats:
            subject_stats[subject] = {
                "subject": subject,
                "totalProblems": 0,
                "correctProblems": 0,
            }
        
        subject_stats[subject]["totalProblems"] += 1

    result = list(subject_stats.values())
    result.sort(key=lambda x: x["totalProblems"], reverse=True)

    return jsonify({
        "success": True,
        "data": result
    })


@stats_bp.route("/difficulty", methods=["GET"])
@jwt_required()
def get_difficulty_stats():
    """Get statistics by difficulty level."""
    user_id = get_jwt_identity()

    history_records = History.query.filter_by(user_id=user_id).all()

    difficulty_stats = {
        "简单": {"totalProblems": 0, "label": "简单"},
        "中等": {"totalProblems": 0, "label": "中等"},
        "困难": {"totalProblems": 0, "label": "困难"},
        "未知": {"totalProblems": 0, "label": "未知"},
    }

    for record in history_records:
        parse_result = record.parse_result or {}
        difficulty = parse_result.get("difficulty", "未知")
        
        if difficulty in difficulty_stats:
            difficulty_stats[difficulty]["totalProblems"] += 1
        else:
            difficulty_stats["未知"]["totalProblems"] += 1

    result = list(difficulty_stats.values())
    result = [r for r in result if r["totalProblems"] > 0]

    return jsonify({
        "success": True,
        "data": result
    })


@stats_bp.route("/weekly", methods=["GET"])
@jwt_required()
def get_weekly_stats():
    """Get weekly learning statistics."""
    user_id = get_jwt_identity()

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)

    this_week_records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= week_start)
        .filter(StudyRecord.date <= today)
        .all()
    )

    last_week_records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= last_week_start)
        .filter(StudyRecord.date < week_start)
        .all()
    )

    def _sum_records(records):
        return {
            "problemsCount": sum(r.problems_count for r in records),
            "correctCount": sum(r.correct_count for r in records),
            "studyTime": sum(r.study_time for r in records),
            "experienceGained": sum(r.experience_gained for r in records),
        }

    this_week = _sum_records(this_week_records)
    last_week = _sum_records(last_week_records)

    def _calc_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

    return jsonify({
        "success": True,
        "data": {
            "thisWeek": this_week,
            "lastWeek": last_week,
            "changes": {
                "problemsCount": _calc_change(this_week["problemsCount"], last_week["problemsCount"]),
                "studyTime": _calc_change(this_week["studyTime"], last_week["studyTime"]),
                "experienceGained": _calc_change(this_week["experienceGained"], last_week["experienceGained"]),
            }
        }
    })


@stats_bp.route("/course-progress", methods=["GET"])
@jwt_required()
def get_course_progress_stats():
    """Get course learning progress statistics."""
    user_id = get_jwt_identity()

    progress_records = UserCourseProgress.query.filter_by(user_id=user_id).all()

    total_courses = len(progress_records)
    completed_courses = sum(1 for p in progress_records if p.completed_at is not None)
    in_progress_courses = total_courses - completed_courses

    avg_progress = (
        sum(p.progress_percent for p in progress_records) / total_courses
        if total_courses > 0 else 0
    )

    return jsonify({
        "success": True,
        "data": {
            "totalCourses": total_courses,
            "completedCourses": completed_courses,
            "inProgressCourses": in_progress_courses,
            "averageProgress": round(avg_progress, 1),
        }
    })


@stats_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def get_activity_heatmap():
    """Get activity heatmap data for the past year."""
    user_id = get_jwt_identity()

    end_date = date.today()
    start_date = end_date - timedelta(days=365)

    records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= start_date)
        .filter(StudyRecord.date <= end_date)
        .all()
    )

    heatmap_data = {}
    for record in records:
        date_str = record.date.isoformat()
        heatmap_data[date_str] = record.problems_count

    return jsonify({
        "success": True,
        "data": heatmap_data
    })


@stats_bp.route("/ranking", methods=["GET"])
@jwt_required()
def get_user_ranking():
    """Get user's ranking in various metrics."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    level_rank = (
        db.session.query(func.count(User.id))
        .filter(User.level > user.level)
        .scalar() + 1
    )

    problems_rank = (
        db.session.query(func.count(User.id))
        .filter(User.total_problems > user.total_problems)
        .scalar() + 1
    )

    streak_rank = (
        db.session.query(func.count(User.id))
        .filter(User.streak_days > user.streak_days)
        .scalar() + 1
    )

    total_users = User.query.count()

    return jsonify({
        "success": True,
        "data": {
            "levelRank": level_rank,
            "problemsRank": problems_rank,
            "streakRank": streak_rank,
            "totalUsers": total_users,
            "percentiles": {
                "level": round((1 - level_rank / total_users) * 100, 1) if total_users > 0 else 0,
                "problems": round((1 - problems_rank / total_users) * 100, 1) if total_users > 0 else 0,
                "streak": round((1 - streak_rank / total_users) * 100, 1) if total_users > 0 else 0,
            }
        }
    })

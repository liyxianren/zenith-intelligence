"""Achievement and leaderboard API blueprint."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.user import Achievement, StudyRecord, User, UserAchievement

achievement_bp = Blueprint("achievement", __name__)


@achievement_bp.route("/list", methods=["GET"])
def list_achievements():
    """List all available achievements."""
    achievements = Achievement.query.order_by(Achievement.category, Achievement.points).all()
    return jsonify({
        "success": True,
        "data": [a.to_dict() for a in achievements]
    })


@achievement_bp.route("/user/<user_id>", methods=["GET"])
@jwt_required()
def get_user_achievements(user_id: str):
    """Get achievements unlocked by a user."""
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"success": False, "error": "无权访问"}), 403

    user_achievements = (
        UserAchievement.query
        .filter_by(user_id=user_id)
        .order_by(UserAchievement.unlocked_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "data": [ua.to_dict() for ua in user_achievements]
    })


@achievement_bp.route("/check", methods=["POST"])
@jwt_required()
def check_achievements():
    """Check and unlock achievements for current user."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    unlocked = []

    all_achievements = Achievement.query.all()
    unlocked_ids = {ua.achievement_id for ua in user.achievements}

    for achievement in all_achievements:
        if achievement.id in unlocked_ids:
            continue

        if _check_achievement_condition(user, achievement):
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            user.add_experience(achievement.points)
            unlocked.append(achievement.to_dict())

    if unlocked:
        db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "unlocked": unlocked,
            "total_points": sum(a["points"] for a in unlocked)
        }
    })


def _check_achievement_condition(user: User, achievement: Achievement) -> bool:
    """Check if user meets achievement condition."""
    condition_type = achievement.condition_type
    required_value = achievement.condition_value

    if condition_type == "total_problems":
        return user.total_problems >= required_value
    elif condition_type == "correct_problems":
        return user.correct_problems >= required_value
    elif condition_type == "accuracy_rate":
        return user.accuracy_rate >= required_value
    elif condition_type == "streak_days":
        return user.streak_days >= required_value
    elif condition_type == "level":
        return user.level >= required_value
    elif condition_type == "study_time":
        return user.total_study_time >= required_value

    return False


@achievement_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get global leaderboard."""
    leaderboard_type = request.args.get("type", "level")
    limit = min(int(request.args.get("limit", 50)), 100)

    if leaderboard_type == "level":
        users = (
            User.query
            .order_by(User.level.desc(), User.experience.desc())
            .limit(limit)
            .all()
        )
        key = "level"
    elif leaderboard_type == "problems":
        users = (
            User.query
            .order_by(User.total_problems.desc())
            .limit(limit)
            .all()
        )
        key = "total_problems"
    elif leaderboard_type == "accuracy":
        users = (
            User.query
            .filter(User.total_problems >= 10)
            .order_by(User.correct_problems.desc())
            .limit(limit)
            .all()
        )
        key = "accuracy_rate"
    elif leaderboard_type == "streak":
        users = (
            User.query
            .order_by(User.streak_days.desc())
            .limit(limit)
            .all()
        )
        key = "streak_days"
    else:
        users = (
            User.query
            .order_by(User.level.desc(), User.experience.desc())
            .limit(limit)
            .all()
        )
        key = "level"

    leaderboard = []
    for rank, user in enumerate(users, 1):
        entry = {
            "rank": rank,
            "userId": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "level": user.level,
            "levelTitle": user.level_title,
        }

        if key == "level":
            entry["value"] = user.level
            entry["subtitle"] = f"经验值: {user.experience}"
        elif key == "total_problems":
            entry["value"] = user.total_problems
            entry["subtitle"] = f"正确: {user.correct_problems}"
        elif key == "accuracy_rate":
            entry["value"] = round(user.accuracy_rate, 1)
            entry["subtitle"] = f"题目数: {user.total_problems}"
        elif key == "streak_days":
            entry["value"] = user.streak_days
            entry["subtitle"] = "连续学习天数"

        leaderboard.append(entry)

    return jsonify({
        "success": True,
        "data": {
            "type": leaderboard_type,
            "leaderboard": leaderboard
        }
    })


@achievement_bp.route("/stats/daily", methods=["GET"])
@jwt_required()
def get_daily_stats():
    """Get daily study statistics for the current user."""
    user_id = get_jwt_identity()
    days = min(int(request.args.get("days", 7)), 30)

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

    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        if current_date in records_dict:
            record = records_dict[current_date]
            daily_stats.append({
                "date": current_date.isoformat(),
                "problemsCount": record.problems_count,
                "correctCount": record.correct_count,
                "studyTime": record.study_time,
                "experienceGained": record.experience_gained,
            })
        else:
            daily_stats.append({
                "date": current_date.isoformat(),
                "problemsCount": 0,
                "correctCount": 0,
                "studyTime": 0,
                "experienceGained": 0,
            })
        current_date += timedelta(days=1)

    return jsonify({
        "success": True,
        "data": daily_stats
    })


@achievement_bp.route("/stats/summary", methods=["GET"])
@jwt_required()
def get_stats_summary():
    """Get study statistics summary for the current user."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_record = StudyRecord.query.filter_by(user_id=user_id, date=today).first()
    week_records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= week_start)
        .all()
    )
    month_records = (
        StudyRecord.query
        .filter_by(user_id=user_id)
        .filter(StudyRecord.date >= month_start)
        .all()
    )

    def _sum_records(records):
        return {
            "problemsCount": sum(r.problems_count for r in records),
            "correctCount": sum(r.correct_count for r in records),
            "studyTime": sum(r.study_time for r in records),
            "experienceGained": sum(r.experience_gained for r in records),
        }

    return jsonify({
        "success": True,
        "data": {
            "total": {
                "problemsCount": user.total_problems,
                "correctCount": user.correct_problems,
                "accuracyRate": round(user.accuracy_rate, 2),
                "studyTime": user.total_study_time,
                "streakDays": user.streak_days,
            },
            "today": _sum_records([today_record] if today_record else []),
            "week": _sum_records(week_records),
            "month": _sum_records(month_records),
        }
    })

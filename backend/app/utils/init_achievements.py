"""Initialize default achievements."""

from app.extensions import db
from app.models.user import Achievement


def init_achievements():
    """Initialize default achievements."""
    achievements_data = [
        # 题目数量成就
        {
            "id": "first_problem",
            "name": "初出茅庐",
            "description": "完成第一道题目",
            "icon": "star",
            "category": "problems",
            "condition_type": "total_problems",
            "condition_value": 1,
            "points": 5,
        },
        {
            "id": "problem_solver_10",
            "name": "解题新手",
            "description": "累计完成10道题目",
            "icon": "book",
            "category": "problems",
            "condition_type": "total_problems",
            "condition_value": 10,
            "points": 10,
        },
        {
            "id": "problem_solver_50",
            "name": "解题达人",
            "description": "累计完成50道题目",
            "icon": "award",
            "category": "problems",
            "condition_type": "total_problems",
            "condition_value": 50,
            "points": 25,
        },
        {
            "id": "problem_solver_100",
            "name": "解题大师",
            "description": "累计完成100道题目",
            "icon": "crown",
            "category": "problems",
            "condition_type": "total_problems",
            "condition_value": 100,
            "points": 50,
        },
        {
            "id": "problem_solver_500",
            "name": "解题传奇",
            "description": "累计完成500道题目",
            "icon": "gem",
            "category": "problems",
            "condition_type": "total_problems",
            "condition_value": 500,
            "points": 100,
        },
        
        # 正确率成就
        {
            "id": "accuracy_80",
            "name": "精准射手",
            "description": "正确率达到80%",
            "icon": "target",
            "category": "accuracy",
            "condition_type": "accuracy_rate",
            "condition_value": 80,
            "points": 20,
        },
        {
            "id": "accuracy_90",
            "name": "神射手",
            "description": "正确率达到90%",
            "icon": "crosshair",
            "category": "accuracy",
            "condition_type": "accuracy_rate",
            "condition_value": 90,
            "points": 40,
        },
        {
            "id": "accuracy_95",
            "name": "完美主义",
            "description": "正确率达到95%",
            "icon": "check-circle",
            "category": "accuracy",
            "condition_type": "accuracy_rate",
            "condition_value": 95,
            "points": 80,
        },
        
        # 连续学习成就
        {
            "id": "streak_3",
            "name": "坚持三天",
            "description": "连续学习3天",
            "icon": "flame",
            "category": "streak",
            "condition_type": "streak_days",
            "condition_value": 3,
            "points": 10,
        },
        {
            "id": "streak_7",
            "name": "周冠军",
            "description": "连续学习7天",
            "icon": "calendar",
            "category": "streak",
            "condition_type": "streak_days",
            "condition_value": 7,
            "points": 25,
        },
        {
            "id": "streak_30",
            "name": "月度之星",
            "description": "连续学习30天",
            "icon": "sun",
            "category": "streak",
            "condition_type": "streak_days",
            "condition_value": 30,
            "points": 100,
        },
        {
            "id": "streak_100",
            "name": "百日坚持",
            "description": "连续学习100天",
            "icon": "fire",
            "category": "streak",
            "condition_type": "streak_days",
            "condition_value": 100,
            "points": 200,
        },
        
        # 等级成就
        {
            "id": "level_5",
            "name": "进阶之路",
            "description": "达到5级",
            "icon": "trending-up",
            "category": "level",
            "condition_type": "level",
            "condition_value": 5,
            "points": 15,
        },
        {
            "id": "level_10",
            "name": "学习达人",
            "description": "达到10级",
            "icon": "zap",
            "category": "level",
            "condition_type": "level",
            "condition_value": 10,
            "points": 30,
        },
        {
            "id": "level_20",
            "name": "知识大师",
            "description": "达到20级",
            "icon": "shield",
            "category": "level",
            "condition_type": "level",
            "condition_value": 20,
            "points": 60,
        },
        {
            "id": "level_30",
            "name": "传奇学霸",
            "description": "达到30级",
            "icon": "crown",
            "category": "level",
            "condition_type": "level",
            "condition_value": 30,
            "points": 150,
        },
        
        # 学习时长成就
        {
            "id": "study_time_1h",
            "name": "初学乍练",
            "description": "累计学习1小时",
            "icon": "clock",
            "category": "time",
            "condition_type": "study_time",
            "condition_value": 60,
            "points": 5,
        },
        {
            "id": "study_time_10h",
            "name": "勤学苦练",
            "description": "累计学习10小时",
            "icon": "watch",
            "category": "time",
            "condition_type": "study_time",
            "condition_value": 600,
            "points": 20,
        },
        {
            "id": "study_time_50h",
            "name": "学而不厌",
            "description": "累计学习50小时",
            "icon": "hourglass",
            "category": "time",
            "condition_type": "study_time",
            "condition_value": 3000,
            "points": 50,
        },
        {
            "id": "study_time_100h",
            "name": "博学多才",
            "description": "累计学习100小时",
            "icon": "book-open",
            "category": "time",
            "condition_type": "study_time",
            "condition_value": 6000,
            "points": 100,
        },
    ]
    
    for data in achievements_data:
        existing = Achievement.query.filter_by(id=data["id"]).first()
        if not existing:
            achievement = Achievement(**data)
            db.session.add(achievement)
    
    db.session.commit()
    print(f"已初始化 {len(achievements_data)} 个成就")

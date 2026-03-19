import json
import traceback
from pathlib import Path

from app import create_app, db
from app.models.course import Course, Chapter, Lesson, Exercise


REPO_ROOT = Path(__file__).resolve().parents[2]
LESSON_CONTENT_DIRS = [
    REPO_ROOT / "Docs",
    REPO_ROOT / "backend" / "data" / "lessons",
]


def load_lesson_markdown(filename: str, title: str) -> str:
    for content_dir in LESSON_CONTENT_DIRS:
        md_path = content_dir / filename
        if md_path.exists():
            return md_path.read_text(encoding="utf-8")

    searched = "\n".join(str(path / filename) for path in LESSON_CONTENT_DIRS)
    return f"# {title}\n文件未找到，已检查以下路径：\n{searched}"

def seed_courses():
    app = create_app()
    with app.app_context():
        # First check if courses already exist
        if Course.query.count() > 0:
            print("Courses already exist. Dropping existing course data...")
            # We need to delete them. To avoid foreign key constraint issues, 
            # delete in reverse order of dependence
            Exercise.query.delete()
            Lesson.query.delete()
            Chapter.query.delete()
            Course.query.delete()
            db.session.commit()
            print("Existing course data cleared.")

        print("Starting to seed courses...")

        # ---------------------------------------------------------
        # Course 1: Python 基础编程
        # ---------------------------------------------------------
        python_course = Course(
            name="Python 基础编程",
            description="从零开始学习 Python 编程语言，掌握变量、数据类型、控制流、函数、面向对象编程和异常处理等核心概念。适合零基础入门。",
            subject="programming",
            difficulty=2,
            cover_image="cover-python",  # Using CSS class name instead of actual URL for frontend compatibility
            instructor="AI 助手",
            duration=280,
            is_featured=True,
            is_active=True,
            order_index=1
        )
        db.session.add(python_course)
        db.session.flush()

        python_chapters_data = [
            {
                "chapter_num": 1,
                "title": "Python基础",
                "description": "变量、数据类型、输入输出、运算符、类型转换",
                "content_file": "01_python_basics.md",
                "order_index": 1,
                "language": "python"
            },
            {
                "chapter_num": 2,
                "title": "条件分支与循环",
                "description": "if/elif/else、比较运算符、逻辑运算符、for循环、while循环、break/continue",
                "content_file": "02_conditions_loops.md",
                "order_index": 2,
                "language": "python"
            },
            {
                "chapter_num": 3,
                "title": "函数与方法",
                "description": "函数定义、参数类型、返回值、作用域、内置函数、lambda表达式",
                "content_file": "03_functions_methods.md",
                "order_index": 3,
                "language": "python"
            },
            {
                "chapter_num": 4,
                "title": "列表与字典",
                "description": "列表操作、字典操作、切片、推导式、常用方法",
                "content_file": "04_list_dict.md",
                "order_index": 4,
                "language": "python"
            },
            {
                "chapter_num": 5,
                "title": "类与对象",
                "description": "类定义、构造函数、实例属性、类属性、实例方法",
                "content_file": "05_class_object.md",
                "order_index": 5,
                "language": "python"
            },
            {
                "chapter_num": 6,
                "title": "面向对象编程",
                "description": "封装、继承、多态、super()、魔术方法",
                "content_file": "06_oop.md",
                "order_index": 6,
                "language": "python"
            },
            {
                "chapter_num": 7,
                "title": "异常处理",
                "description": "try/except/finally、raise、自定义异常、断言",
                "content_file": "07_exception.md",
                "order_index": 7,
                "language": "python"
            }
        ]

        python_lesson_map = {} 

        for c_idx, chap_data in enumerate(python_chapters_data):
            chapter = Chapter(
                course_id=python_course.id,
                name=chap_data["title"],
                description=chap_data["description"],
                order_index=c_idx + 1,
                is_active=True
            )
            db.session.add(chapter)
            db.session.flush()

            md_content = load_lesson_markdown(chap_data["content_file"], chap_data["title"])

            lesson = Lesson(
                chapter_id=chapter.id,
                name=chap_data["title"],
                description="",
                content=md_content,
                content_type="markdown",
                duration=45,
                order_index=1,
                is_free=(c_idx == 0), 
                is_active=True
            )
            db.session.add(lesson)
            db.session.flush()
            # store mapping to find later for exercises
            python_lesson_map[chap_data["chapter_num"]] = lesson.id

        exercises_data = [
            # 第1章练习题
            {
                "chapter_num": 1,
                "title": "计算矩形面积",
                "description": "编写程序，输入矩形的长和宽（两个整数，各占一行），计算并输出矩形的面积。\n\n**示例输入：**\n```\n5\n3\n```\n\n**示例输出：**\n```\n15\n```",
                "difficulty": 1,
                "initial_code": "# 输入长和宽\nlength = int(input())\nwidth = int(input())\n\n# 计算面积并输出\n# 在这里编写代码\n",
                "test_cases": json.dumps({
                    "test_type": "output",
                    "cases": [
                        {"input": "5\n3", "expected_output": "15", "description": "测试 5×3"},
                        {"input": "10\n4", "expected_output": "40", "description": "测试 10×4"},
                        {"input": "1\n1", "expected_output": "1", "description": "测试 1×1"}
                    ]
                }),
                "hint": "面积 = 长 × 宽，使用 * 运算符计算乘法",
                "solution": "length = int(input())\nwidth = int(input())\narea = length * width\nprint(area)",
                "exercise_type": "code"
            },
            {
                "chapter_num": 1,
                "title": "温度转换",
                "description": "编写程序，输入摄氏温度（浮点数），转换为华氏温度并输出（保留1位小数）。\n\n转换公式：华氏温度 = 摄氏温度 × 9/5 + 32\n\n**示例输入：**\n```\n100\n```\n\n**示例输出：**\n```\n212.0\n```",
                "difficulty": 1,
                "initial_code": "# 输入摄氏温度\ncelsius = float(input())\n\n# 转换为华氏温度并输出（保留1位小数）\n# 在这里编写代码\n",
                "test_cases": json.dumps({
                    "test_type": "output",
                    "cases": [
                        {"input": "100", "expected_output": "212.0", "description": "测试 100°C"},
                        {"input": "0", "expected_output": "32.0", "description": "测试 0°C"},
                        {"input": "37", "expected_output": "98.6", "description": "测试 37°C"}
                    ]
                }),
                "hint": "使用公式计算，然后用 round(结果, 1) 保留1位小数",
                "solution": "celsius = float(input())\nfahrenheit = celsius * 9/5 + 32\nprint(round(fahrenheit, 1))",
                "exercise_type": "code"
            },
            # 第2章练习题 
            {
                "chapter_num": 2,
                "title": "判断奇偶数",
                "description": "输入一个整数，判断是奇数还是偶数。如果是偶数输出 `even`，否则输出 `odd`。\n\n**示例输入：**\n```\n4\n```\n\n**示例输出：**\n```\neven\n```",
                "difficulty": 1,
                "initial_code": "n = int(input())\n\n# 判断奇偶并输出\n# 在这里编写代码\n",
                "test_cases": json.dumps({
                    "test_type": "output",
                    "cases": [
                        {"input": "4", "expected_output": "even", "description": "测试偶数4"},
                        {"input": "7", "expected_output": "odd", "description": "测试奇数7"},
                        {"input": "0", "expected_output": "even", "description": "测试0"},
                        {"input": "-3", "expected_output": "odd", "description": "测试负奇数"}
                    ]
                }),
                "hint": "使用取余运算符 %，如果 n % 2 == 0 则为偶数",
                "solution": "n = int(input())\nif n % 2 == 0:\n    print('even')\nelse:\n    print('odd')",
                "exercise_type": "code"
            },
            # 第3章练习题
            {
                "chapter_num": 3,
                "title": "计算平方",
                "description": "编写一个函数 `square(n)`，返回n的平方。\n\n**示例：**\n```python\nprint(square(5))  # 输出: 25\nprint(square(-3)) # 输出: 9\n```",
                "difficulty": 1,
                "initial_code": "def square(n):\n    # 返回n的平方\n    pass\n",
                "test_cases": json.dumps({
                    "test_type": "function",
                    "function_name": "square",
                    "function_tests": [
                        {"args": [5], "expected": 25},
                        {"args": [-3], "expected": 9},
                        {"args": [0], "expected": 0},
                        {"args": [10], "expected": 100}
                    ]
                }),
                "hint": "使用 ** 运算符计算幂，或者使用 * 计算乘法",
                "solution": "def square(n):\n    return n ** 2",
                "exercise_type": "code"
            }
        ]

        for ex_data in exercises_data:
            c_num = ex_data.pop("chapter_num")
            mapped_lesson_id = python_lesson_map.get(c_num)
            if not mapped_lesson_id: continue
            
            ex = Exercise(
                lesson_id=mapped_lesson_id,
                **ex_data,
                is_active=True
            )
            db.session.add(ex)

        # ---------------------------------------------------------
        # Course 2: C 语言基础
        # ---------------------------------------------------------
        c_course = Course(
            name="C 语言基础",
            description="系统学习 C 语言的核心概念：数据类型、控制结构、函数、数组和指针，为底层编程和嵌入式开发打下坚实基础。",
            subject="programming",
            difficulty=2,
            cover_image="cover-c",
            instructor="AI 助手",
            duration=320,
            is_featured=False,
            is_active=True,
            order_index=2
        )
        db.session.add(c_course)
        db.session.flush()

        c_chapters_data = [
            {
                "chapter_num": 1,
                "title": "C语言入门",
                "description": "了解C语言的历史、特点，编写第一个Hello World程序，理解编译流程",
                "content_file": "01_c_intro.md",
                "order_index": 1,
                "language": "c"
            },
            {
                "chapter_num": 2,
                "title": "数据类型与变量",
                "description": "学习C语言的基本数据类型（int、float、char），变量声明与初始化，scanf和printf的使用",
                "content_file": "02_data_types.md",
                "order_index": 2,
                "language": "c"
            },
            {
                "chapter_num": 3,
                "title": "运算符与表达式",
                "description": "掌握算术运算符、关系运算符、逻辑运算符和位运算符的使用",
                "content_file": "03_operators.md",
                "order_index": 3,
                "language": "c"
            },
            {
                "chapter_num": 4,
                "title": "条件语句",
                "description": "学习if-else条件判断、switch-case多分支选择结构",
                "content_file": "04_conditions.md",
                "order_index": 4,
                "language": "c"
            },
            {
                "chapter_num": 5,
                "title": "循环结构",
                "description": "掌握for循环、while循环、do-while循环，以及break和continue的使用",
                "content_file": "05_loops.md",
                "order_index": 5,
                "language": "c"
            },
            {
                "chapter_num": 6,
                "title": "数组",
                "description": "学习一维数组、二维数组的声明和使用，字符串处理函数",
                "content_file": "06_arrays.md",
                "order_index": 6,
                "language": "c"
            },
            {
                "chapter_num": 7,
                "title": "函数",
                "description": "学习函数的定义与调用、参数传递、返回值、递归函数和变量作用域",
                "content_file": "07_functions.md",
                "order_index": 7,
                "language": "c"
            },
            {
                "chapter_num": 8,
                "title": "指针基础",
                "description": "理解指针的概念，学习指针的声明、初始化和基本操作，指针与数组的关系",
                "content_file": "08_pointers.md",
                "order_index": 8,
                "language": "c"
            }
        ]

        c_lesson_map = {}

        for c_idx, chap_data in enumerate(c_chapters_data):
            chapter = Chapter(
                course_id=c_course.id,
                name=chap_data["title"],
                description=chap_data["description"],
                order_index=c_idx + 1,
                is_active=True
            )
            db.session.add(chapter)
            db.session.flush()
            md_content = load_lesson_markdown(chap_data["content_file"], chap_data["title"])

            lesson = Lesson(
                chapter_id=chapter.id,
                name=chap_data["title"],
                description="",
                content=md_content,
                content_type="markdown",
                duration=45,
                order_index=1,
                is_free=(c_idx == 0),
                is_active=True
            )
            db.session.add(lesson)
            db.session.flush()
            c_lesson_map[chap_data["chapter_num"]] = lesson.id

        c_exercises_data = [
            # C语言 第一章
            {
                "chapter_num": 1,
                "title": "Hello, C!",
                "description": "编写并运行你的第一个 C 语言程序，输出 `Hello, C Language!`并换行。\n\n**示例输出：**\n```\nHello, C Language!\n```",
                "difficulty": 1,
                "initial_code": "#include <stdio.h>\n\nint main() {\n    // 在这里编写代码\n    \n    return 0;\n}",
                "test_cases": json.dumps({
                    "test_type": "output",
                    "cases": [
                        {"input": "", "expected_output": "Hello, C Language!", "description": "基本输出测试"}
                    ]
                }),
                "hint": "使用 printf 函数输出，不要忘记末尾的分号",
                "solution": "#include <stdio.h>\n\nint main() {\n    printf(\"Hello, C Language!\\n\");\n    return 0;\n}",
                "exercise_type": "code"
            }
        ]

        for ex_data in c_exercises_data:
            c_num = ex_data.pop("chapter_num")
            mapped_lesson_id = c_lesson_map.get(c_num)
            if not mapped_lesson_id: continue
            
            ex = Exercise(
                lesson_id=mapped_lesson_id,
                **ex_data,
                is_active=True
            )
            db.session.add(ex)

        # ---------------------------------------------------------
        # Course 3: Vibe 编程入门
        # ---------------------------------------------------------
        vibe_course = Course(
            name="Vibe 编程入门",
            description="专为零基础学习者设计！不需要记代码，学会用 AI 做出游戏、工具和网站。核心技能：学会跟 AI 说清楚你要什么。",
            subject="programming",
            difficulty=1,
            cover_image="cover-vibe",
            instructor="AI 助手",
            duration=240,
            is_featured=False,
            is_active=True,
            order_index=3
        )
        db.session.add(vibe_course)
        db.session.flush()

        vibe_chapters_data = [
            {
                "chapter_num": 1,
                "title": "AI是你的超级队友",
                "description": "认识AI，了解Vibe Coding理念，体验AI的能力和局限",
                "content_file": "01_vibe_intro.md",
                "order_index": 1,
                "language": "vibe"
            },
            {
                "chapter_num": 2,
                "title": "学会跟AI说话",
                "description": "掌握Prompt技巧，学会清晰表达需求，写出好的提示词",
                "content_file": "02_vibe_prompt.md",
                "order_index": 2,
                "language": "vibe"
            },
            {
                "chapter_num": 3,
                "title": "做一个贪吃蛇游戏",
                "description": "用AI生成第一个可玩的游戏，学习网页基础和代码运行",
                "content_file": "03_vibe_snake.md",
                "order_index": 3,
                "language": "vibe"
            },
            {
                "chapter_num": 4,
                "title": "做一个属于你的小工具",
                "description": "用AI做实用小工具，如番茄钟、单词卡片等",
                "content_file": "04_vibe_tools.md",
                "order_index": 4,
                "language": "vibe"
            },
            {
                "chapter_num": 5,
                "title": "让全世界看到你的作品",
                "description": "学习如何把作品发布到网上，使用GitHub Pages部署",
                "content_file": "05_vibe_website.md",
                "order_index": 5,
                "language": "vibe"
            },
            {
                "chapter_num": 6,
                "title": "当AI出错了怎么办",
                "description": "学习调试技巧，掌握错误排查三板斧",
                "content_file": "06_vibe_debug.md",
                "order_index": 6,
                "language": "vibe"
            },
            {
                "chapter_num": 7,
                "title": "自由创作时间",
                "description": "综合运用所学，独立规划并完成一个创意项目",
                "content_file": "07_vibe_final.md",
                "order_index": 7,
                "language": "vibe"
            },
            {
                "chapter_num": 8,
                "title": "成果展示与总结",
                "description": "展示作品、互相点评、回顾学习成果、展望未来",
                "content_file": "08_vibe_showcase.md",
                "order_index": 8,
                "language": "vibe"
            }
        ]

        for c_idx, chap_data in enumerate(vibe_chapters_data):
            chapter = Chapter(
                course_id=vibe_course.id,
                name=chap_data["title"],
                description=chap_data["description"],
                order_index=c_idx + 1,
                is_active=True
            )
            db.session.add(chapter)
            db.session.flush()
            md_content = load_lesson_markdown(chap_data["content_file"], chap_data["title"])

            lesson = Lesson(
                chapter_id=chapter.id,
                name=chap_data["title"],
                description="",
                content=md_content,
                content_type="markdown",
                duration=45,
                order_index=1,
                is_free=(c_idx == 0),
                is_active=True
            )
            db.session.add(lesson)

        try:
            db.session.commit()
            print("Successfully seeded courses, chapters, lessons, and exercises!")
        except Exception as e:
            db.session.rollback()
            print("Failed to seed courses. Rolling back.")
            traceback.print_exc()

if __name__ == "__main__":
    seed_courses()

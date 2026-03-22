from app.core.tools.jwc.client import Grade, ClassEntry


def test_grade_dataclass():
    grade = Grade(
        term="2024-2025-1",
        course_name="高等数学",
        score="95",
        credit="4.0",
        attribute="必修",
        nature="考试"
    )
    assert grade.term == "2024-2025-1"
    assert grade.score == "95"


def test_class_entry_dataclass():
    entry = ClassEntry(
        course_name="数据结构",
        teacher="张三",
        weeks="1-16",
        place="教学楼A101",
        day_of_week="周一",
        time_of_day="1-2节"
    )
    assert entry.course_name == "数据结构"

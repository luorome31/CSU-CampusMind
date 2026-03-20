"""
LangChain Tools 封装 - 教务系统查询
"""
import logging
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.core.session.factory import get_session_manager
from app.core.session.manager import UnifiedSessionManager
from .service import JwcService, Grade, ClassEntry, RankEntry, LevelExamEntry

logger = logging.getLogger(__name__)

# 全局 SessionManager 实例（后续可注入）
_session_manager: Optional[UnifiedSessionManager] = None


def set_session_manager(manager: UnifiedSessionManager):
    """设置全局 SessionManager"""
    global _session_manager
    _session_manager = manager


def get_session_manager() -> UnifiedSessionManager:
    """获取全局 SessionManager"""
    if _session_manager is None:
        # 尝试从 factory 模块获取
        from app.core.session.factory import get_session_manager as factory_get
        return factory_get()
    return _session_manager


# ============ Tool Input Models ============

def _get_default_user_id() -> str:
    """从配置获取默认 user_id"""
    from app.config import settings
    return settings.cas_username or ""


class GradeInput(BaseModel):
    user_id: str = Field(default_factory=_get_default_user_id, description="用户 ID (学号)")
    term: str = Field(default="", description="学期，如 '2024-2025-1'，为空则查询全部")


class ScheduleInput(BaseModel):
    user_id: str = Field(default_factory=_get_default_user_id, description="用户 ID (学号)")
    term: str = Field(description="学期，如 '2024-2025-1'")
    week: str = Field(default="0", description="周次，'0' 为全部周")


class RankInput(BaseModel):
    user_id: str = Field(default_factory=_get_default_user_id, description="用户 ID (学号)")


class LevelExamInput(BaseModel):
    user_id: str = Field(default_factory=_get_default_user_id, description="用户 ID (学号)")


# ============ Tool Functions ============
async def _get_jwc_service() -> JwcService:
    """获取 JwcService 实例"""
    return JwcService(get_session_manager())


def _format_grades(grades: list[Grade]) -> str:
    """格式化成绩为字符串"""
    if not grades:
        return "未查询到成绩记录"

    lines = ["## 成绩查询结果\n"]
    lines.append(f"| 学期 | 课程名称 | 成绩 | 学分 | 课程属性 | 课程性质 |")
    lines.append(f"|------|----------|------|------|----------|----------|")

    for g in grades:
        lines.append(f"| {g.term} | {g.course_name} | {g.score} | {g.credit} | {g.attribute} | {g.nature} |")

    return "\n".join(lines)


async def _get_grades(user_id: str, term: str = "") -> str:
    """查询成绩"""
    try:
        service = _get_jwc_service()
        grades = await service.get_grades(user_id, term)
        return _format_grades(grades)
    except Exception as e:
        logger.error(f"成绩查询失败: {e}")
        return f"成绩查询失败: {str(e)}"


def _format_schedule(classes: list[ClassEntry]) -> str:
    """格式化课表为字符串"""
    if not classes:
        return "未查询到课表记录"

    lines = ["## 课表查询结果\n"]
    lines.append(f"| 课程名称 | 教师 | 周次 | 地点 | 星期 | 节次 |")
    lines.append(f"|----------|------|------|------|------|------|")

    for c in classes:
        lines.append(f"| {c.course_name} | {c.teacher} | {c.weeks} | {c.place} | {c.day_of_week} | {c.time_of_day} |")

    return "\n".join(lines)


async def _get_schedule(user_id: str, term: str, week: str = "0") -> str:
    """查询课表"""
    try:
        service = _get_jwc_service()
        classes, start_week_day = await service.get_schedule(user_id, term, week)
        result = _format_schedule(classes)
        # 如果有开始日期信息，附加到结果中
        if start_week_day:
            result += f"\n\n> 学期第1周开始于: {start_week_day}日"
        return result
    except Exception as e:
        logger.error(f"课表查询失败: {e}")
        return f"课表查询失败: {str(e)}"


def _format_ranks(ranks: list[RankEntry]) -> str:
    """格式化排名为字符串"""
    if not ranks:
        return "未查询到排名记录"

    lines = ["## 专业排名结果\n"]
    lines.append(f"| 学期 | 总分 | 班级排名 | 平均分 |")
    lines.append(f"|------|------|----------|--------|")

    for r in ranks:
        lines.append(f"| {r.term} | {r.total_score} | {r.class_rank} | {r.average_score} |")

    return "\n".join(lines)


async def _get_rank(user_id: str) -> str:
    """查询专业排名"""
    try:
        service = _get_jwc_service()
        ranks = await service.get_rank(user_id)
        return _format_ranks(ranks)
    except Exception as e:
        logger.error(f"排名查询失败: {e}")
        return f"排名查询失败: {str(e)}"


def _format_level_exams(exams: list[LevelExamEntry]) -> str:
    """格式化等级考试为字符串"""
    if not exams:
        return "未查询到等级考试记录"

    lines = ["## 等级考试成绩\n"]
    lines.append(f"| 科目 | 笔试成绩 | 机试成绩 | 总分 | 笔试等级 | 机试等级 | 总等级 | 考试日期 |")
    lines.append(f"|------|----------|----------|------|----------|----------|--------|----------|")

    for e in exams:
        lines.append(f"| {e.course} | {e.written_score} | {e.computer_score} | {e.total_score} | {e.written_level} | {e.computer_level} | {e.total_level} | {e.exam_date} |")

    return "\n".join(lines)


async def _get_level_exams(user_id: str) -> str:
    """查询等级考试成绩"""
    try:
        service = _get_jwc_service()
        exams = await service.get_level_exams(user_id)
        return _format_level_exams(exams)
    except Exception as e:
        logger.error(f"等级考试查询失败: {e}")
        return f"等级考试查询失败: {str(e)}"


# ============ LangChain Tools ============
JwcGradeTool = StructuredTool.from_function(
    func=_get_grades,
    name="jwc_grade",
    description="查询学生的考试成绩。需要提供用户 ID（学号）和可选的学期参数。",
    args_schema=GradeInput,
)

JwcScheduleTool = StructuredTool.from_function(
    func=_get_schedule,
    name="jwc_schedule",
    description="查询学生的课表。需要提供用户 ID（学号）、学期和周次。",
    args_schema=ScheduleInput,
)

JwcRankTool = StructuredTool.from_function(
    func=_get_rank,
    name="jwc_rank",
    description="查询学生的专业排名。需要提供用户 ID（学号）。",
    args_schema=RankInput,
)

JwcLevelExamTool = StructuredTool.from_function(
    func=_get_level_exams,
    name="jwc_level_exam",
    description="查询学生的等级考试成绩（如英语四六级、计算机等级考试等）。需要提供用户 ID（学号）。",
    args_schema=LevelExamInput,
)


# 工具列表
JWC_TOOLS = [
    JwcGradeTool,
    JwcScheduleTool,
    JwcRankTool,
    JwcLevelExamTool,
]


# ============ Factory Function ============
from typing import List
from langchain_core.tools import BaseTool
from app.core.context import ToolContext


def create_jwc_tools(ctx: ToolContext) -> List[BaseTool]:
    """
    创建 JWC 工具（依赖 ToolContext，利用闭包隐藏 user_id）

    Args:
        ctx: 工具运行时上下文，包含用户身份和会话管理

    Returns:
        JWC 相关工具列表
    """
    # 获取 JwcService 实例（使用 ctx 的 session_manager）
    session_manager = ctx.session_manager

    def _get_jwc_service_factory() -> "JwcService":
        """获取 JwcService 实例"""
        from app.core.session.manager import UnifiedSessionManager
        return JwcService(session_manager)

    def _get_grades(term: str = "") -> str:
        """查询教务处成绩"""
        if not ctx.is_authenticated:
            return "请先登录后再查询成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = _get_jwc_service_factory()
            grades = service.get_grades(ctx.user_id, term)
            return _format_grades(grades)
        except Exception as e:
            logger.error(f"成绩查询失败: {e}")
            return f"成绩查询失败: {str(e)}"

    def _get_schedule(term: str, week: str = "0") -> str:
        """查询教务处课表"""
        if not ctx.is_authenticated:
            return "请先登录后再查询课表"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = _get_jwc_service_factory()
            classes, start_week_day = service.get_schedule(ctx.user_id, term, week)
            result = _format_schedule(classes)
            if start_week_day:
                result += f"\n\n> 学期第1周开始于: {start_week_day}日"
            return result
        except Exception as e:
            logger.error(f"课表查询失败: {e}")
            return f"课表查询失败: {str(e)}"

    def _get_rank() -> str:
        """查询专业排名"""
        if not ctx.is_authenticated:
            return "请先登录后再查询排名"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = _get_jwc_service_factory()
            ranks = service.get_rank(ctx.user_id)
            return _format_ranks(ranks)
        except Exception as e:
            logger.error(f"排名查询失败: {e}")
            return f"排名查询失败: {str(e)}"

    def _get_level_exams() -> str:
        """查询等级考试成绩"""
        if not ctx.is_authenticated:
            return "请先登录后再查询等级考试成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = _get_jwc_service_factory()
            exams = service.get_level_exams(ctx.user_id)
            return _format_level_exams(exams)
        except Exception as e:
            logger.error(f"等级考试查询失败: {e}")
            return f"等级考试查询失败: {str(e)}"

    return [
        StructuredTool.from_function(
            func=_get_grades,
            name="jwc_grade",
            description="查询学生的考试成绩。参数：term（学期，如 '2024-2025-1'），不传则查询所有学期成绩。"
        ),
        StructuredTool.from_function(
            func=_get_schedule,
            name="jwc_schedule",
            description="查询学生的课表。参数：term（学期，必填，如 '2024-2025-1'），week（周次，可选，'0' 为全部周）。"
        ),
        StructuredTool.from_function(
            func=_get_rank,
            name="jwc_rank",
            description="查询学生的专业排名。不需要额外参数。"
        ),
        StructuredTool.from_function(
            func=_get_level_exams,
            name="jwc_level_exam",
            description="查询学生的等级考试成绩（如英语四六级、计算机等级考试等）。不需要额外参数。"
        ),
    ]

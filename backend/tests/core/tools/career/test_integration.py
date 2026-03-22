"""
就业指导中心集成测试

运行方式:
    uv run pytest tests/core/tools/career/test_integration.py -v -m integration

注意: 需要网络连接，会发起真实HTTP请求
"""
import pytest

pytestmark = pytest.mark.integration


class TestRealAPI:
    """真实API测试（可选）"""

    def test_teachin_real(self):
        """测试真实宣讲会接口"""
        from app.core.tools.career import CareerService
        service = CareerService()
        result = service.get_teachin()

        # Check for table format or "empty" message
        assert "宣讲会查询" in result or "公司名称" in result or "为空" in result

    def test_jobfair_real(self):
        """测试真实招聘会接口"""
        from app.core.tools.career import CareerService
        service = CareerService()
        result = service.get_jobfair()

        # Check for table format or "empty" message
        assert "招聘会" in result or "招聘公告" in result or "为空" in result

    def test_campus_recruit_real(self):
        """测试真实校园招聘接口"""
        from app.core.tools.career import CareerService
        service = CareerService()
        result = service.get_campus_recruit()

        # Check for table format or "empty" message
        assert "校园招聘" in result or "招聘公告" in result or "为空" in result

    def test_campus_intern_real(self):
        """测试真实实习接口"""
        from app.core.tools.career import CareerService
        service = CareerService()
        result = service.get_campus_intern()

        # Check for table format or "empty" message
        assert "实习" in result or "岗位" in result or "为空" in result
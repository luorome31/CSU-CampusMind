"""
就业指导中心集成测试

运行方式:
    uv run pytest tests/core/tools/jwc_career/test_integration.py -v -m integration

注意: 需要网络连接，会发起真实HTTP请求
"""
import pytest

pytestmark = pytest.mark.integration


class TestRealAPI:
    """真实API测试（可选）"""

    def test_teachin_real(self):
        """测试真实宣讲会接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_teachin()

        assert "## 宣讲会查询结果" in result or "宣讲会查询" in result

    def test_jobfair_real(self):
        """测试真实招聘会接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_jobfair()

        assert "## 大型招聘会信息" in result or "招聘会查询" in result

    def test_campus_recruit_real(self):
        """测试真实校园招聘接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_campus_recruit()

        assert "## 校园招聘信息" in result or "校园招聘查询" in result

    def test_campus_intern_real(self):
        """测试真实实习接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_campus_intern()

        assert "## 实习岗位信息" in result or "实习信息查询" in result
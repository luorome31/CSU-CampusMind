# backend/tests/core/session/test_oa_notification.py
"""
Tests for OANotificationList tool components.

Tests DepartmentEnum and build_params function.
"""
import base64
import json


class TestBuildParams:
    """Tests for build_params() function."""

    def test_build_params_with_all_fields(self):
        """build_params should encode all search fields correctly."""
        from app.core.tools.oa.departments import build_params

        result = build_params(
            qssj="2024-03-12",
            jssj="2024-12-31",
            qcbmmc="学校办公室",
            wjbt="通知",
            qwss="印发",
            hid_odby="DJSJP DESC"
        )

        parsed = json.loads(result)
        assert parsed["tableName"] == "ZNDX_ZHBG_GGTZ"
        assert parsed["pxzd"] == "DJSJP DESC"

        # Decode the base64-encoded SQL condition
        tjnr = parsed["tjnr"]
        decoded = base64.b64decode(tjnr).decode("utf-8")

        assert "DJSJP >= to_date('2024-03-12" in decoded
        assert "DJSJP <= to_date('2024-12-31" in decoded
        assert "QCBMMC like '%学校办公室%'" in decoded
        assert "WJBT LIKE '%通知%'" in decoded
        assert "QWSS LIKE '%印发%'" in decoded

    def test_build_params_empty_fields(self):
        """build_params with no fields should return empty conditions."""
        from app.core.tools.oa.departments import build_params

        result = build_params()
        parsed = json.loads(result)

        assert parsed["tableName"] == "ZNDX_ZHBG_GGTZ"
        assert parsed["tjnr"] == ""  # empty string when no conditions
        assert parsed["pxzd"] == ""

    def test_build_params_partial_fields(self):
        """build_params with only wjbt should only include that condition."""
        from app.core.tools.oa.departments import build_params

        result = build_params(wjbt="放假")
        parsed = json.loads(result)

        decoded = base64.b64decode(parsed["tjnr"]).decode("utf-8")
        assert "WJBT LIKE '%放假%'" in decoded
        # Should NOT contain other conditions
        assert "QCBMMC" not in decoded
        assert "QWSS" not in decoded
        assert "DJSJP" not in decoded

    def test_build_params_only_qcbmmc(self):
        """build_params with only department should only include that condition."""
        from app.core.tools.oa.departments import build_params

        result = build_params(qcbmmc="人事处")
        parsed = json.loads(result)

        decoded = base64.b64decode(parsed["tjnr"]).decode("utf-8")
        assert "QCBMMC like '%人事处%'" in decoded
        assert "DJSJP" not in decoded
        assert "WJBT" not in decoded

    def test_build_params_time_range_only(self):
        """build_params with only time range should only include DJSJP conditions."""
        from app.core.tools.oa.departments import build_params

        result = build_params(qssj="2024-01-01", jssj="2024-06-30")
        parsed = json.loads(result)

        decoded = base64.b64decode(parsed["tjnr"]).decode("utf-8")
        assert "DJSJP >= to_date('2024-01-01" in decoded
        assert "DJSJP <= to_date('2024-06-30" in decoded
        assert "QCBMMC" not in decoded
        assert "WJBT" not in decoded


class TestDepartmentEnum:
    """Tests for DepartmentEnum."""

    def test_department_enum_has_school_office(self):
        """DepartmentEnum should have SCHOOL_OFFICE with correct value."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "SCHOOL_OFFICE")
        assert DepartmentEnum.SCHOOL_OFFICE.value == "学校办公室"

    def test_department_enum_has_personnel_division(self):
        """DepartmentEnum should have PERSONNEL_DIVISION with correct value."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "PERSONNEL_DIVISION")
        assert DepartmentEnum.PERSONNEL_DIVISION.value == "人事处"

    def test_department_enum_all_values_are_strings(self):
        """All DepartmentEnum values should be non-empty strings."""
        from app.core.tools.oa.departments import DepartmentEnum

        for member_name in DepartmentEnum._values:
            member = getattr(DepartmentEnum, member_name)
            assert isinstance(member.value, str), f"{member_name} value is not a string"
            assert len(member.value) > 0, f"{member_name} value is empty"

    def test_department_enum_has_undergraduate_college(self):
        """DepartmentEnum should have UNDERGRADUATE_COLLEGE."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "UNDERGRADUATE_COLLEGE")
        assert DepartmentEnum.UNDERGRADUATE_COLLEGE.value == "本科生院"

    def test_department_enum_has_graduate_school(self):
        """DepartmentEnum should have GRADUATE_SCHOOL."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "GRADUATE_SCHOOL")
        assert DepartmentEnum.GRADUATE_SCHOOL.value == "研究生院"

    def test_department_enum_has_library(self):
        """DepartmentEnum should have LIBRARY."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "LIBRARY")
        assert DepartmentEnum.LIBRARY.value == "图书馆"

    def test_department_enum_has_research_division(self):
        """DepartmentEnum should have RESEARCH_DIVISION."""
        from app.core.tools.oa.departments import DepartmentEnum

        assert hasattr(DepartmentEnum, "RESEARCH_DIVISION")
        assert DepartmentEnum.RESEARCH_DIVISION.value == "科学研究部"

    def test_department_enum_values_are_exact_chinese_strings(self):
        """DepartmentEnum values should be the exact Chinese department names."""
        from app.core.tools.oa.departments import DepartmentEnum

        # Key departments that should have exact values
        expected_values = {
            "SCHOOL_OFFICE": "学校办公室",
            "PERSONNEL_DIVISION": "人事处",
            "UNDERGRADUATE_COLLEGE": "本科生院",
            "GRADUATE_SCHOOL": "研究生院",
            "RESEARCH_DIVISION": "科学研究部",
            "LIBRARY": "图书馆",
        }

        for attr, expected_value in expected_values.items():
            assert hasattr(DepartmentEnum, attr)
            actual = getattr(DepartmentEnum, attr).value
            assert actual == expected_value, f"{attr}: expected '{expected_value}', got '{actual}'"

# backend/app/core/tools/oa/departments.py
"""
部门枚举和查询参数构造

基于中南大学校内办公网前端 JavaScript 代码逆向工程
"""
import base64
import json
from enum import Enum


# === Department Enum ===
# All 80+ departments from the fixed department list
_DEPARTMENT_VALUES = [
    "中共中南大学委员会",
    "中南大学",
    "学校办公室",
    "纪委办公室",
    "党委巡视办",
    "党委组织部",
    "党委宣传部",
    "党委统战部",
    "学生工作部（处）",
    "保卫部（处）",
    "机关及直附属单位党委",
    "校工会",
    "校团委",
    "党委教师工作部",
    "人事处",
    "监察处",
    "计划财务处",
    "本科生院",
    "科学研究部",
    "人文社会科学处",
    "研究生院",
    "发展规划与学科建设处",
    "国内合作处",
    "国际合作与交流处",
    "医院管理处",
    "资产与实验室管理处",
    "房产管理处",
    "审计处",
    "后勤保障部",
    "基建处",
    "离退休工作处",
    "采购与招标管理中心",
    "湘雅医学院",
    "实验动物学部",
    "铁道校区管委会",
    "人文学院",
    "外国语学院",
    "马克思主义学院",
    "公共管理学院",
    "材料科学与工程学院",
    "粉末冶金研究院",
    "冶金与环境学院",
    "地球科学与信息物理学院",
    "体育教研部",
    "信息与网络中心",
    "图书馆",
    "档案馆（校史馆）",
    "继续教育学院",
    "教育发展与校友事务办公室",
    "高等研究中心",
    "出版社",
    "校医院",
    "资产经营有限公司",
    "国际教育学院",
    "第二附属中学",
    "第一附属小学",
    "第二附属小学",
    "其他单位",
    "\"双一流\"建设办公室",
    "创新创业指导中心",
    "创新与创业教育办公室",
    "党校",
    "档案馆",
    "档案馆 (校史馆)",
    "发展与联络办公室（教育基金会、校友总会）",
    "国际合作与交流处、学校保密办公室",
    "后勤管理处",
    "后勤集团",
    "基础医学院",
    "计划财务处、信息与网络中心",
    "科学研究部、人文社科处",
    "普教管理服务中心",
    "人事处  计划财务处",
    "图书馆      学工部",
    "文学与新闻传播学院",
    "校办产业管理办公室",
    "校级奖励金委员会",
    "信息安全与大数据研究院",
    "信息科学与工程学院",
    "学生工作部",
    "研究生工作部（处）",
    "研究生院、国际合作与交流处",
    "职工医院",
    "资产管理处",
]


# Key department name to identifier mappings (uppercase for enum member names)
_KEY_DEPT_MAPPINGS = {
    "学校办公室": "SCHOOL_OFFICE",
    "人事处": "PERSONNEL_DIVISION",
    "本科生院": "UNDERGRADUATE_COLLEGE",
    "研究生院": "GRADUATE_SCHOOL",
    "科学研究部": "RESEARCH_DIVISION",
    "图书馆": "LIBRARY",
    "纪委办公室": "DISCIPLINE_INSPECTION_OFFICE",
    "党委组织部": "PARTY_ORGANIZATION_DEPARTMENT",
    "党委宣传部": "PROPAGANDA_DEPARTMENT",
    "党委统战部": "UNITED_FRONT_WORK_DEPARTMENT",
    "学生工作部（处）": "STUDENT_AFFAIRS_DEPARTMENT",
    "保卫部（处）": "SECURITY_DEPARTMENT",
    "校工会": "LABOR_UNION",
    "校团委": "YOUTH_LEAGUE_COMMITTEE",
    "党委教师工作部": "TEACHER_WORK_DEPARTMENT",
    "监察处": "SUPERVISION_DIVISION",
    "计划财务处": "PLANNING_FINANCE_DIVISION",
    "人文社会科学处": "HUMANITIES_SOCIAL_SCIENCES_DIVISION",
    "发展规划与学科建设处": "DEVELOPMENT_PLANNING_DIVISION",
    "国内合作处": "DOMESTIC_COOPERATION_DIVISION",
    "国际合作与交流处": "INTERNATIONAL_COOPERATION_DIVISION",
    "医院管理处": "HOSPITAL_ADMINISTRATION_DIVISION",
    "资产与实验室管理处": "ASSETS_LABORATORY_MANAGEMENT_DIVISION",
    "房产管理处": "REAL_ESTATE_MANAGEMENT_DIVISION",
    "审计处": "AUDIT_DIVISION",
    "后勤保障部": "LOGISTICS_SUPPORT_DIVISION",
    "基建处": "INFRASTRUCTURE_CONSTRUCTION_DIVISION",
    "离退休工作处": "RETIRED_WORKERS_DIVISION",
    "采购与招标管理中心": "PROCUREMENT_BIDDING_MANAGEMENT_CENTER",
    "湘雅医学院": "XIANGYA_MEDICAL_COLLEGE",
    "实验动物学部": "LABORATORY_ANIMAL_DIVISION",
    "铁道校区管委会": "RAILWAY_CAMPUS_MANAGEMENT_COMMITTEE",
    "人文学院": "SCHOOL_OF_HUMANITIES",
    "外国语学院": "SCHOOL_OF_FOREIGN_LANGUAGES",
    "马克思主义学院": "SCHOOL_OF_MARXISM",
    "公共管理学院": "SCHOOL_OF_PUBLIC_ADMINISTRATION",
    "材料科学与工程学院": "SCHOOL_OF_MATERIALS_SCIENCE_ENGINEERING",
    "粉末冶金研究院": "POWDER_METALLURGY_RESEARCH_INSTITUTE",
    "冶金与环境学院": "SCHOOL_OF_METALLURGY_ENVIRONMENT",
    "地球科学与信息物理学院": "SCHOOL_OF_EARTH_SCIENCES_INFO_PHYSICS",
    "体育教研部": "PHYSICAL_EDUCATION_TEACHING_DIVISION",
    "信息与网络中心": "INFO_NETWORK_CENTER",
    "档案馆（校史馆）": "ARCHIVES_MUSEUM",
    "继续教育学院": "CONTINUING_EDUCATION_COLLEGE",
    "教育发展与校友事务办公室": "EDUCATION_DEVELOPMENT_ALUMNI_AFFAIRS_OFFICE",
    "高等研究中心": "ADVANCED_RESEARCH_CENTER",
    "出版社": "UNIVERSITY_PRESS",
    "校医院": "UNIVERSITY_HOSPITAL",
    "资产经营有限公司": "ASSET_MANAGEMENT_COMPANY",
    "国际教育学院": "INTERNATIONAL_EDUCATION_COLLEGE",
    "第二附属中学": "SECOND_AFFILIATED_MIDDLE_SCHOOL",
    "第一附属小学": "FIRST_AFFILIATED_PRIMARY_SCHOOL",
    "第二附属小学": "SECOND_AFFILIATED_PRIMARY_SCHOOL",
    "其他单位": "OTHER_UNITS",
    "\"双一流\"建设办公室": "DOUBLE_FIRST_CLASS_CONSTRUCTION_OFFICE",
    "创新创业指导中心": "INNOVATION_ENTREPRENEURSHIP_GUIDANCE_CENTER",
    "创新与创业教育办公室": "INNOVATION_ENTREPRENEURSHIP_EDUCATION_OFFICE",
    "党校": "PARTY_SCHOOL",
    "档案馆": "ARCHIVES",
    "档案馆 (校史馆)": "ARCHIVES_MUSEUM_2",
    "发展与联络办公室（教育基金会、校友总会）": "DEVELOPMENT_LIAISON_OFFICE",
    "国际合作与交流处、学校保密办公室": "INTERNATIONAL_COOPERATION_SECRETARY_OFFICE",
    "后勤管理处": "LOGISTICS_MANAGEMENT_DIVISION",
    "后勤集团": "LOGISTICS_GROUP",
    "基础医学院": "SCHOOL_OF_BASIC_MEDICAL_SCIENCES",
    "计划财务处、信息与网络中心": "PLANNING_FINANCE_INFO_CENTER",
    "科学研究部、人文社科处": "RESEARCH_HUMANITIES_SOCIAL_DIVISION",
    "普教管理服务中心": "GENERAL_EDUCATION_MANAGEMENT_SERVICE_CENTER",
    "人事处  计划财务处": "PERSONNEL_PLANNING_FINANCE",
    "图书馆      学工部": "LIBRARY_STUDENT_AFFAIRS",
    "文学与新闻传播学院": "SCHOOL_OF_LITERATURE_JOURNALISM",
    "校办产业管理办公室": "UNIVERSITY_INDUSTRY_MANAGEMENT_OFFICE",
    "校级奖励金委员会": "UNIVERSITY_LEVEL_AWARD_COMMITTEE",
    "信息安全与大数据研究院": "INFO_SECURITY_BIG_DATA_INSTITUTE",
    "信息科学与工程学院": "SCHOOL_OF_INFO_SCIENCE_ENGINEERING",
    "学生工作部": "STUDENT_AFFAIRS_DIVISION",
    "研究生工作部（处）": "GRADUATE_STUDENT_AFFAIRS_DIVISION",
    "研究生院、国际合作与交流处": "GRADUATE_SCHOOL_INTERNATIONAL_DIVISION",
    "职工医院": "STAFF_HOSPITAL",
    "资产管理处": "ASSET_MANAGEMENT_DIVISION",
}


def _get_identifier(dept_name: str) -> str:
    """Get Python identifier for a department name."""
    if dept_name in _KEY_DEPT_MAPPINGS:
        return _KEY_DEPT_MAPPINGS[dept_name]
    # For other departments, use a simple transformation
    result = dept_name
    result = result.replace("（", "_").replace("）", "")
    result = result.replace("(", "_").replace(")", "")
    result = result.replace(" ", "_").replace(",", "_")
    result = result.replace("'", "").replace(""", "").replace(""", "")
    # Remove consecutive underscores
    while "__" in result:
        result = result.replace("__", "_")
    return result.upper()


# === DepartmentEnum using standard Enum ===
# Build enum members dict with proper identifiers
_dept_members = {_get_identifier(d): d for d in _DEPARTMENT_VALUES}

# Create DepartmentEnum using functional API with str mixin
# Using StrEnum would be cleaner but functional API creates it differently
DepartmentEnum = Enum(
    'DepartmentEnum',
    {ident: dept_name for ident, dept_name in _dept_members.items()},
    type=str,
    module=__name__,
)

# Add _values for backward compatibility (used by tests)
DepartmentEnum._values = _dept_members


# === Query Parameter Builder ===

def build_params(
    qssj: str = "",
    jssj: str = "",
    qcbmmc: str = "",
    wjbt: str = "",
    qwss: str = "",
    hid_odby: str = "",
) -> str:
    """
    构造校内通知查询的 params 参数（JSON 字符串）

    Args:
        qssj: 起始时间 YYYY-MM-DD
        jssj: 结束时间 YYYY-MM-DD
        qcbmmc: 起草部门名称（模糊匹配）
        wjbt: 文件标题关键词（模糊匹配）
        qwss: 全文搜索关键词
        hid_odby: 排序字段，如 "DJSJP DESC"

    Returns:
        JSON 字符串，可直接作为 params 表单参数使用
    """
    # 1. 拼接高级搜索条件
    gjssCXTJ = ""
    if qssj:
        gjssCXTJ += f" and DJSJP >= to_date('{qssj} 00:00:00','yyyy-mm-dd hh24:mi:ss') "
    if jssj:
        gjssCXTJ += f" and DJSJP <= to_date('{jssj} 23:59:59','yyyy-mm-dd hh24:mi:ss')"
    if qcbmmc:
        gjssCXTJ += f" and QCBMMC like '%{qcbmmc}%' "
    if wjbt:
        gjssCXTJ += f" and WJBT LIKE '%{wjbt}%'  "
    if qwss:
        gjssCXTJ += f" and QWSS LIKE '%{qwss}%' "

    # 2. Base64 编码
    tjnr_encoded = base64.b64encode(gjssCXTJ.encode("utf-8")).decode("utf-8")

    # 3. 构造参数字典（tableName 硬编码，不暴露给 LLM）
    params_dict = {
        "tableName": "ZNDX_ZHBG_GGTZ",  # 校内通知固定表名
        "tjnr": tjnr_encoded,
        "pxzd": hid_odby,
    }

    # 4. 转换为紧凑 JSON 字符串
    return json.dumps(params_dict, separators=(",", ":"), ensure_ascii=False)
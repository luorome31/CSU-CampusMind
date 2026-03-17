"""
数据模型 - 图书馆搜索
"""
from typing import Optional
from pydantic import BaseModel, Field


class LibraryBookItem(BaseModel):
    """图书基本信息"""
    record_id: int = Field(..., description="记录ID，用于查询复本位置")
    title: str = Field(..., description="书名")
    author: Optional[str] = Field(None, description="作者")
    publisher: Optional[str] = Field(None, description="出版社")
    isbns: list[str] = Field(default_factory=list, description="ISBN 数组")
    publish_year: Optional[str] = Field(None, description="出版年")
    call_no: list[str] = Field(default_factory=list, description="索书号数组")
    doc_name: Optional[str] = Field(None, description="文献类型")
    physical_count: int = Field(0, description="馆藏册数")
    on_shelf_count: int = Field(0, description="在架册数")
    language: Optional[str] = Field(None, description="语言代码")
    country: Optional[str] = Field(None, description="国家代码")
    subjects: Optional[str] = Field(None, description="主题词")
    abstract: Optional[str] = Field(None, description="摘要")


class LibraryBookSearchResult(BaseModel):
    """图书搜索结果"""
    total: int = Field(..., description="搜索结果总数")
    items: list[LibraryBookItem] = Field(default_factory=list, description="图书列表")


class LibraryBookItemCopy(BaseModel):
    """单本复本信息"""
    item_id: int = Field(..., description="复本ID")
    call_no: str = Field(..., description="索书号,用于索引书架上书本的位置")
    barcode: Optional[str] = Field(None, description="条码号")
    lib_code: Optional[str] = Field(None, description="馆代码")
    lib_name: Optional[str] = Field(None, description="馆名称")
    location_id: Optional[int] = Field(None, description="位置ID")
    location_name: Optional[str] = Field(None, description="位置名称")
    cur_location_id: Optional[int] = Field(None, description="当前所在位置ID")
    cur_location_name: Optional[str] = Field(None, description="当前所在位置名称")
    vol: Optional[str] = Field(None, description="卷册信息")
    in_date: Optional[str] = Field(None, description="入藏日期")
    process_type: Optional[str] = Field(None, description="处理类型/借阅状态")
    item_policy_name: Optional[str] = Field(None, description="流通规则名称")
    shelf_no: Optional[str] = Field(None, description="架位号")


class LibraryBookItemCopiesResult(BaseModel):
    """复本列表结果"""
    total: int = Field(..., description="总数")
    items: list[LibraryBookItemCopy] = Field(default_factory=list, description="复本列表")

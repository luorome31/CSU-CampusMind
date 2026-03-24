# 图书馆工具

查询中南大学图书馆馆藏图书。

## 工具列表

### library_search - 图书搜索

搜索图书馆馆藏图书。

**参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| keywords | string | 是 | 搜索关键词（建议 3 字以内） |
| page | int | 否 | 页码，默认 1 |
| rows | int | 否 | 每页数量，默认 10 |

**返回格式:**

```markdown
共找到 5 条结果：

--- 第 1 条 ---
📚 书名: 人工智能：一种现代方法
👤 作者: Stuart Russell
🏢 出版社: 人民邮电出版社
📅 出版年: 2018
📖 ISBN: 9787115484678
🔖 索书号: TP18/R832
📊 馆藏: 5 册 / 在架: 3 册
🔑 Record ID: 123456
```

---

### library_get_book_location - 图书位置查询

查询图书的馆藏位置和可借状态。

**参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| record_id | int | 是 | 图书记录 ID（来自搜索结果） |

**返回格式:**

```markdown
共 3 个复本：

--- 复本 1 ---
📍 馆: 校本部馆
📍 位置: 社科图书阅览室
🔖 索书号: TP18/R832
🏷️ 条码号: 31125087654
📦 架位号: A-15-3
📌 状态: ✅ 在架
📅 入藏日期: 2020-05-01

--- 复本 2 ---
📍 馆: 校本部馆
📍 位置: 社科图书借阅室
🔖 索书号: TP18/R832
📌 状态: ❌ 已借出
```

---

## 认证要求

**需要登录**: 否

图书馆工具是公开的，所有用户都可以使用，无需登录。

---

## 服务类

```python
class LibraryService:
    def search(self, keywords: str, page: int = 1, rows: int = 10) -> LibraryBookSearchResult:
        """搜索图书"""
        ...

    def get_book_copies(self, record_id: int) -> LibraryBookItemCopiesResult:
        """获取图书复本位置"""
        ...
```

---

## 数据模型

### LibraryBookSearchResult

```python
class LibraryBookSearchResult(BaseModel):
    total: int
    items: List[LibraryBookItem]

class LibraryBookItem(BaseModel):
    record_id: int
    title: str
    author: Optional[str]
    publisher: Optional[str]
    publish_year: Optional[str]
    isbns: List[str]
    call_no: List[str]
    physical_count: int      # 馆藏复本数
    on_shelf_count: int      # 在架复本数
```

### LibraryBookItemCopiesResult

```python
class LibraryBookItemCopiesResult(BaseModel):
    total: int
    items: List[LibraryBookCopy]

class LibraryBookCopy(BaseModel):
    lib_name: Optional[str]      # 馆名称
    location_name: Optional[str] # 馆藏地
    cur_location_name: Optional[str]
    call_no: str                 # 索书号
    barcode: Optional[str]      # 条码号
    shelf_no: Optional[str]     # 架位号
    process_type: str            # 在架/已借出
    in_date: Optional[str]      # 入藏日期
```

"""
Library Service - 封装图书馆 API 调用
"""
import json
import logging
import requests
from typing import Optional
from .models import (
    LibraryBookSearchResult,
    LibraryBookItem,
    LibraryBookItemCopiesResult,
    LibraryBookItemCopy,
)

logger = logging.getLogger(__name__)

# API 配置
SEARCH_URL = "https://opac.lib.csu.edu.cn/find/unify/advancedSearch"
LOCATION_URL = "https://opac.lib.csu.edu.cn/find/physical/groupitems"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "mappingPath": "",
    "groupCode": "800388",
    "sec-ch-ua-mobile": "?0",
    "x-lang": "CHI",
    "Content-Type": "application/json;charset=UTF-8",
    "content-language": "zh_CN",
    "Origin": "https://opac.lib.csu.edu.cn",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://opac.lib.csu.edu.cn/",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


class LibraryService:
    """图书馆服务"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search(self, keywords: str, page: int = 1, rows: int = 10) -> LibraryBookSearchResult:
        """
        搜索图书馆馆藏

        Args:
            keywords: 搜索关键词
            page: 页码
            rows: 每页数量

        Returns:
            LibraryBookSearchResult: 搜索结果
        """
        payload = {
            "docCode": [None],
            "litCode": [],
            "matchMode": "2",
            "resourceType": [],
            "subject": [],
            "discode1": [],
            "publisher": [],
            "libCode": [],
            "locationId": [],
            "eCollectionIds": [],
            "neweCollectionIds": [],
            "curLocationId": [],
            "campusId": [],
            "kindNo": [],
            "collectionName": [],
            "author": [],
            "langCode": [],
            "countryCode": [],
            "publishBegin": None,
            "publishEnd": None,
            "coreInclude": [],
            "ddType": [],
            "verifyStatus": [],
            "group": [],
            "sortField": "relevance",
            "sortClause": None,
            "page": page,
            "rows": rows,
            "onlyOnShelf": None,
            "searchItems": [
                {
                    "oper": None,
                    "searchField": "keyWord",
                    "matchMode": "2",
                    "searchFieldContent": keywords
                }
            ],
            "searchFieldContent": "",
            "searchField": "keyWord",
            "searchFieldList": None,
            "isOpen": False
        }

        try:
            response = self.session.post(SEARCH_URL, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.warning(f"Search failed: {data.get('message')}")
                return LibraryBookSearchResult(total=0, items=[])

            search_result = data.get("data", {})
            total = search_result.get("numFound", 0)
            items = []

            for item in search_result.get("searchResult", []):
                items.append(LibraryBookItem(
                    record_id=item.get("recordId", 0),
                    title=item.get("title", ""),
                    author=item.get("author"),
                    publisher=item.get("publisher"),
                    isbns=item.get("isbns", []),
                    publish_year=item.get("publishYear"),
                    call_no=item.get("callNo", []),
                    doc_name=item.get("docName"),
                    physical_count=item.get("physicalCount", 0),
                    on_shelf_count=item.get("onShelfCountI", 0),
                    language=item.get("langCode"),
                    country=item.get("countryCode"),
                    subjects=item.get("subjectWord"),
                    abstract=item.get("adstract"),
                ))

            return LibraryBookSearchResult(total=total, items=items)

        except Exception as e:
            logger.error(f"Library search error: {e}")
            return LibraryBookSearchResult(total=0, items=[])

    def get_book_copies(self, record_id: int) -> LibraryBookItemCopiesResult:
        """
        获取图书复本位置信息

        Args:
            record_id: 图书记录ID

        Returns:
            LibraryBookItemCopiesResult: 复本列表
        """
        payload = {
            "page": 1,
            "rows": 50,
            "entrance": None,
            "recordId": str(record_id),
            "isUnify": True,
            "sortType": 0,
            "callNo": ""
        }

        try:
            response = self.session.post(LOCATION_URL, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.warning(f"Get copies failed: {data.get('message')}")
                return LibraryBookItemCopiesResult(total=0, items=[])

            copies_data = data.get("data", {})
            total = copies_data.get("totalCount", 0)
            items = []

            for item in copies_data.get("list", []):
                items.append(LibraryBookItemCopy(
                    item_id=item.get("itemId", 0),
                    call_no=item.get("callNo", ""),
                    barcode=item.get("barcode"),
                    lib_code=item.get("libCode"),
                    lib_name=item.get("libName"),
                    location_id=item.get("locationId"),
                    location_name=item.get("locationName"),
                    cur_location_id=item.get("curLocationId"),
                    cur_location_name=item.get("curLocationName"),
                    vol=item.get("vol"),
                    in_date=item.get("inDate"),
                    process_type=item.get("processType"),
                    item_policy_name=item.get("itemPolicyName"),
                    shelf_no=item.get("shelfNo"),
                ))

            return LibraryBookItemCopiesResult(total=total, items=items)

        except Exception as e:
            logger.error(f"Library get copies error: {e}")
            return LibraryBookItemCopiesResult(total=0, items=[])


# 全局服务实例
_library_service: Optional[LibraryService] = None


def get_library_service() -> LibraryService:
    """获取全局 LibraryService 实例"""
    global _library_service
    if _library_service is None:
        _library_service = LibraryService()
    return _library_service

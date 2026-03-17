import requests
import json

url = "https://opac.lib.csu.edu.cn/find/unify/advancedSearch"

payload2 = {
  "docCode": [
    None
  ],
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
  "page": 1,
  "rows": 10,
  "onlyOnShelf": None,
  "searchItems": [
    {
      "oper": None,
      "searchField": "keyWord",
      "matchMode": "2",
      "searchFieldContent": "vue"
    },
    {
      "oper": "OR",
      "searchField": "keyWord", # 使用 key word 就足够
      "matchMode": "2",# 一是完全匹配二是模糊匹配
      "searchFieldContent": "system"
    },
    #上述内容是需要解析的关键部分
  ],
  "searchFieldContent": "",
  "searchField": "keyWord",
  "searchFieldList": None,
  "isOpen": False
}


headers = {
  'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
  'Accept': "application/json, text/plain, */*",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Linux\"",
  'sec-ch-ua': "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
  'mappingPath': "",
  'groupCode': "800388",
  'sec-ch-ua-mobile': "?0",
  'x-lang': "CHI",
  'Content-Type': "application/json;charset=UTF-8",
  'content-language': "zh_CN",
  'Origin': "https://opac.lib.csu.edu.cn",
  'Sec-Fetch-Site': "same-origin",
  'Sec-Fetch-Mode': "cors",
  'Sec-Fetch-Dest': "empty",
  'Referer': "https://opac.lib.csu.edu.cn/",
  'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}

response = requests.post(url, data=json.dumps(payload2), headers=headers)

print(response.text)


"""
{
  "success": true,
  "message": "操作成功",
  "errCode": 200,
  "errorCode": null,
  "data": {
    "numFound": 21964,
    "searchResult": [
      {
        "recordId": 62843,
        "favoritesId": null,
        "kbcId": null,
        "title": "Identification and system parameter estimation 1976  :proceedings of the Sixth IFAC Symposium, Washington DC, USA, 7-11 June 1982  V. 2  1st ed.",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": "edited by Rajbman,N,S.",
        "publisher": "Published for the International Federation of Automatic Control by Pergamon Press,",
        "isbn": "0444851127 (V.1) :",
        "isbns": [
          "0444851127 (V.1) :",
          "0444851135 (V.2) :",
          "0444851143 (V.3) :"
        ],
        "issn": "0444851127 (V.1) :",
        "publishYear": "1983?",
        "publFreqCode": null,
        "adstract": "\"Sixth IFAC Symposium on Identification and System Paramer Estimation organized by Controls Systems Society of the Institute of Electrical and Electronics Engineers (IEEE) ; sponsored by IFAC Technical Committee on Applications, IFAC Theory Committee\"--V. 1, p. v.",
        "ddAbstract": null,
        "subjectWord": "System identification Parameter estimation",
        "chiClassNo": null,
        "sciClassNo": [
          "73.82083"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 3,
        "groupPhysicalCount": 3,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "edited by Rajbman,N,S.",
          "Bekey, George A.,",
          "Saridis, George N.,",
          "IEEE Control Systems Society.",
          "IEEE Control Systems Society.",
          "IFAC Symposium on Identification and System Parameter Estimation"
        ],
        "_48Unit": null,
        "hostUnit": ",IEEE Control Systems Society.,Saridis, George N.,,edited by Rajbman,N,S.,IFAC Symposium on Identification and System Parameter Estimation,Bekey, George A.,",
        "docCode": 1,
        "callNoOne": "73.8083/I-61*5",
        "callNo": [
          "73.8083/I-61*5"
        ],
        "onShelfCountI": 3,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":62843,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 62843,
            "mdLevel": 3
          }
        ],
        "price": "4.80",
        "bookPage": "1709 p.; :",
        "bookThickness": "31 cm.",
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": null,
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 62600,
        "favoritesId": null,
        "kbcId": null,
        "title": "Identification and system parameter estimation part1 :proceedings of the 4th IFAC Symposium, Washington DC, USA, 7-11 June 1982  V. 1  1st ed.",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": "edited by G.A. Bekey and G.N. Saridis.",
        "publisher": "Published for the International Federation of Automatic Control by Pergamon Press,",
        "isbn": "0444851127(V.1) :",
        "isbns": [
          "0444851127(V.1) :"
        ],
        "issn": "0444851127(V.1) :",
        "publishYear": "1983?",
        "publFreqCode": null,
        "adstract": "\"Sixth IFAC Symposium on Identification and System Paramer Estimation organized by Controls Systems Society of the Institute of Electrical and Electronics Engineers (IEEE) ; sponsored by IFAC Technical Committee on Applications, IFAC Theory Committee\"--V. 1, p. v.",
        "ddAbstract": null,
        "subjectWord": "System identification Parameter estimation",
        "chiClassNo": null,
        "sciClassNo": [
          "73.8083"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 2,
        "groupPhysicalCount": 2,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "edited by G.A. Bekey and G.N. Saridis.",
          "Bekey, George A.,",
          "Saridis, George N.,",
          "IEEE Control Systems Society.",
          "IEEE Control Systems Society.",
          "IFAC Symposium on Identification and System Parameter Estimation"
        ],
        "_48Unit": null,
        "hostUnit": ",IEEE Control Systems Society.,Saridis, George N.,,edited by G.A. Bekey and G.N. Saridis.,IFAC Symposium on Identification and System Parameter Estimation,Bekey, George A.,",
        "docCode": 1,
        "callNoOne": "73.8083/I-61*5",
        "callNo": [
          "73.8083/I-61*5"
        ],
        "onShelfCountI": 2,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":62600,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 62600,
            "mdLevel": 3
          }
        ],
        "price": "4.80",
        "bookPage": "840 p.; :",
        "bookThickness": "23 cm.",
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": null,
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 39192,
        "favoritesId": null,
        "kbcId": null,
        "title": "System modeling and optimization  :proceedings of the 10th IFIP Conference, New York City, USA, August 31-September 4, 1981 ",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": "edited by R.F. Drenick and F. Kozin.",
        "publisher": "Springer-Verlag,",
        "isbn": "0387116915 (U.S. : pbk. ):",
        "isbns": [
          "0387116915 (U.S. : pbk. ):"
        ],
        "issn": "0387116915 (U.S. : pbk. ):",
        "publishYear": "1982.",
        "publFreqCode": null,
        "adstract": "Papers selected from those presented at the 10th IFIP Conference on System Modeling and Optimization which was organized on behalf of the Technical Committee of the International Federation for Information Processing by the Polytechnic Institute of New York.",
        "ddAbstract": null,
        "subjectWord": "System analysis Digital computer simulation Mathematical optimization",
        "chiClassNo": [
          "TP273-53"
        ],
        "sciClassNo": [
          "51.33083"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 2,
        "groupPhysicalCount": 2,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "edited by R.F. Drenick and F. Kozin.",
          "Drenick, R.F.",
          "Kozin, F.",
          "Polytechnic Institute of New York.",
          "Polytechnic Institute of New York.",
          "IFIP Conference on System Modeling and Optimization"
        ],
        "_48Unit": null,
        "hostUnit": ",Kozin, F.,Drenick, R.F.,Polytechnic Institute of New York.,edited by R.F. Drenick and F. Kozin.,IFIP Conference on System Modeling and Optimization",
        "docCode": 1,
        "callNoOne": "73.822083/ICS",
        "callNo": [
          "73.822083/ICS",
          "73.822083/ICS/1981",
          "51.33083/P963"
        ],
        "onShelfCountI": 2,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":39192,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 39192,
            "mdLevel": 3
          }
        ],
        "price": "106.20",
        "bookPage": "893 p. :",
        "bookThickness": "25 cm.",
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "工业技术"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 794724,
        "favoritesId": null,
        "kbcId": null,
        "title": "Vue.js实战",
        "collectionName": null,
        "langCode": "chi",
        "countryCode": "CN",
        "subjects": null,
        "author": "梁灏编著",
        "publisher": "清华大学出版社",
        "isbn": "978-7-302-48492-9",
        "isbns": [
          "978-7-302-48492-9"
        ],
        "issn": "978-7-302-48492-9",
        "publishYear": "2017",
        "publFreqCode": null,
        "adstract": "本书以Vue.js 2为基础，以项目实战的方式来引导读者渐进式学习Vue.js。全书分为基础篇、进阶篇和实战篇三部分。基础篇主要是对 Vue.js核心功能的介绍；进阶篇主要讲解前端工程化Vue.js的组件化、插件的使用；实战篇着重开发了两个完整的示例，所涉及的内容涵盖Vue.js绝大部分API。通过阅读本书，读者能够掌握Vue.js框架主要API的使用方法、自定义指令、组件开发、单文件组件、Render函数、使用webpack开发可复用的单页面富应用等。",
        "ddAbstract": null,
        "subjectWord": "网页制作工具",
        "chiClassNo": [
          "TP392.092.2"
        ],
        "sciClassNo": null,
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 3,
        "groupPhysicalCount": 3,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": [
          "08"
        ],
        "discode2": [
          "0812"
        ],
        "discode3": [
          "081203"
        ],
        "_47Unit": [
          "梁灏"
        ],
        "_48Unit": [
          "梁灏编著"
        ],
        "hostUnit": ",梁灏",
        "docCode": 1,
        "callNoOne": "TP392.092.2/LH",
        "callNo": [
          "TP392.092.2/LH"
        ],
        "onShelfCountI": 3,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":794724,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 794724,
            "mdLevel": 3
          }
        ],
        "price": "79.00",
        "bookPage": "xi, 330页",
        "bookThickness": "26cm",
        "_021": [
          "梁灏"
        ],
        "personalAuthor": "梁灏",
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "工业技术"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 907324,
        "favoritesId": null,
        "kbcId": null,
        "title": "Vue.js技术内幕",
        "collectionName": null,
        "langCode": "chi",
        "countryCode": "CN",
        "subjects": null,
        "author": "黄轶著",
        "publisher": "人民邮电出版社",
        "isbn": "978-7-115-59646-8",
        "isbns": [
          "978-7-115-59646-8"
        ],
        "issn": "978-7-115-59646-8",
        "publishYear": "2022",
        "publFreqCode": null,
        "adstract": "本书将带领读者阅读Vue.js 3.0的源码, 通过大量注释、流程图, 呈现每部分源码的“前因后果”, 帮助读者体会Vue.js的设计思想。全书共七部分, 分为24章, 作者结合实际用例, 循序渐进地介绍了Vue.js的整体设计、组件、响应式原理、编译和优化、实用特性、内置组件、官方生态等内容。阅读本书不仅可以深人理解Vue.js的内核实现, 还能学到阅读源码的技巧, 提高业务逻辑分析能力和代码重构能力。",
        "ddAbstract": null,
        "subjectWord": "网页制作工具",
        "chiClassNo": [
          "TP393.092.2"
        ],
        "sciClassNo": null,
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 2,
        "groupPhysicalCount": 2,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": [
          "08"
        ],
        "discode2": [
          "0812"
        ],
        "discode3": [
          "081203"
        ],
        "_47Unit": [
          "黄轶"
        ],
        "_48Unit": [
          "黄轶著"
        ],
        "hostUnit": ",黄轶",
        "docCode": 1,
        "callNoOne": "TP393.092.2/HY2",
        "callNo": [
          "TP393.092.2/HY2"
        ],
        "onShelfCountI": 2,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":907324,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 907324,
            "mdLevel": 3
          }
        ],
        "price": "119.80",
        "bookPage": "x, 474页",
        "bookThickness": "24cm",
        "_021": [
          "黄轶"
        ],
        "personalAuthor": "黄轶",
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "工业技术"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 12862,
        "favoritesId": null,
        "kbcId": null,
        "title": "Vehicle system dynamics.",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": null,
        "publisher": "Swets and Zeitlinger.,",
        "isbn": "0042-3114",
        "isbns": [
          "0042-3114",
          "873C0176"
        ],
        "issn": "0042-3114",
        "publishYear": "1972-",
        "publFreqCode": 2,
        "adstract": "Official organ of the International Association for Vehicle System Dynamics <, May 1980->",
        "ddAbstract": null,
        "subjectWord": "Motor vehicles",
        "chiClassNo": [
          "U4"
        ],
        "sciClassNo": [
          "87.18"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 61,
        "groupPhysicalCount": 61,
        "contiCount": 13,
        "groupContiCount": 13,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "International Association for Vehicle System Dynamics.",
          "International Association for Vehicle System Dynamics."
        ],
        "_48Unit": null,
        "hostUnit": ",International Association for Vehicle System Dynamics.",
        "docCode": 2,
        "callNoOne": "U4/4",
        "callNo": [
          "U4/4",
          "95.8718/VSD"
        ],
        "onShelfCountI": 61,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":12862,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 12862,
            "mdLevel": 3
          }
        ],
        "price": null,
        "bookPage": " v.",
        "bookThickness": "24 cm.",
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "交通运输-公路运输"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "期刊",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 49717,
        "favoritesId": null,
        "kbcId": null,
        "title": "Proceedings of the 15th Hawall International Conference on System Science, V.2:Medical information processing.",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": null,
        "publisher": "Hawall International Conference on System Science,",
        "isbn": null,
        "isbns": null,
        "issn": null,
        "publishYear": "1982.",
        "publFreqCode": null,
        "adstract": null,
        "ddAbstract": null,
        "subjectWord": null,
        "chiClassNo": null,
        "sciClassNo": [
          "73.87221083"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 1,
        "groupPhysicalCount": 1,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "Hawall International Conference on System Science, 15th, 1982."
        ],
        "_48Unit": null,
        "hostUnit": ",Hawall International Conference on System Science, 15th, 1982.",
        "docCode": 1,
        "callNoOne": "73.87221083/HIC/15:2",
        "callNo": [
          "73.87221083/HIC/15:2"
        ],
        "onShelfCountI": 1,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":49717,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 49717,
            "mdLevel": 3
          }
        ],
        "price": "224.00",
        "bookPage": "778 p.",
        "bookThickness": null,
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": null,
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 907857,
        "favoritesId": null,
        "kbcId": null,
        "title": "Vue.js从入门到项目实战. 第2版",
        "collectionName": null,
        "langCode": "chi",
        "countryCode": "CN",
        "subjects": null,
        "author": "刘汉伟编著",
        "publisher": "清华大学出版社",
        "isbn": "978-7-302-59587-8",
        "isbns": [
          "978-7-302-59587-8"
        ],
        "issn": "978-7-302-59587-8",
        "publishYear": "2022",
        "publFreqCode": null,
        "adstract": "本书从Vue框架的基础语法讲起, 逐步深入Vue进阶实战, 并在最后配合项目实战案例, 重点演示了Vue在项目开发中的一些应用。在系统地讲解Vue的相关知识之余, 本书力图使读者对Vue项目开发产生更深入的理解。本书共分为11章, 涵盖的主要内容有前端的发展历程、Vue的基本介绍、Vue的语法、Vue中的选项、Vue中的内置组件、Vue项目化、使用Vue开发电商类网站、使用Vue开发企业官网、使用Vue开发移动端资讯类网站、使用Vue开发工具类网站。",
        "ddAbstract": null,
        "subjectWord": "网页制作工具",
        "chiClassNo": [
          "TP393.092.2"
        ],
        "sciClassNo": null,
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 3,
        "groupPhysicalCount": 3,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": [
          "08"
        ],
        "discode2": [
          "0812"
        ],
        "discode3": [
          "081203"
        ],
        "_47Unit": [
          "刘汉伟"
        ],
        "_48Unit": [
          "刘汉伟编著"
        ],
        "hostUnit": ",刘汉伟",
        "docCode": 1,
        "callNoOne": "TP393.092.2/LHW=2",
        "callNo": [
          "TP393.092.2/LHW=2"
        ],
        "onShelfCountI": 3,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":907857,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 907857,
            "mdLevel": 3
          }
        ],
        "price": "89.00",
        "bookPage": "XII, 240页",
        "bookThickness": "24cm",
        "_021": [
          "刘汉伟"
        ],
        "personalAuthor": "刘汉伟",
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "工业技术"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 49716,
        "favoritesId": null,
        "kbcId": null,
        "title": "Proceedings of  the 15th Hawall International Conference on System Science,V.1: Software, hardware decision support systems, special topics. .",
        "collectionName": null,
        "langCode": "eng",
        "countryCode": "US",
        "subjects": null,
        "author": null,
        "publisher": "Hawall International Conference on System Science,",
        "isbn": null,
        "isbns": null,
        "issn": null,
        "publishYear": "1982.",
        "publFreqCode": null,
        "adstract": null,
        "ddAbstract": null,
        "subjectWord": null,
        "chiClassNo": null,
        "sciClassNo": [
          "73.87221083"
        ],
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 1,
        "groupPhysicalCount": 1,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": null,
        "discode2": null,
        "discode3": null,
        "_47Unit": [
          "Hawall International Conference on System Science, 15th. 1982."
        ],
        "_48Unit": null,
        "hostUnit": ",Hawall International Conference on System Science, 15th. 1982.",
        "docCode": 1,
        "callNoOne": "73.87221083/HIC/15:1",
        "callNo": [
          "73.87221083/HIC/15:1"
        ],
        "onShelfCountI": 1,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":49716,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 49716,
            "mdLevel": 3
          }
        ],
        "price": "224.00",
        "bookPage": "916 p.",
        "bookThickness": null,
        "_021": null,
        "personalAuthor": null,
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": null,
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      },
      {
        "recordId": 851396,
        "favoritesId": null,
        "kbcId": null,
        "title": "Vue.js从入门到项目实战",
        "collectionName": null,
        "langCode": "chi",
        "countryCode": "CN",
        "subjects": null,
        "author": "胡同江编著",
        "publisher": "清华大学出版社",
        "isbn": "978-7-302-53919-3",
        "isbns": [
          "978-7-302-53919-3"
        ],
        "issn": "978-7-302-53919-3",
        "publishYear": "2019",
        "publFreqCode": null,
        "adstract": "本书共16章, 主要讲解了Vue.js的基本概念, Vue实例和模板语法, 计算属性、侦听器和过滤器, 内置指令, 页面元素样式的绑定, 事件处理, 双向数据绑定, 组件技术, 使用webpack打包, 项目脚手架vue-cli, 前端路由技术, 状态管理等。",
        "ddAbstract": null,
        "subjectWord": "网页制作工具",
        "chiClassNo": [
          "TP393.092.2"
        ],
        "sciClassNo": null,
        "periName": null,
        "vol": null,
        "issue": null,
        "year": null,
        "keyWord": null,
        "claimStatus": null,
        "_46": null,
        "ddGroup": null,
        "ddType": null,
        "ddYear": null,
        "needVerify": null,
        "verifyStatus": null,
        "physicalCount": 3,
        "groupPhysicalCount": 3,
        "contiCount": 0,
        "groupContiCount": null,
        "groupECount": 0,
        "groupDCount": null,
        "esCount": 0,
        "eCount": 0,
        "dCount": 0,
        "discode1": [
          "08"
        ],
        "discode2": [
          "0812"
        ],
        "discode3": [
          "081203"
        ],
        "_47Unit": [
          "胡同江"
        ],
        "_48Unit": [
          "胡同江编著"
        ],
        "hostUnit": ",胡同江",
        "docCode": 1,
        "callNoOne": "TP393.092.2/HTJ",
        "callNo": [
          "TP393.092.2/HTJ"
        ],
        "onShelfCountI": 3,
        "multiVersionNum": null,
        "canBrrowCountI": null,
        "groupRecord": "[{\"recordId\":851396,\"mdLevel\":3}]",
        "groupRecordIds": [
          {
            "recordId": 851396,
            "mdLevel": 3
          }
        ],
        "price": "78.00",
        "bookPage": "329页",
        "bookThickness": "26cm",
        "_021": [
          "胡同江"
        ],
        "personalAuthor": "胡同江",
        "_022": null,
        "organizedAuthor": null,
        "uniformBookNo": null,
        "postNo": null,
        "bgnEndVol": null,
        "bgnEndVols": null,
        "publFreq": null,
        "publFreqDoc": null,
        "npcClassNo": null,
        "pagesNum": null,
        "group": null,
        "tutor": null,
        "tutorGroup": null,
        "chiSubjectClass": [
          "工业技术"
        ],
        "avgScore": null,
        "doi": null,
        "beginDate": null,
        "endDate": null,
        "docName": "图书",
        "coreInclude": null,
        "eCollectionIds": null,
        "coreIncludeValue": [],
        "pic": null,
        "inDate": null,
        "calisCode": "243040",
        "eIsbn": null,
        "systemCoreStr": null,
        "customCoreStr": null,
        "neweCollectionIds": null,
        "toolNumber": null,
        "onShelfNum": null,
        "borrowNum": null,
        "transTitle": null,
        "relationNum": null,
        "collectTime": null,
        "myFav": false
      }
    ],
    "facetResult": {
      "campusId": {
        "2": 4122,
        "1": 2934,
        "4": 2751,
        "3": 1017,
        "5": 66,
        "6": 3
      },
      "curLocationId": {
        "67": 1155,
        "144": 273,
        "24": 1141,
        "37": 1611,
        "59": 512,
        "28": 352,
        "31": 1100,
        "20": 173,
        "65": 3917,
        "76": 568,
        "21": 513
      },
      "coreIncludes": {
        "BKCI": 211,
        "SSCI": 34,
        "AHCI": 25,
        "SNIP": 524,
        "EI": 285,
        "ESCI": 146,
        "JCR": 284,
        "SCOPUS": 221,
        "SJR": 522,
        "ESI": 279,
        "SCIE": 247
      },
      "langCode": {
        "eng": 11169,
        "999": 6137,
        "chi": 4658
      },
      "discode1": {
        "00": 468,
        "12": 1238,
        "01": 306,
        "02": 1370,
        "03": 1098,
        "04": 529,
        "05": 318,
        "06": 382,
        "07": 1885,
        "08": 5157,
        "10": 742
      },
      "libCode": {
        "80038800001": 8258
      },
      "author": {
        "M.": 56,
        "L.": 51,
        "J.": 46,
        "Gmelin": 46,
        "H.": 46,
        "Jr.": 48,
        "G.": 44,
        "Liu": 45,
        "S.": 71,
        "Li": 52,
        "A.": 47
      },
      "publisher": {
        "IntechOpen": 5114,
        "科学出版社": 277,
        "清华大学出版社": 283,
        "John Wiley & Sons, Incorporated": 498,
        "ASME": 299,
        "中南大学": 240,
        "Springer": 244,
        "National Academies Press": 284,
        "机械工业出版社": 323,
        "电子工业出版社": 231,
        "Taylor & Francis Group": 257
      },
      "subject": {
        "高等学校": 400,
        "系统仿真": 73,
        "系统建模": 66,
        "高等教育": 78,
        "程序设计": 166,
        "Expert systems (Computer science)": 82,
        "系统设计": 188,
        "System analysis.": 162,
        "System design.": 89,
        "研究": 1480,
        "应用": 109
      },
      "resourceType": {
        "2": 13705,
        "1": 8259
      },
      "locationId": {
        "67": 1155,
        "144": 273,
        "24": 1141,
        "37": 1611,
        "59": 512,
        "28": 352,
        "31": 1109,
        "20": 173,
        "65": 3951,
        "76": 574,
        "21": 518
      },
      "countryCode": {
        "US": 11056,
        "99": 6129,
        "CN": 4779
      },
      "kindNo": {
        "O61-62": 55,
        "C931.6": 39,
        "TP271": 40,
        "TP3": 85,
        "TP273": 71,
        "TP316": 82,
        "N94": 54,
        "TM": 42,
        "TN": 40,
        "TP311.13": 29,
        "TP393.092.2": 54
      },
      "docCode": {
        "1": 20200,
        "2": 1496,
        "28": 268
      },
      "neweCollectionIds": {
        "1466399814846181378": 300,
        "1331664856845623296": 600,
        "1331595103007383552": 534,
        "1466399815248834585": 126,
        "1466399814246395908": 211,
        "1466399814909095942": 179,
        "1466399812858081286": 300,
        "1466399815248834566": 180,
        "1466399813860519938": 4994,
        "1331635717065383936": 5389,
        "1331622967513686016": 870
      },
      "litCode": {
        "3": 15621,
        "2": 4579,
        "7": 1474,
        "1": 268,
        "6": 22
      },
      "customSub": {}
    },
    "hlResult": {
      "49716": {
        "publisher": [
          "Hawall International Conference on <font color='#ff9933'>System</font> Science,"
        ],
        "title": [
          "Proceedings of  the 15th Hawall International Conference on <font color='#ff9933'>System</font> Science,V.1: Software, hardware decision support systems, special topics. ."
        ]
      },
      "794724": {
        "adstract": [
          "本书以<font color='#ff9933'>Vue</font>.js 2为基础，以项目实战的方式来引导读者渐进式学习<font color='#ff9933'>Vue</font>.js。全书分为基础篇、进阶篇和实战篇三部分。基础篇主要是对 <font color='#ff9933'>Vue</font>.js核心功能的介绍；进阶篇主要讲解前端工程化<font color='#ff9933'>Vue</font>.js的组件化、插件的使用；实战篇着重开发了两个完整的示例，所涉及的内容涵盖<font color='#ff9933'>Vue</font>.js绝大部分API。通过阅读本书，读者能够掌握<font color='#ff9933'>Vue</font>.js框架主要API的使用方法、自定义指令、组件开发、单文件组件、Render函数、使用webpack开发可复用的单页面富应用等。"
        ],
        "title": [
          "<font color='#ff9933'>Vue</font>.js实战"
        ]
      },
      "907324": {
        "adstract": [
          "本书将带领读者阅读<font color='#ff9933'>Vue</font>.js 3.0的源码, 通过大量注释、流程图, 呈现每部分源码的“前因后果”, 帮助读者体会<font color='#ff9933'>Vue</font>.js的设计思想。全书共七部分, 分为24章, 作者结合实际用例, 循序渐进地介绍了<font color='#ff9933'>Vue</font>.js的整体设计、组件、响应式原理、编译和优化、实用特性、内置组件、官方生态等内容。阅读本书不仅可以深人理解<font color='#ff9933'>Vue</font>.js的内核实现, 还能学到阅读源码的技巧, 提高业务逻辑分析能力和代码重构能力。"
        ],
        "title": [
          "<font color='#ff9933'>Vue</font>.js技术内幕"
        ]
      },
      "907857": {
        "adstract": [
          "本书从<font color='#ff9933'>Vue</font>框架的基础语法讲起, 逐步深入<font color='#ff9933'>Vue</font>进阶实战, 并在最后配合项目实战案例, 重点演示了<font color='#ff9933'>Vue</font>在项目开发中的一些应用。在系统地讲解<font color='#ff9933'>Vue</font>的相关知识之余, 本书力图使读者对<font color='#ff9933'>Vue</font>项目开发产生更深入的理解。本书共分为11章, 涵盖的主要内容有前端的发展历程、<font color='#ff9933'>Vue</font>的基本介绍、<font color='#ff9933'>Vue</font>的语法、<font color='#ff9933'>Vue</font>中的选项、<font color='#ff9933'>Vue</font>中的内置组件、<font color='#ff9933'>Vue</font>项目化、使用<font color='#ff9933'>Vue</font>开发电商类网站、使用<font color='#ff9933'>Vue</font>开发企业官网、使用<font color='#ff9933'>Vue</font>开发移动端资讯类网站、使用<font color='#ff9933'>Vue</font>开发工具类网站。"
        ],
        "title": [
          "<font color='#ff9933'>Vue</font>.js从入门到项目实战. 第2版"
        ]
      },
      "12862": {
        "adstract": [
          "Official organ of the International Association for Vehicle <font color='#ff9933'>System</font> Dynamics <, May 1980->"
        ],
        "title": [
          "Vehicle <font color='#ff9933'>system</font> dynamics."
        ]
      },
      "62600": {
        "adstract": [
          "\"Sixth IFAC Symposium on Identification and <font color='#ff9933'>System</font> Paramer Estimation organized by Controls Systems Society of the Institute of Electrical and Electronics Engineers (IEEE) ; sponsored by IFAC Technical Committee on Applications, IFAC Theory Committee\"--V. 1, p. v."
        ],
        "subjectWord": [
          "<font color='#ff9933'>System</font> identification Parameter estimation"
        ],
        "title": [
          "Identification and <font color='#ff9933'>system</font> parameter estimation part1 :proceedings of the 4th IFAC Symposium, Washington DC, USA, 7-11 June 1982  V. 1  1st ed."
        ]
      },
      "62843": {
        "adstract": [
          "\"Sixth IFAC Symposium on Identification and <font color='#ff9933'>System</font> Paramer Estimation organized by Controls Systems Society of the Institute of Electrical and Electronics Engineers (IEEE) ; sponsored by IFAC Technical Committee on Applications, IFAC Theory Committee\"--V. 1, p. v."
        ],
        "subjectWord": [
          "<font color='#ff9933'>System</font> identification Parameter estimation"
        ],
        "title": [
          "Identification and <font color='#ff9933'>system</font> parameter estimation 1976  :proceedings of the Sixth IFAC Symposium, Washington DC, USA, 7-11 June 1982  V. 2  1st ed."
        ]
      },
      "39192": {
        "adstract": [
          "Papers selected from those presented at the 10th IFIP Conference on <font color='#ff9933'>System</font> Modeling and Optimization which was organized on behalf of the Technical Committee of the International Federation for Information Processing by the Polytechnic Institute of New York."
        ],
        "subjectWord": [
          "<font color='#ff9933'>System</font> analysis Digital computer simulation Mathematical optimization"
        ],
        "title": [
          "<font color='#ff9933'>System</font> modeling and optimization  :proceedings of the 10th IFIP Conference, New York City, USA, August 31-September 4, 1981 "
        ]
      },
      "851396": {
        "adstract": [
          "本书共16章, 主要讲解了<font color='#ff9933'>Vue</font>.js的基本概念, <font color='#ff9933'>Vue</font>实例和模板语法, 计算属性、侦听器和过滤器, 内置指令, 页面元素样式的绑定, 事件处理, 双向数据绑定, 组件技术, 使用webpack打包, 项目脚手架<font color='#ff9933'>vue</font>-cli, 前端路由技术, 状态管理等。"
        ],
        "title": [
          "<font color='#ff9933'>Vue</font>.js从入门到项目实战"
        ]
      },
      "49717": {
        "publisher": [
          "Hawall International Conference on <font color='#ff9933'>System</font> Science,"
        ],
        "title": [
          "Proceedings of the 15th Hawall International Conference on <font color='#ff9933'>System</font> Science, V.2:Medical information processing."
        ]
      }
    },
    "levelResultList": []
  }
}

"""
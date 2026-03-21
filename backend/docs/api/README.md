# API 参考文档

CampusMind 后端 API 参考文档，涵盖所有 RESTful 接口。

## 认证方式

所有需要认证的接口通过 **JWT Bearer Token** 进行身份验证。

### 请求头格式

```
Authorization: Bearer <your_jwt_token>
```

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 Token 过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 423 | 账号已被锁定 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

## 目录结构

- [认证接口](./endpoints-auth.md) - 登录/登出/刷新 Token
- [知识库 CRUD](./endpoints-knowledge.md) - 知识库管理
- [知识文件管理](./endpoints-knowledge-file.md) - 知识文件操作
- [网页爬取](./endpoints-crawl.md) - 内容爬取与索引
- [内容索引](./endpoints-index.md) - 向量/关键词索引
- [RAG 检索](./endpoints-retrieve.md) - 混合检索
- [LLM 对话](./endpoints-completion.md) - 流式对话与历史

# 测试指南

## 测试框架

CampusMind 使用 **pytest** 作为测试框架。

## 运行测试

### 运行所有测试

```bash
cd backend
uv run pytest
```

### 运行指定测试文件

```bash
uv run pytest tests/api/test_auth.py
```

### 运行指定测试类

```bash
uv run pytest tests/api/test_auth.py::TestAuth
```

### 运行指定测试函数

```bash
uv run pytest tests/api/test_auth.py::TestAuth::test_login_success
```

### 收集测试（不运行）

```bash
uv run pytest --collect-only
```

---

## 测试结构

```
tests/
├── api/                    # API 端点测试
│   ├── test_auth.py
│   ├── test_knowledge.py
│   └── ...
├── core/                  # 核心模块测试
│   ├── session/
│   ├── tools/
│   └── agents/
├── services/              # 服务层测试
│   ├── test_rag_handler.py
│   └── ...
├── e2e/                   # 端到端测试
│   ├── test_auth.py
│   ├── test_api_flow.py
│   └── ...
└── conftest.py            # pytest 配置和 fixtures
```

---

## 测试配置

### 环境变量

```bash
DATABASE_URL=sqlite:///./test_campusmind.db
TESTING=true
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

---

## 目录结构

- [测试 Fixtures](./fixtures.md) - conftest.py 中的 fixtures 说明

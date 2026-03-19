-- CampusMind Database Schema (Simplified)
-- Version: 2.0
-- Date: 2026-03-19
-- Database: PostgreSQL (compatible with SQLite for testing)

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    email TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================================================
-- 2. DIALOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS dialogs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dialogs_user_id ON dialogs(user_id);
CREATE INDEX IF NOT EXISTS idx_dialogs_updated_at ON dialogs(updated_at DESC);

-- ============================================================================
-- 3. CHAT HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    dialog_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    file_url TEXT,
    events TEXT,
    extra TEXT,
    parent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialog_id) REFERENCES dialogs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_history_dialog_id ON chat_history(dialog_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_history_dialog_created ON chat_history(dialog_id, created_at);

-- ============================================================================
-- 4. KNOWLEDGE BASES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(name, user_id)
);

CREATE INDEX IF NOT EXISTS idx_kb_user_id ON knowledge_bases(user_id);
CREATE INDEX IF NOT EXISTS idx_kb_updated_at ON knowledge_bases(updated_at DESC);

-- ============================================================================
-- 5. KNOWLEDGE FILES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_files (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    knowledge_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    oss_url TEXT NOT NULL,
    file_size BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kf_knowledge_id ON knowledge_files(knowledge_id);
CREATE INDEX IF NOT EXISTS idx_kf_user_id ON knowledge_files(user_id);
CREATE INDEX IF NOT EXISTS idx_kf_status ON knowledge_files(status);
CREATE INDEX IF NOT EXISTS idx_kf_created_at ON knowledge_files(created_at);

-- ============================================================================
-- 6. TOOL DEFINITIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS tool_definitions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    requires_auth BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tool_def_category ON tool_definitions(category);
CREATE INDEX IF NOT EXISTS idx_tool_def_requires_auth ON tool_definitions(requires_auth);

-- ============================================================================
-- 7. TOOL CALL LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS tool_call_logs (
    id TEXT PRIMARY KEY,
    dialog_id TEXT,
    tool_name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialog_id) REFERENCES dialogs(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tcl_dialog_id ON tool_call_logs(dialog_id);
CREATE INDEX IF NOT EXISTS idx_tcl_user_id ON tool_call_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_tcl_tool_name ON tool_call_logs(tool_name);
CREATE INDEX IF NOT EXISTS idx_tcl_created_at ON tool_call_logs(created_at DESC);

-- ============================================================================
-- SEED DATA: TOOL DEFINITIONS
-- ============================================================================
INSERT INTO tool_definitions (id, name, description, category, requires_auth) VALUES
    ('tool_library_search', 'library_search', '图书馆馆藏搜索', 'library', FALSE),
    ('tool_library_location', 'library_get_book_location', '图书馆馆藏位置查询', 'library', FALSE),
    ('tool_career_teachin', 'career_teachin', '宣讲会信息查询', 'career', FALSE),
    ('tool_career_recruit', 'career_campus_recruit', '校园招聘信息搜索', 'career', FALSE),
    ('tool_career_intern', 'career_campus_intern', '实习岗位信息搜索', 'career', FALSE),
    ('tool_career_jobfair', 'career_jobfair', '招聘会信息查询', 'career', FALSE),
    ('tool_rag_search', 'rag_search', '知识库RAG检索', 'rag', FALSE),
    ('tool_jwc_grade', 'jwc_grade', '成绩查询', 'jwc', TRUE),
    ('tool_jwc_schedule', 'jwc_schedule', '课表查询', 'jwc', TRUE),
    ('tool_jwc_rank', 'jwc_rank', '专业排名查询', 'jwc', TRUE),
    ('tool_jwc_level_exam', 'jwc_level_exam', '等级考试成绩查询', 'jwc', TRUE),
    ('tool_oa_notification', 'oa_notification_list', '校内办公网通知查询', 'oa', TRUE);

-- ============================================================================
-- MIGRATION LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_migrations (version, description) VALUES
    ('2.0', 'Simplified schema - removed sessions, departments, oa_notifications, chunks tables');

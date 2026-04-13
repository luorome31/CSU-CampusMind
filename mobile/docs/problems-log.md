# Mobile 问题日志

## 格式说明

| id | date | problem | solution | commit |
|----|------|---------|----------|--------|
| 自增编号 | 发现日期 | 问题描述及影响 | 解决方案 | 对应的 commit hash |

---

## 日志

| id | date | problem | solution | commit |
|----|------|---------|----------|--------|
| 1 | 2026-04-13 | package.json 依赖版本错误：@react-native-community/netinfo 版本 ~13.0.0 不存在，@types/react-native 版本 ~0.76.0 不存在 | 修正为 ~12.0.1 和 ~0.73.0 | 153b260 |
| 2 | 2026-04-13 | babel-plugin-module-resolver 未安装导致 Jest 测试无法运行（早期问题） | 已安装 babel-plugin-module-resolver 到 devDependencies | 153b260 |
| 3 | 2026-04-13 | useNetworkStatus hook 存在 stale closure bug：toastShown 在依赖数组中导致监听器捕获过期值 | 使用 useRef 替代 useState 追踪 toastShown | c811485 |
| 4 | 2026-04-13 | User 类型字段与后端不匹配：user_id 应为 id，nickname 应为 display_name，缺少 is_active 和 updated_at | 修正类型定义与后端对齐 | e5702c2 |
| 5 | 2026-04-13 | eslint.config.mjs 初始为空导致 pre-commit hook 失败 | 添加基础 ESLint 规则配置 | 153b260 |
| 6 | 2026-04-13 | 多个 barrel 文件 (types/index.ts, hooks/index.ts, navigation/index.ts) 为空导出 | 填充正确的 re-export 语句 | 054ca26 |
| 7 | 2026-04-13 | app.json 引用了未安装的 expo-router 插件导致启动失败 | 移除 expo-router 插件配置；移除不存在的 icon/splash/adaptive-icon 资源引用 | - |
| 8 | 2026-04-13 | Expo 无法找到 App 入口，期望根目录有 App.tsx | 创建根目录 App.tsx re-export src/App | - |

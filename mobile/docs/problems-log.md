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
| 9 | 2026-04-13 | authStore.ts 中 axios.post 返回的是 AxiosResponse 对象，需通过 response.data 访问响应数据 | 修改代码为 `const data = response.data;` 再使用 data.user_id 等字段 | e6df5bb |
| 10 | 2026-04-13 | Jest 配置缺失导致 React Native 组件测试失败：Cannot find module 'react-test-renderer' | 安装 jest-expo@52 preset，它已内置 React Native 测试支持 | 后续 commit |
| 11 | 2026-04-13 | react-test-renderer@19.2.5 与 react@18.3.1 版本冲突（peer react^19.2.5 required） | 卸载 react-test-renderer，jest-expo 已包含所需功能 | 后续 commit |
| 12 | 2026-04-13 | Jest 测试中 mock 路径错误：'../../utils/storage' 应为 '../../../utils/storage' | 修正从 `__tests__/` 到 `utils/` 的相对路径 | 1566a32 |
| 13 | 2026-04-13 | Zustand store 在测试间共享状态导致测试互相干扰 | 在 beforeEach 中使用 `useAuthStore.setState({...})` 重置状态 | 后续 commit |
| 14 | 2026-04-13 | LoginScreen 测试中 ActivityIndicator 缺少 testID 导致 getByTestId 失败 | 改用 screen.queryByText('登录') 检测 loading 状态替代方案 | 后续 commit |
| 15 | 2026-04-14 | 移动端 LoginScreen 样式局促，组件过度拥挤 | 减小了外层 padding，调整标题字体及卡片内边距以适配小屏 | 后续 commit |
| 16 | 2026-04-14 | 发起登录 API 时报错 502 Bad Gateway 且后端无收发记录 | 本地网络代理(如 7890)拦截了局域网请求，在代理配置中忽略了 `192.168.*` | - |
| 17 | 2026-04-14 | 登录过程产生未捕获异常导致只显示前端错误而无 log 输出，且状态机终端 | React Native Keychain 依赖未适配 Expo Go 和 Web；将其替换为 `expo-secure-store` 并增加 Web 端 `localStorage` 降级及异常 catch 日志打印 | 后续 commit |
| 18 | 2026-04-14 | Web Bundling failed: Unable to resolve "./components/BlurView" from @react-native-community/blur | Expo 项目应使用 `expo-blur` 而非 `@react-native-community/blur`；后者依赖原生代码链接，在 Expo 托管工作流中无法正常工作 | f35004b |
| 19 | 2026-04-14 | TabNavigator 中 Tab 图标仍使用 emoji（🏠💬📚👤）而非 lucide icons | 导入 lucide-react-native 的 Home/MessageCircle/BookOpen/User 组件替换 | 后续 commit |
| 20 | 2026-04-14 | Expo Go 提示 ViewManagerResolver returned null for ExpoBlur 或 RCTViewManagerAdapter_ExpoBlur | 依赖版本不匹配（SDK 52 环境中使用了 55 版本）。降级 expo-blur 至 ~14.0.3，并使用 `yarn add --ignore-engines` 绕过 node 版本限制 | 后续 commit |
| 21 | 2026-04-15 | Chat SSE 数据解析错误：后端发送 `{type: "response_chunk", data: {chunk: "..."}}`，前端错误地访问 `data.chunk` 而非 `data.data.chunk`，导致 UI 不更新 | 修正 parseSSEData 处理双重包装结构，正确从 `data.data.chunk` 提取内容 | 2d99b67 |
| 22 | 2026-04-15 | `onDone` 回调从未被调用：react-native-sse 在流结束时触发 error 事件而非 close 事件，且错误消息为 "null" 时应视为正常结束 | 添加 close 事件监听器；错误处理中检测 "null" 消息判定为正常结束 | fab7731 |
| 23 | 2026-04-15 | ThinkingBlock 展开时 FlatList 的 `onContentSizeChange` 无条件调用 `scrollToEnd`，导致用户滚动阅读时被强制拉到最底部 | 使用 `isAtBottom` ref 追踪用户是否在底部，仅在 `isStreaming` 或用户位于底部时才自动滚动 | fab7731 |
| 24 | 2026-04-15 | react-native-sse 在流正常结束后不会触发 close 事件，且会尝试自动重连，导致 `onDone` 无法被调用 | 重写 chat.ts 使用原生 XMLHttpRequest，正确检测 `readyState === XMLHttpRequest.DONE` 并在 status 2xx 时调用 `onDone` | 用户最新 commit |


module.exports = {
  // 1. 使用 jest-expo 作为预设
  preset: 'jest-expo',
  // 2. 设置测试文件运行前需要执行的文件
  setupFilesAfterEnv: ['@testing-library/jest-native/extend-expect'],
  // 3. 配置需要被转换的 node_modules
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)',
  ],
};

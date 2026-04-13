export default [
  {
    ignores: ['node_modules/**', 'dist/**', '.expo/**', 'babel.config.js', 'metro.config.js', 'jest.config.js'],
  },
  {
    rules: {
      'no-unused-vars': 'off',
      'no-console': 'warn',
    },
  },
];

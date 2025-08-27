module.exports = {
  root: true,
  extends: ['next/core-web-vitals'],
  rules: {
    // Disable some strict rules for development
    '@next/next/no-img-element': 'off',
    'react-hooks/exhaustive-deps': 'warn',
  },
}

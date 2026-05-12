const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [],
  lintOnSave: false,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  outputDir: 'dist',
  assetsDir: 'static',
})

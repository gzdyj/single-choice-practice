<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">刷单选题系统</h2>
      <el-form ref="form" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="el-icon-user" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      form: { username: '', password: '' },
      loading: false,
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      },
    }
  },
  methods: {
    async handleLogin() {
      const valid = await this.$refs.form.validate().catch(() => false)
      if (!valid) return
      this.loading = true
      try {
        await this.$store.dispatch('user/login', this.form)
        this.$message.success('登录成功')
        const redirect = this.$route.query.redirect || '/'
        this.$router.push(redirect)
      } catch {
        // Error handled by interceptor
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
}
.login-footer {
  text-align: center;
  font-size: 14px;
  color: #909399;
}
.login-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>

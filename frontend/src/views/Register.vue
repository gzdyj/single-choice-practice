<template>
  <div class="register-container">
    <div class="register-card">
      <h2 class="register-title">用户注册</h2>
      <el-form ref="form" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="el-icon-user" size="large" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称（选填）" prefix-icon="el-icon-edit" size="large" />
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
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            prefix-icon="el-icon-lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleRegister">
            注 册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { register } from '@/api/auth'

export default {
  name: 'Register',
  data() {
    const validatePass = (rule, value, callback) => {
      if (value !== this.form.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    return {
      form: { username: '', nickname: '', password: '', confirmPassword: '' },
      loading: false,
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 4, message: '密码至少4位', trigger: 'blur' }],
        confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validatePass, trigger: 'blur' }],
      },
    }
  },
  methods: {
    async handleRegister() {
      const valid = await this.$refs.form.validate().catch(() => false)
      if (!valid) return
      this.loading = true
      try {
        await register({
          username: this.form.username,
          nickname: this.form.nickname || this.form.username,
          password: this.form.password,
        })
        this.$message.success('注册成功，请登录')
        this.$router.push('/login')
      } catch {
        // handled by interceptor
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
}
.register-footer {
  text-align: center;
  font-size: 14px;
  color: #909399;
}
.register-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>

<template>
  <div>
    <!-- Toolbar -->
    <div class="toolbar">
      <el-button type="primary" icon="el-icon-plus" @click="openCreateDialog">新增用户</el-button>
    </div>

    <!-- Filter -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filter" size="small">
        <el-form-item label="角色">
          <el-select v-model="filter.role" placeholder="全部" clearable style="width: 120px">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filter.keyword" placeholder="用户名/昵称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <el-table :data="users" v-loading="loading" stripe highlight-current-row>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="text" size="small" @click="openResetPwd(row)">重置密码</el-button>
            <el-button type="text" size="small" style="color: #f56c6c" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          @current-change="handlePageChange"
          :current-page="page"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          :total="total"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px" :close-on-click-modal="false">
      <el-form ref="dialogForm" :model="dialogForm" :rules="dialogRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="dialogForm.username" :disabled="isEditing" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="dialogForm.nickname" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="dialogForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEditing">
          <el-input v-model="dialogForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="dialogForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </span>
    </el-dialog>

    <!-- Reset Password Dialog -->
    <el-dialog title="重置密码" :visible.sync="pwdDialogVisible" width="400px" :close-on-click-modal="false">
      <el-form ref="pwdForm" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="handleResetPwd">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getUsers, createUser, updateUser, deleteUser, resetPassword } from '@/api/user'

export default {
  name: 'Users',
  data() {
    return {
      users: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
      filter: { role: '', keyword: '' },
      // Dialog
      dialogVisible: false,
      isEditing: false,
      dialogTitle: '',
      editId: null,
      submitLoading: false,
      dialogForm: { username: '', nickname: '', role: 'student', password: '', is_active: true },
      dialogRules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      },
      // Pwd dialog
      pwdDialogVisible: false,
      pwdLoading: false,
      pwdUserId: null,
      pwdForm: { new_password: '', confirm_password: '' },
      pwdRules: {
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 8, message: '密码至少8位', trigger: 'blur' },
          { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]).{8,}$/, message: '密码需包含大小写字母、数字和特殊字符', trigger: 'blur' },
        ],
        confirm_password: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: (rule, value, callback) => {
            if (value !== this.pwdForm.new_password) {
              callback(new Error('两次输入的密码不一致'))
            } else { callback() }
          }, trigger: 'blur' },
        ],
      },
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    roleLabel(role) {
      return { admin: '管理员', teacher: '教师', student: '学生' }[role] || role
    },
    roleTagType(role) {
      return { admin: 'danger', teacher: 'warning', student: 'success' }[role] || 'info'
    },
    async fetchData() {
      this.loading = true
      try {
        const res = await getUsers({ page: this.page, page_size: this.pageSize, ...this.filter })
        this.users = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    resetFilter() {
      this.filter = { role: '', keyword: '' }
      this.page = 1
      this.fetchData()
    },
    handlePageChange(page) {
      this.page = page
      this.fetchData()
    },
    // Create
    openCreateDialog() {
      this.isEditing = false
      this.dialogTitle = '新增用户'
      this.dialogForm = { username: '', nickname: '', role: 'student', password: '', is_active: true }
      this.editId = null
      this.dialogVisible = true
      this.$nextTick(() => this.$refs.dialogForm?.clearValidate())
    },
    // Edit
    openEditDialog(row) {
      this.isEditing = true
      this.dialogTitle = '编辑用户'
      this.dialogForm = { username: row.username, nickname: row.nickname, role: row.role, password: '', is_active: row.is_active }
      this.editId = row.id
      this.dialogVisible = true
      this.$nextTick(() => this.$refs.dialogForm?.clearValidate())
    },
    async handleSubmit() {
      const valid = await this.$refs.dialogForm.validate().catch(() => false)
      if (!valid) return
      this.submitLoading = true
      try {
        if (this.isEditing) {
          const data = { nickname: this.dialogForm.nickname, role: this.dialogForm.role, is_active: this.dialogForm.is_active }
          await updateUser(this.editId, data)
          this.$message.success('更新成功')
        } else {
          await createUser(this.dialogForm)
          this.$message.success('创建成功')
        }
        this.dialogVisible = false
        this.fetchData()
      } catch {
        // handled by interceptor
      } finally {
        this.submitLoading = false
      }
    },
    // Delete
    async handleDelete(row) {
      try {
        await this.$confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' })
        await deleteUser(row.id)
        this.$message.success('删除成功')
        this.fetchData()
      } catch {
        // cancelled or error
      }
    },
    // Reset password
    openResetPwd(row) {
      this.pwdUserId = row.id
      this.pwdForm = { new_password: '' }
      this.pwdDialogVisible = true
      this.$nextTick(() => this.$refs.pwdForm?.clearValidate())
    },
    async handleResetPwd() {
      const valid = await this.$refs.pwdForm.validate().catch(() => false)
      if (!valid) return
      this.pwdLoading = true
      try {
        await resetPassword(this.pwdUserId, this.pwdForm)
        this.$message.success('密码已重置')
        this.pwdDialogVisible = false
      } finally {
        this.pwdLoading = false
      }
    },
  },
}
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.filter-card {
  margin-bottom: 16px;
}
.pagination-wrap {
  margin-top: 20px;
  text-align: center;
}
</style>

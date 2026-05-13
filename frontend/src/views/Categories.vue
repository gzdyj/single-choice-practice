<template>
  <div>
    <el-card>
      <div slot="header" style="display:flex;align-items:center;justify-content:space-between">
        <span>分类管理</span>
        <div>
          <el-input
            v-model="keyword"
            placeholder="搜索分类名称"
            clearable
            size="small"
            style="width:200px;margin-right:8px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <el-button type="primary" icon="el-icon-plus" size="small" @click="openCreate">新增分类</el-button>
        </div>
      </div>

      <el-table :data="categories" v-loading="loading" stripe highlight-current-row>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="description" label="描述" min-width="240">
          <template slot-scope="{ row }">
            <span>{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="text" size="small" style="color:#f56c6c" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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
    <el-dialog :title="isEditing ? '编辑分类' : '新增分类'" :visible.sync="dialogVisible" width="500px" @closed="resetForm">
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="form.description" placeholder="请输入分类描述（选填）" :rows="3" maxlength="256" show-word-limit />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'

export default {
  name: 'Categories',
  data() {
    return {
      categories: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
      keyword: '',
      dialogVisible: false,
      isEditing: false,
      editingId: null,
      submitLoading: false,
      form: { name: '', description: '' },
      rules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' },
          { max: 64, message: '名称不能超过64个字符', trigger: 'blur' },
        ],
        description: [
          { max: 256, message: '描述不能超过256个字符', trigger: 'blur' },
        ],
      },
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.keyword) params.keyword = this.keyword
        const res = await getCategories(params)
        this.categories = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.fetchData()
    },
    handlePageChange(page) {
      this.page = page
      this.fetchData()
    },
    openCreate() {
      this.isEditing = false
      this.editingId = null
      this.form = { name: '', description: '' }
      this.dialogVisible = true
    },
    openEdit(row) {
      this.isEditing = true
      this.editingId = row.id
      this.form = { name: row.name, description: row.description }
      this.dialogVisible = true
    },
    resetForm() {
      this.$refs.form?.clearValidate()
    },
    async handleSubmit() {
      const valid = await this.$refs.form.validate().catch(() => false)
      if (!valid) return
      this.submitLoading = true
      try {
        if (this.isEditing) {
          await updateCategory(this.editingId, this.form)
          this.$message.success('更新成功')
        } else {
          await createCategory(this.form)
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
    async handleDelete(row) {
      try {
        await this.$confirm(`确定删除分类「${row.name}」吗？`, '提示', {
          type: 'warning',
          confirmButtonText: '确定删除',
        })
        await deleteCategory(row.id)
        this.$message.success('删除成功')
        this.fetchData()
      } catch (err) {
        if (err?.response?.data?.detail) {
          this.$message.error(err.response.data.detail)
        }
      }
    },
  },
}
</script>

<style scoped>
.pagination-wrap {
  margin-top: 20px;
  text-align: center;
}
</style>

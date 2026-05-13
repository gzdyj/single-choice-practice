<template>
  <div>
    <!-- Teacher/Admin tools -->
    <div class="toolbar" v-if="isTeacher || isAdmin">
      <el-button type="primary" icon="el-icon-plus" @click="showCreateDialog">创建考试</el-button>
      <el-button icon="el-icon-refresh" @click="fetchData">刷新</el-button>
    </div>

    <!-- Filter -->
    <el-card class="filter-card">
      <el-form :inline="true" size="small" style="margin-bottom:0">
        <el-form-item label="分类">
          <el-select v-model="filter.category_id" placeholder="全部分类" clearable style="width:160px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filter.keyword" placeholder="考试标题" clearable style="width:200px" @keyup.enter="handleFilter" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Teacher/Admin: Table view -->
    <el-card v-if="isTeacher || isAdmin">
      <el-empty v-if="!loading && exams.length === 0" description="暂无考试，点击上方创建" />
      <el-table v-if="exams.length > 0" :data="exams" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="考试标题" min-width="200">
          <template slot-scope="{ row }">
            <el-button type="text" @click="viewExam(row)">{{ row.title }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template slot-scope="{ row }">{{ row.category_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="题数" width="70" align="center">
          <template slot-scope="{ row }">{{ row.question_count }}</template>
        </el-table-column>
        <el-table-column label="时长" width="80" align="center">
          <template slot-scope="{ row }">{{ row.time_limit_minutes }}分钟</template>
        </el-table-column>
        <el-table-column label="及格分" width="80" align="center">
          <template slot-scope="{ row }">{{ row.passing_score }}分</template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template slot-scope="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '已发布' : '已关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建者" width="100">
          <template slot-scope="{ row }">{{ row.creator_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" size="small" @click="editExam(row)">编辑</el-button>
            <el-button type="text" size="small" :style="{color: row.is_active ? '#e6a23c' : '#67c23a'}" @click="toggleActive(row)">
              {{ row.is_active ? '关闭' : '发布' }}
            </el-button>
            <el-button type="text" size="small" style="color:#f56c6c" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination @current-change="handlePageChange" :current-page="page" :page-size="pageSize" layout="total, prev, pager, next" :total="total" />
      </div>
    </el-card>

    <!-- Student: Card view -->
    <div v-if="!isTeacher && !isAdmin">
      <el-empty v-if="!loading && exams.length === 0" description="暂无可用考试" />
      <el-row :gutter="20" v-loading="loading">
        <el-col :span="8" v-for="e in exams" :key="e.id" style="margin-bottom:20px">
          <el-card shadow="hover" class="exam-card">
            <div class="exam-card-title">{{ e.title }}</div>
            <div class="exam-card-desc">{{ e.description || '暂无说明' }}</div>
            <div class="exam-card-meta">
              <span>{{ e.category_name || '全部分类' }}</span>
              <span>{{ e.question_count }} 题</span>
              <span>{{ e.time_limit_minutes }} 分钟</span>
            </div>
            <div class="exam-card-footer">
              <el-button type="primary" @click="handleStart(e)">开始考试</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination @current-change="handlePageChange" :current-page="page" :page-size="pageSize" layout="total, prev, pager, next" :total="total" />
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog :title="isEditing ? '编辑考试' : '创建考试'" :visible.sync="dialogVisible" width="600px" :close-on-click-modal="false">
      <el-form :model="form" :rules="rules" ref="examForm" label-width="120px">
        <el-form-item label="考试标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入考试标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="考试说明" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="考试说明（可选）" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category_id">
              <el-select v-model="form.category_id" placeholder="全部分类" clearable style="width:100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度" prop="difficulty">
              <el-select v-model="form.difficulty" placeholder="全部难度" clearable style="width:100%">
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="题目数量" prop="question_count">
              <el-input-number v-model="form.question_count" :min="1" :max="200" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时间限制" prop="time_limit_minutes">
              <el-input-number v-model="form.time_limit_minutes" :min="1" :max="300" style="width:100%">
                <template slot="append">分钟</template>
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="及格分数" prop="passing_score">
              <el-input-number v-model="form.passing_score" :min="0" :max="100" style="width:100%">
                <template slot="append">%</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="打乱题序" prop="shuffle_questions">
              <el-switch v-model="form.shuffle_questions" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">{{ isEditing ? '保存' : '创建' }}</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getExams, createExam, updateExam, deleteExam, startExam } from '@/api/exam'
import { getAllCategories } from '@/api/category'
import { mapGetters } from 'vuex'

export default {
  name: 'ExamList',
  data() {
    return {
      exams: [],
      categories: [],
      total: 0,
      page: 1,
      pageSize: 12,
      loading: false,
      saving: false,
      filter: { category_id: '', keyword: '' },
      dialogVisible: false,
      isEditing: false,
      editingId: null,
      form: {
        title: '',
        description: '',
        category_id: null,
        difficulty: null,
        question_count: 10,
        time_limit_minutes: 30,
        passing_score: 60,
        shuffle_questions: true,
      },
      rules: {
        title: [{ required: true, message: '请输入考试标题', trigger: 'blur' }],
      },
    }
  },
  computed: { ...mapGetters(['isAdmin', 'isTeacher']) },
  created() {
    this.loadCategories()
    this.fetchData()
  },
  methods: {
    async loadCategories() {
      try {
        const res = await getAllCategories()
        this.categories = res.data
      } catch { /* ignore */ }
    },
    async fetchData() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filter.category_id) params.category_id = this.filter.category_id
        if (this.filter.keyword) params.keyword = this.filter.keyword
        const res = await getExams(params)
        this.exams = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    handleFilter() { this.page = 1; this.fetchData() },
    resetFilter() { this.filter = { category_id: '', keyword: '' }; this.page = 1; this.fetchData() },
    handlePageChange(page) { this.page = page; this.fetchData() },

    showCreateDialog() {
      this.isEditing = false
      this.editingId = null
      this.form = { title: '', description: '', category_id: null, difficulty: null, question_count: 10, time_limit_minutes: 30, passing_score: 60, shuffle_questions: true }
      this.dialogVisible = true
    },
    editExam(row) {
      this.isEditing = true
      this.editingId = row.id
      this.form = {
        title: row.title,
        description: row.description,
        category_id: row.category_id,
        difficulty: row.difficulty,
        question_count: row.question_count,
        time_limit_minutes: row.time_limit_minutes,
        passing_score: row.passing_score,
        shuffle_questions: row.shuffle_questions,
      }
      this.dialogVisible = true
    },
    async handleSave() {
      const valid = await this.$refs.examForm.validate().catch(() => false)
      if (!valid) return
      this.saving = true
      try {
        // Normalize empty strings to null
        const data = {
          ...this.form,
          category_id: this.form.category_id || null,
          difficulty: this.form.difficulty || null,
        }
        if (this.isEditing) {
          await updateExam(this.editingId, data)
          this.$message.success('考试已更新')
        } else {
          await createExam(data)
          this.$message.success('考试创建成功，已自动选题')
        }
        this.dialogVisible = false
        this.fetchData()
      } catch (err) {
        this.$message.error(err.response?.data?.detail || '操作失败')
      } finally {
        this.saving = false
      }
    },
    async toggleActive(row) {
      try {
        await updateExam(row.id, { is_active: !row.is_active })
        this.$message.success(row.is_active ? '考试已关闭' : '考试已发布')
        this.fetchData()
      } catch (err) {
        this.$message.error(err.response?.data?.detail || '操作失败')
      }
    },
    async handleDelete(row) {
      try {
        await this.$confirm(`确定删除考试「${row.title}」吗？关联的数据将被清理。`, '提示', { type: 'warning' })
        await deleteExam(row.id)
        this.$message.success('删除成功')
        this.fetchData()
      } catch { /* cancelled or error */ }
    },
    viewExam(row) {
      this.$router.push(`/exam-result/${row.id}`)
    },
    async handleStart(row) {
      try {
        const res = await startExam(row.id)
        this.$router.push({ name: 'ExamTaking', params: { attemptData: res.data } })
      } catch (err) {
        const msg = err.response?.data?.detail || '开始考试失败'
        if (msg.includes('正在进行中')) {
          this.$confirm(msg + '，是否继续？', '提示', {
            confirmButtonText: '去继续',
            cancelButtonText: '取消',
            type: 'warning',
          }).then(() => {
            this.$router.push('/exam-history')
          }).catch(() => {})
        } else {
          this.$message.error(msg)
        }
      }
    },
  },
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.filter-card { margin-bottom: 16px; }
.pagination-wrap { margin-top: 20px; text-align: center; }
.exam-card-title { font-size: 18px; font-weight: bold; color: #303133; margin-bottom: 8px; }
.exam-card-desc { font-size: 13px; color: #909399; margin-bottom: 12px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.exam-card-meta { display: flex; justify-content: space-between; color: #606266; font-size: 12px; margin-bottom: 16px; }
.exam-card-footer { text-align: center; }
</style>

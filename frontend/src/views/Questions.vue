<template>
  <div>
    <div class="toolbar" v-if="isTeacher">
      <el-button type="primary" icon="el-icon-plus" @click="$router.push('/questions/create')">新增题目</el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filter" size="small">
        <el-form-item label="分类">
          <el-select v-model="filter.category_id" placeholder="全部分类" clearable style="width: 160px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学科">
          <el-select v-model="filter.subject" placeholder="全部" clearable style="width: 150px">
            <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="filter.difficulty" placeholder="全部" clearable style="width: 120px">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filter.keyword" placeholder="题目内容/学科" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <!-- Empty state -->
      <el-empty v-if="!loading && questions.length === 0" description="暂无题目，请先导入题库">
        <el-button type="primary" @click="$router.push('/import')" v-if="isTeacher">导入题库</el-button>
        <el-button type="primary" @click="$router.push('/questions/create')" v-if="isTeacher">新增题目</el-button>
      </el-empty>

      <el-table v-if="questions.length > 0" :data="questions" v-loading="loading" stripe highlight-current-row>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="题目" min-width="350">
          <template slot-scope="{ row }">
            <div class="question-text">{{ row.question_text }}</div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template slot-scope="{ row }">
            {{ categoryName(row.category_id) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="学科" width="100" />
        <el-table-column label="难度" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="difficultyTag(row.difficulty)" size="small">{{ difficultyLabel(row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="正确答案" width="80" align="center">
          <template slot-scope="{ row }">
            <el-tag type="success" size="small">{{ row.correct_answer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" size="small" @click="viewQuestion(row)">查看</el-button>
            <el-button type="text" size="small" @click="$router.push(`/questions/edit/${row.id}`)" v-if="isTeacher">编辑</el-button>
            <el-button type="text" size="small" style="color:#f56c6c" @click="handleDelete(row)" v-if="isTeacher">删除</el-button>
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

    <!-- View Dialog -->
    <el-dialog title="题目详情" :visible.sync="viewVisible" width="700px">
      <div v-if="viewData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分类">{{ categoryName(viewData.category_id) || '未分类' }}</el-descriptions-item>
          <el-descriptions-item label="难度">{{ difficultyLabel(viewData.difficulty) }}</el-descriptions-item>
          <el-descriptions-item label="学科">{{ viewData.subject || '-' }}</el-descriptions-item>
          <el-descriptions-item label="题目" :span="2">{{ viewData.question_text }}</el-descriptions-item>
        </el-descriptions>
        <div class="options-list">
          <div :class="['option-item', { 'correct-option': viewData.correct_answer === 'A' }]">
            A. {{ viewData.option_a }}
          </div>
          <div :class="['option-item', { 'correct-option': viewData.correct_answer === 'B' }]">
            B. {{ viewData.option_b }}
          </div>
          <div :class="['option-item', { 'correct-option': viewData.correct_answer === 'C' }]">
            C. {{ viewData.option_c }}
          </div>
          <div :class="['option-item', { 'correct-option': viewData.correct_answer === 'D' }]">
            D. {{ viewData.option_d }}
          </div>
        </div>
        <div v-if="viewData.explanation" class="explanation">
          <strong>解析：</strong>{{ viewData.explanation }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getQuestions, deleteQuestion, getSubjects } from '@/api/question'
import { getAllCategories } from '@/api/category'
import { mapGetters } from 'vuex'

export default {
  name: 'Questions',
  data() {
    return {
      questions: [],
      subjects: [],
      categories: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
      filter: { category_id: '', subject: '', difficulty: '', keyword: '' },
      viewVisible: false,
      viewData: null,
    }
  },
  computed: { ...mapGetters(['isTeacher']) },
  created() {
    this.fetchSubjects()
    this.fetchCategories()
    this.fetchData()
  },
  methods: {
    async fetchSubjects() {
      try {
        const res = await getSubjects()
        this.subjects = res.data
      } catch { /* ignore */ }
    },
    async fetchCategories() {
      try {
        const res = await getAllCategories()
        this.categories = res.data
      } catch { /* ignore */ }
    },
    categoryName(categoryId) {
      if (!categoryId || !this.categories.length) return ''
      const c = this.categories.find(c => c.id === categoryId)
      return c ? c.name : ''
    },
    async fetchData() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filter.category_id) params.category_id = this.filter.category_id
        if (this.filter.subject) params.subject = this.filter.subject
        if (this.filter.difficulty) params.difficulty = this.filter.difficulty
        if (this.filter.keyword) params.keyword = this.filter.keyword
        const res = await getQuestions(params)
        this.questions = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    resetFilter() {
      this.filter = { category_id: '', subject: '', difficulty: '', keyword: '' }
      this.page = 1
      this.fetchData()
    },
    handlePageChange(page) {
      this.page = page
      this.fetchData()
    },
    viewQuestion(row) {
      this.viewData = row
      this.viewVisible = true
    },
    async handleDelete(row) {
      try {
        await this.$confirm(`确定删除题目 #${row.id} 吗？`, '提示', { type: 'warning' })
        await deleteQuestion(row.id)
        this.$message.success('删除成功')
        this.fetchData()
      } catch { /* cancelled or error */ }
    },
    difficultyLabel(d) {
      return { easy: '简单', medium: '中等', hard: '困难' }[d] || d
    },
    difficultyTag(d) {
      return { easy: 'success', medium: 'warning', hard: 'danger' }[d] || 'info'
    },
  },
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.filter-card { margin-bottom: 16px; }
.pagination-wrap { margin-top: 20px; text-align: center; }
.question-text {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.options-list { margin-top: 16px; }
.option-item {
  padding: 8px 12px;
  margin-bottom: 4px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
.correct-option {
  background-color: #f0f9eb;
  border-color: #67c23a;
}
.explanation {
  margin-top: 16px;
  padding: 12px;
  background: #fdf6ec;
  border-radius: 4px;
  color: #e6a23c;
}
</style>

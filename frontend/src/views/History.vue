<template>
  <div>
    <el-card>
      <div slot="header" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
        <span>练习记录</span>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-select v-model="filterCategoryId" placeholder="全部分类" clearable size="small" style="width:150px" @change="handleFilter">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-select v-model="filterDifficulty" placeholder="全部难度" clearable size="small" style="width:120px" @change="handleFilter">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
          <el-button type="primary" size="small" icon="el-icon-search" @click="handleFilter">筛选</el-button>
        </div>
      </div>

      <!-- Empty state -->
      <el-empty v-if="!loading && records.length === 0" description="暂无练习记录，快去刷题吧！">
        <el-button type="primary" @click="$router.push('/practice')">去刷题</el-button>
      </el-empty>

      <el-table v-if="records.length > 0" :data="records" v-loading="loading" stripe highlight-current-row>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="题目" min-width="300">
          <template slot-scope="{ row }">
            <div class="question-text">{{ row.question_text }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="学科" width="100" />
        <el-table-column label="你的答案" width="100" align="center">
          <template slot-scope="{ row }">
            <el-tag :type="row.user_answer === row.correct_answer ? 'success' : 'danger'" size="small">
              {{ row.user_answer }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="正确答案" width="100" align="center">
          <template slot-scope="{ row }">
            <el-tag type="success" size="small">{{ row.correct_answer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="80" align="center">
          <template slot-scope="{ row }">
            <i :class="row.is_correct ? 'el-icon-success' : 'el-icon-error'"
               :style="{ color: row.is_correct ? '#67c23a' : '#f56c6c', fontSize: '20px' }">
            </i>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="答题时间" width="180" />
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
  </div>
</template>

<script>
import { getHistory } from '@/api/practice'
import { getAllCategories } from '@/api/category'

export default {
  name: 'History',
  data() {
    return {
      records: [],
      categories: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
      filterCategoryId: '',
      filterDifficulty: '',
    }
  },
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
        if (this.filterCategoryId) params.category_id = this.filterCategoryId
        if (this.filterDifficulty) params.difficulty = this.filterDifficulty
        const res = await getHistory(params)
        this.records = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.page = 1
      this.fetchData()
    },
    handlePageChange(page) {
      this.page = page
      this.fetchData()
    },
  },
}
</script>

<style scoped>
.question-text {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.pagination-wrap {
  margin-top: 20px;
  text-align: center;
}
</style>

<template>
  <div>
    <el-card>
      <div slot="header" style="display:flex;align-items:center;justify-content:space-between">
        <span>考试记录</span>
        <el-button size="small" icon="el-icon-refresh" @click="fetchData">刷新</el-button>
      </div>

      <el-empty v-if="!loading && records.length === 0" description="暂无考试记录">
        <el-button type="primary" @click="$router.push('/exams')">去参加考试</el-button>
      </el-empty>

      <el-table v-if="records.length > 0" :data="records" v-loading="loading" stripe>
        <el-table-column prop="exam_title" label="考试名称" min-width="200" />
        <el-table-column label="状态" width="100" align="center">
          <template slot-scope="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="80" align="center">
          <template slot-scope="{ row }">
            <span v-if="row.score !== null" :style="{ color: row.passed ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
              {{ row.score }}分
            </span>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="100" align="center">
          <template slot-scope="{ row }">
            <span v-if="row.correct_count !== null">
              {{ row.correct_count }}/{{ row.total_questions }}
            </span>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="80" align="center">
          <template slot-scope="{ row }">
            <i v-if="row.passed === true" class="el-icon-success" style="color:#67c23a;font-size:20px"></i>
            <i v-else-if="row.passed === false" class="el-icon-error" style="color:#f56c6c;font-size:20px"></i>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="170">
          <template slot-scope="{ row }">{{ row.started_at }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template slot-scope="{ row }">
            <el-button type="text" size="small" @click="viewResult(row)" :disabled="row.status === 'in_progress'">
              查看结果
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination @current-change="handlePageChange" :current-page="page" :page-size="pageSize" layout="total, prev, pager, next" :total="total" />
      </div>
    </el-card>
  </div>
</template>

<script>
import { getMyExamAttempts } from '@/api/exam'

export default {
  name: 'ExamHistory',
  data() {
    return {
      records: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const res = await getMyExamAttempts({ page: this.page, page_size: this.pageSize })
        this.records = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) { this.page = page; this.fetchData() },
    viewResult(row) {
      this.$router.push({ name: 'ExamResult', params: { attemptId: row.attempt_id } })
    },
    statusLabel(s) {
      return { in_progress: '进行中', submitted: '已交卷', timed_out: '超时' }[s] || s
    },
    statusTag(s) {
      return { in_progress: 'warning', submitted: 'success', timed_out: 'danger' }[s] || 'info'
    },
  },
}
</script>

<style scoped>
.pagination-wrap { margin-top: 20px; text-align: center; }
</style>

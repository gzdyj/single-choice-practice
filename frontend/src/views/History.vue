<template>
  <div>
    <el-card>
      <div slot="header">
        <span>练习记录</span>
      </div>

      <el-table :data="records" v-loading="loading" stripe highlight-current-row>
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

export default {
  name: 'History',
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
        const res = await getHistory({ page: this.page, page_size: this.pageSize })
        this.records = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
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

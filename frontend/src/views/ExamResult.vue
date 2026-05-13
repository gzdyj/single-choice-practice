<template>
  <div class="exam-result-page" v-loading="loading">
    <!-- Result header -->
    <el-card class="result-header" :class="passed ? 'result-passed' : 'result-failed'">
      <div class="result-icon">
        <i :class="passed ? 'el-icon-success' : 'el-icon-error'"></i>
      </div>
      <div class="result-title">{{ passed ? '恭喜通过！' : '未通过' }}</div>
      <div class="result-subtitle">{{ result.exam_title }}</div>
      <div class="result-scores">
        <div class="score-item">
          <div class="score-value" :style="{ color: passed ? '#67c23a' : '#f56c6c' }">{{ result.score }}</div>
          <div class="score-label">得分（分）</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
          <div class="score-value">{{ result.correct_count }}/{{ result.total_questions }}</div>
          <div class="score-label">正确</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
          <div class="score-value">{{ formatTime(result.time_used_seconds) }}</div>
          <div class="score-label">用时</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
          <div class="score-value">{{ result.passing_score }}分</div>
          <div class="score-label">及格线</div>
        </div>
      </div>
    </el-card>

    <!-- Answer review -->
    <el-card class="answer-review">
      <div slot="header">详细答案</div>
      <div v-for="(ans, idx) in result.answers" :key="ans.question_id" class="answer-item">
        <div class="answer-header">
          <span class="answer-number">第 {{ idx + 1 }} 题</span>
          <el-tag :type="diffTag(ans.difficulty)" size="mini">{{ diffLabel(ans.difficulty) }}</el-tag>
          <span v-if="ans.subject" style="margin-left:8px;color:#909399;font-size:12px">{{ ans.subject }}</span>
          <el-tag :type="ans.is_correct ? 'success' : 'danger'" size="mini" style="margin-left:auto">
            {{ ans.is_correct ? '正确' : '错误' }}
          </el-tag>
        </div>
        <div class="answer-question">{{ ans.question_text }}</div>
        <div class="answer-options">
          <div :class="['opt', optClass(ans, 'A')]">A. {{ ans.option_a }}</div>
          <div :class="['opt', optClass(ans, 'B')]">B. {{ ans.option_b }}</div>
          <div :class="['opt', optClass(ans, 'C')]">C. {{ ans.option_c }}</div>
          <div :class="['opt', optClass(ans, 'D')]">D. {{ ans.option_d }}</div>
        </div>
        <div class="answer-summary">
          <span v-if="!ans.selected_answer" style="color:#f56c6c">未作答</span>
          <span v-else>
            你的答案：<el-tag :type="ans.is_correct ? 'success' : 'danger'" size="mini">{{ ans.selected_answer }}</el-tag>
          </span>
          <span style="margin-left:16px">
            正确答案：<el-tag type="success" size="mini">{{ ans.correct_answer }}</el-tag>
          </span>
        </div>
      </div>
    </el-card>

    <!-- Actions -->
    <div class="result-actions">
      <el-button type="primary" @click="$router.push('/exams')">返回考试列表</el-button>
      <el-button @click="$router.push('/exam-history')">查看考试记录</el-button>
    </div>
  </div>
</template>

<script>
import { getExamResult } from '@/api/exam'

export default {
  name: 'ExamResult',
  data() {
    return {
      result: { answers: [], score: 0, correct_count: 0, total_questions: 0, passing_score: 60, passed: false, time_used_seconds: 0, exam_title: '' },
      loading: false,
    }
  },
  computed: {
    passed() { return this.result.passed },
  },
  created() {
    const data = this.$route.params?.resultData
    if (data) {
      this.result = data
    } else {
      // Fetch from API if navigated directly
      this.fetchResult()
    }
  },
  methods: {
    async fetchResult() {
      const attemptId = this.$route.params?.attemptId || this.$route.query?.attemptId
      if (!attemptId) {
        this.$router.push('/exams')
        return
      }
      this.loading = true
      try {
        const res = await getExamResult(attemptId)
        this.result = res.data
      } catch {
        this.$message.error('获取考试结果失败')
        this.$router.push('/exams')
      } finally {
        this.loading = false
      }
    },
    formatTime(seconds) {
      if (!seconds && seconds !== 0) return '-'
      const m = Math.floor(seconds / 60)
      const s = seconds % 60
      return `${m}分${s}秒`
    },
    optClass(ans, key) {
      if (ans.correct_answer === key) return 'opt-correct'
      if (ans.selected_answer === key && key !== ans.correct_answer) return 'opt-wrong'
      return ''
    },
    diffLabel(d) { return { easy: '简单', medium: '中等', hard: '困难' }[d] || d },
    diffTag(d) { return { easy: 'success', medium: 'warning', hard: 'danger' }[d] || 'info' },
  },
}
</script>

<style scoped>
.exam-result-page { max-width: 800px; margin: 0 auto; }
.result-header { text-align: center; padding: 40px 20px; margin-bottom: 20px; border: none; }
.result-passed { background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%); }
.result-failed { background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%); }
.result-icon { font-size: 64px; margin-bottom: 16px; }
.result-passed .result-icon { color: #67c23a; }
.result-failed .result-icon { color: #f56c6c; }
.result-title { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
.result-subtitle { font-size: 16px; color: #909399; margin-bottom: 24px; }
.result-scores { display: flex; justify-content: center; align-items: center; gap: 0; }
.score-item { padding: 0 30px; }
.score-value { font-size: 32px; font-weight: bold; }
.score-label { font-size: 13px; color: #909399; margin-top: 4px; }
.score-divider { width: 1px; height: 50px; background: #dcdfe6; }

.answer-review { margin-bottom: 20px; }
.answer-item { padding: 16px; border-bottom: 1px solid #f0f0f0; }
.answer-item:last-child { border-bottom: none; }
.answer-header { display: flex; align-items: center; margin-bottom: 8px; gap: 8px; }
.answer-number { font-size: 14px; font-weight: bold; color: #303133; }
.answer-question { font-size: 16px; color: #303133; margin-bottom: 12px; line-height: 1.5; }
.answer-options { margin-bottom: 12px; }
.opt { padding: 6px 10px; margin-bottom: 4px; border: 1px solid #e8e8e8; border-radius: 4px; font-size: 14px; }
.opt-correct { background: #f0f9eb; border-color: #67c23a; }
.opt-wrong { background: #fef0f0; border-color: #f56c6c; }
.answer-summary { font-size: 13px; color: #606266; }
.result-actions { text-align: center; margin-bottom: 40px; }
</style>

<template>
  <div class="exam-taking-page">
    <!-- Top bar: Timer + Exam info -->
    <el-card class="exam-topbar" shadow="always">
      <div class="topbar-inner">
        <div class="topbar-left">
          <span class="exam-title">{{ examData.exam_title }}</span>
          <el-tag size="small" type="info" v-if="examData.exam_description" style="margin-left:8px">
            {{ examData.exam_description }}
          </el-tag>
        </div>
        <div class="topbar-right">
          <div class="progress-info">
            第 {{ currentIndex + 1 }} / {{ questions.length }} 题
          </div>
          <div :class="['timer', { 'timer-warning': remainingTime <= 120 }]">
            <i class="el-icon-time"></i>
            {{ formattedTime }}
          </div>
          <el-button type="danger" size="small" @click="confirmSubmit" :disabled="submitting">
            {{ submitting ? '提交中...' : '交卷' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Progress bar -->
    <div class="progress-bar-wrapper">
      <div class="progress-dots">
        <div
          v-for="(q, idx) in questions"
          :key="q.question_id"
          :class="['dot', dotClass(idx)]"
          @click="goToQuestion(idx)"
          :title="'第' + (idx+1) + '题'"
        >
          {{ idx + 1 }}
        </div>
      </div>
    </div>

    <!-- Question card -->
    <el-card class="question-card" v-if="currentQuestion">
      <!-- Question text -->
      <div class="question-header">
        <el-tag :type="difficultyTag(currentQuestion.difficulty)" size="small">
          {{ difficultyLabel(currentQuestion.difficulty) }}
        </el-tag>
        <span style="margin-left:8px;color:#909399;font-size:12px" v-if="currentQuestion.subject">
          {{ currentQuestion.subject }}
        </span>
      </div>
      <div class="question-text">{{ currentQuestion.question_text }}</div>

      <!-- Options -->
      <div class="options">
        <div
          v-for="opt in questionOptions"
          :key="opt.key"
          :class="['option', { 'option-selected': answers[currentQuestion.question_id] === opt.key }]"
          @click="selectOption(currentQuestion.question_id, opt.key)"
        >
          <span class="option-key">{{ opt.key }}.</span>
          <span class="option-content">{{ opt.value }}</span>
        </div>
      </div>

      <!-- Navigation -->
      <div class="question-nav">
        <el-button @click="prevQuestion" :disabled="currentIndex === 0">上一题</el-button>
        <el-button type="primary" @click="nextQuestion" v-if="currentIndex < questions.length - 1">
          下一题
        </el-button>
        <el-button type="success" v-else @click="confirmSubmit">
          完成！去交卷
        </el-button>
      </div>
    </el-card>

    <!-- Submit confirm dialog -->
    <el-dialog title="确认交卷" :visible.sync="submitDialogVisible" width="400px">
      <div style="text-align:center;padding:20px 0">
        <div style="font-size:48px;color:#e6a23c;margin-bottom:16px">
          <i class="el-icon-warning-outline"></i>
        </div>
        <p style="font-size:16px;margin-bottom:8px">你确定要交卷吗？</p>
        <p style="color:#909399">
          已作答 {{ answeredCount }} / {{ questions.length }} 题
          <span v-if="unansweredCount > 0" style="color:#f56c6c">（{{ unansweredCount }} 题未作答）</span>
        </p>
      </div>
      <span slot="footer">
        <el-button @click="submitDialogVisible = false">继续答题</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确认交卷</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { submitExam } from '@/api/exam'

export default {
  name: 'ExamTaking',
  data() {
    return {
      examData: {},
      questions: [],
      answers: {},        // { question_id: 'A'|'B'|... }
      attemptId: null,
      currentIndex: 0,
      remainingTime: 0,   // seconds
      timerInterval: null,
      submitting: false,
      submitDialogVisible: false,
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || null
    },
    questionOptions() {
      if (!this.currentQuestion) return []
      return [
        { key: 'A', value: this.currentQuestion.option_a },
        { key: 'B', value: this.currentQuestion.option_b },
        { key: 'C', value: this.currentQuestion.option_c },
        { key: 'D', value: this.currentQuestion.option_d },
      ]
    },
    answeredCount() {
      return Object.keys(this.answers).filter(k => this.answers[k]).length
    },
    unansweredCount() {
      return this.questions.length - this.answeredCount
    },
    formattedTime() {
      const m = Math.floor(this.remainingTime / 60)
      const s = this.remainingTime % 60
      return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    },
  },
  created() {
    const data = this.$route.params?.attemptData || {}
    this.examData = data
    this.questions = data.questions || []
    this.attemptId = data.attempt_id
    this.remainingTime = (data.time_limit_minutes || 0) * 60
    this.currentIndex = 0

    // Initialize answers from URL params (restore state)
    const saved = parseInt(localStorage.getItem(`exam_${this.attemptId}_state`))
    if (saved) {
      try {
        const state = JSON.parse(sessionStorage.getItem(`exam_${this.attemptId}_state`))
        if (state && state.answers) {
          this.answers = state.answers
          this.currentIndex = state.currentIndex || 0
          this.remainingTime = state.remainingTime
        }
      } catch { /* ignore */ }
    }

    // If no redirect from exam list, try to get data from query
    if (!this.attemptId) {
      this.$message.error('考试数据异常，请重新开始')
      this.$router.push('/exams')
      return
    }

    this.startTimer()
  },
  beforeDestroy() {
    this.saveState()
    this.clearTimer()
  },
  methods: {
    startTimer() {
      // Use end timestamp to persist across refreshes
      const endKey = `exam_${this.attemptId}_end`
      let endTime = parseInt(localStorage.getItem(endKey))
      if (!endTime) {
        endTime = Date.now() + this.remainingTime * 1000
        localStorage.setItem(endKey, endTime)
      }

      // Recalculate remaining time from stored end time
      this.remainingTime = Math.max(0, Math.floor((endTime - Date.now()) / 1000))

      this.clearTimer()
      this.timerInterval = setInterval(() => {
        this.remainingTime = Math.max(0, Math.floor((endTime - Date.now()) / 1000))
        this.saveState()
        if (this.remainingTime <= 0) {
          this.clearTimer()
          this.$message.warning('考试时间到，自动交卷')
          this.handleSubmit()
        }
      }, 1000)
    },
    clearTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    },
    saveState() {
      if (!this.attemptId) return
      const state = JSON.stringify({ answers: this.answers, currentIndex: this.currentIndex, remainingTime: this.remainingTime })
      sessionStorage.setItem(`exam_${this.attemptId}_state`, state)
    },
    selectOption(questionId, key) {
      this.$set(this.answers, questionId, key)
      this.saveState()
    },
    goToQuestion(idx) {
      this.currentIndex = idx
    },
    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.saveState()
      }
    },
    prevQuestion() {
      if (this.currentIndex > 0) {
        this.currentIndex--
        this.saveState()
      }
    },
    dotClass(idx) {
      const qId = this.questions[idx]?.question_id
      if (this.answers[qId]) return 'dot-answered'
      if (idx === this.currentIndex) return 'dot-current'
      return 'dot-unanswered'
    },
    confirmSubmit() {
      this.submitDialogVisible = true
    },
    async handleSubmit() {
      if (this.submitting) return
      this.submitting = true
      this.clearTimer()
      try {
        const answers = this.questions.map(q => ({
          question_id: q.question_id,
          selected_answer: this.answers[q.question_id] || null,
        }))
        const res = await submitExam(this.examData.exam_id, answers)

        // Clean up storage
        localStorage.removeItem(`exam_${this.attemptId}_end`)
        sessionStorage.removeItem(`exam_${this.attemptId}_state`)

        this.$router.replace({
          name: 'ExamResult',
          params: { resultData: res.data },
        })
      } catch (err) {
        const msg = err.response?.data?.detail || '提交失败'
        // If timed out, try to get the result anyway
        if (msg.includes('超时')) {
          this.$router.push('/exam-history')
        } else {
          this.$message.error(msg)
          this.startTimer() // resume timer on failure
        }
      } finally {
        this.submitting = false
        this.submitDialogVisible = false
      }
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
.exam-taking-page { max-width: 900px; margin: 0 auto; }
.exam-topbar { margin-bottom: 16px; position: sticky; top: 0; z-index: 100; }
.topbar-inner { display: flex; align-items: center; justify-content: space-between; }
.topbar-left { display: flex; align-items: center; }
.exam-title { font-size: 16px; font-weight: bold; color: #303133; }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.progress-info { font-size: 14px; color: #606266; }
.timer { font-size: 24px; font-weight: bold; color: #409eff; font-variant-numeric: tabular-nums; min-width: 80px; text-align: center; }
.timer-warning { color: #f56c6c; animation: pulse 1s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.progress-bar-wrapper { margin-bottom: 16px; }
.progress-dots { display: flex; flex-wrap: wrap; gap: 6px; }
.dot {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; cursor: pointer; transition: all 0.2s;
  border: 2px solid #dcdfe6; color: #909399; background: #fff;
}
.dot:hover { border-color: #409eff; }
.dot-current { border-color: #409eff; color: #409eff; font-weight: bold; }
.dot-answered { border-color: #67c23a; color: #fff; background: #67c23a; }
.dot-unanswered { }

.question-card { margin-bottom: 20px; }
.question-header { margin-bottom: 12px; display: flex; align-items: center; }
.question-text {
  font-size: 18px; color: #303133; line-height: 1.6;
  margin-bottom: 20px; padding: 12px;
  background: #fafafa; border-radius: 4px;
}
.options { margin-bottom: 20px; }
.option {
  padding: 12px 16px; margin-bottom: 8px;
  border: 1px solid #dcdfe6; border-radius: 6px;
  cursor: pointer; transition: all 0.2s;
  display: flex; align-items: center;
}
.option:hover { border-color: #409eff; }
.option-selected { border-color: #409eff; background: #ecf5ff; }
.option-key { font-weight: bold; margin-right: 8px; }
.option-content { flex: 1; }
.question-nav { text-align: center; }
</style>

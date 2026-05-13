<template>
  <div class="practice-page">
    <!-- Stats -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">总答题数</div>
            <div class="stat-value">{{ stats.total_attempts }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">答对</div>
            <div class="stat-value" style="color: #67c23a">{{ stats.correct_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">答错</div>
            <div class="stat-value" style="color: #f56c6c">{{ stats.wrong_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">正确率</div>
            <div class="stat-value" style="color: #409eff">{{ stats.accuracy }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <el-card class="filter-card">
      <el-form :inline="true" size="small" style="margin-bottom:0">
        <el-form-item label="分类">
          <el-select v-model="filterCategoryId" placeholder="全部分类" clearable style="width:160px" @change="nextQuestion">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="filterDifficulty" placeholder="全部难度" clearable style="width:120px" @change="nextQuestion">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Question Card -->
    <el-card v-if="question" class="question-card">
      <div class="question-header">
        <el-tag size="small" type="info">{{ categoryName(question.category_id) || question.subject || '未分类' }}</el-tag>
        <el-tag :type="difficultyTag(question.difficulty)" size="small" style="margin-left: 8px">
          {{ difficultyLabel(question.difficulty) }}
        </el-tag>
        <span class="question-number">#{{ question.id }}</span>
      </div>

      <div class="question-text">{{ question.question_text }}</div>

      <div class="options">
        <div
          v-for="opt in options"
          :key="opt.key"
          :class="['option', optionClass(opt.key)]"
          @click="selectOption(opt.key)"
        >
          <span class="option-key">{{ opt.key }}.</span>
          <span class="option-content">{{ opt.value }}</span>
          <i v-if="answered && question.correct_answer === opt.key" class="el-icon-success option-icon correct-icon"></i>
          <i v-else-if="answered && selected === opt.key && selected !== question.correct_answer" class="el-icon-error option-icon wrong-icon"></i>
        </div>
      </div>

      <!-- Result feedback -->
      <div v-if="answered" class="result-feedback">
        <el-alert
          :type="isCorrect ? 'success' : 'error'"
          :closable="false"
          show-icon
        >
          <template slot="title">
            {{ isCorrect ? '✓ 回答正确！' : '✗ 回答错误' }}
          </template>
        </el-alert>
        <div v-if="question.explanation" class="explanation">
          <strong>解析：</strong>{{ question.explanation }}
        </div>
      </div>

      <div class="question-actions">
        <el-button
          type="primary"
          :disabled="!selected"
          @click="submitAnswer"
          v-if="!answered"
        >提交答案</el-button>
        <el-button type="success" @click="nextQuestion" v-else>
          {{ noMore ? '恭喜，所有题目已答对！' : '下一题' }}
        </el-button>
      </div>
    </el-card>

    <!-- No question state -->
    <el-card v-else class="question-card empty-state">
      <el-empty description="暂无题目">
        <el-button type="primary" @click="nextQuestion">随机抽题</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script>
import { getRandomQuestion, submitAnswer, getStats } from '@/api/practice'
import { getAllCategories } from '@/api/category'

export default {
  name: 'Practice',
  data() {
    return {
      question: null,
      selected: '',
      answered: false,
      isCorrect: false,
      noMore: false,
      categories: [],
      filterCategoryId: '',
      filterDifficulty: '',
      stats: { total_attempts: 0, correct_count: 0, wrong_count: 0, accuracy: 0 },
      options: [
        { key: 'A', value: '' },
        { key: 'B', value: '' },
        { key: 'C', value: '' },
        { key: 'D', value: '' },
      ],
    }
  },
  created() {
    this.loadStats()
    this.loadCategories()
    this.nextQuestion()
  },
  methods: {
    async loadCategories() {
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
    async loadStats() {
      try {
        const res = await getStats()
        this.stats = res.data
      } catch { /* ignore */ }
    },
    async nextQuestion() {
      this.selected = ''
      this.answered = false
      this.isCorrect = false
      this.noMore = false
      try {
        const params = {}
        if (this.filterCategoryId) params.category_id = this.filterCategoryId
        if (this.filterDifficulty) params.difficulty = this.filterDifficulty
        const res = await getRandomQuestion(params)
        this.question = res.data
        this.options = [
          { key: 'A', value: this.question.option_a },
          { key: 'B', value: this.question.option_b },
          { key: 'C', value: this.question.option_c },
          { key: 'D', value: this.question.option_d },
        ]
      } catch (err) {
        if (err.response?.status === 404) {
          this.noMore = true
          this.question = null
        }
      }
    },
    selectOption(key) {
      if (this.answered) return
      this.selected = key
    },
    optionClass(key) {
      if (!this.answered) {
        return this.selected === key ? 'option-selected' : ''
      }
      if (this.question.correct_answer === key) {
        return 'option-correct'
      }
      if (this.selected === key && key !== this.question.correct_answer) {
        return 'option-wrong'
      }
      return ''
    },
    async submitAnswer() {
      if (!this.selected) return
      try {
        const res = await submitAnswer({ question_id: this.question.id, user_answer: this.selected })
        this.isCorrect = res.data.is_correct
        this.answered = true
        this.loadStats()
      } catch { /* ignore */ }
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
.stat-item { text-align: center; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #303133; }
.question-card { max-width: 800px; margin: 0 auto; }
.question-header { margin-bottom: 16px; display: flex; align-items: center; }
.question-number { margin-left: auto; color: #909399; font-size: 12px; }
.question-text {
  font-size: 18px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
}
.options { margin-bottom: 20px; }
.option {
  padding: 12px 16px;
  margin-bottom: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}
.option:hover { border-color: #409eff; }
.option-selected { border-color: #409eff; background: #ecf5ff; }
.option-correct { border-color: #67c23a; background: #f0f9eb; }
.option-wrong { border-color: #f56c6c; background: #fef0f0; }
.option-key { font-weight: bold; margin-right: 8px; }
.option-content { flex: 1; }
.option-icon { font-size: 18px; }
.correct-icon { color: #67c23a; }
.wrong-icon { color: #f56c6c; }
.result-feedback { margin-bottom: 20px; }
.explanation {
  margin-top: 12px;
  padding: 12px;
  background: #fdf6ec;
  border-radius: 4px;
  color: #e6a23c;
  font-size: 14px;
}
.question-actions { text-align: center; }
.empty-state { text-align: center; padding: 60px 0; }
.filter-card { max-width: 800px; margin: 0 auto 16px; }
</style>

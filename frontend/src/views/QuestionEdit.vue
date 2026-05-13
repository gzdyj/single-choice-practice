<template>
  <el-card>
    <div slot="header">
      <span>{{ isEdit ? '编辑题目' : '新增题目' }}</span>
    </div>

    <el-form ref="form" :model="form" :rules="rules" label-width="100px" style="max-width: 800px">
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 250px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <span style="margin-left:8px;color:#909399;font-size:12px">若没有合适的分类，请先到分类管理添加</span>
      </el-form-item>
      <el-form-item label="学科标签">
        <el-input v-model="form.subject" placeholder="保留原有学科作为标签（选填）" maxlength="64" />
      </el-form-item>
      <el-form-item label="难度" prop="difficulty">
        <el-select v-model="form.difficulty" style="width: 200px">
          <el-option label="简单" value="easy" />
          <el-option label="中等" value="medium" />
          <el-option label="困难" value="hard" />
        </el-select>
      </el-form-item>
      <el-form-item label="题目内容" prop="question_text">
        <el-input type="textarea" v-model="form.question_text" :rows="3" placeholder="请输入题目" />
      </el-form-item>
      <el-form-item label="选项 A" prop="option_a">
        <el-input v-model="form.option_a" placeholder="选项 A 的内容" />
      </el-form-item>
      <el-form-item label="选项 B" prop="option_b">
        <el-input v-model="form.option_b" placeholder="选项 B 的内容" />
      </el-form-item>
      <el-form-item label="选项 C" prop="option_c">
        <el-input v-model="form.option_c" placeholder="选项 C 的内容" />
      </el-form-item>
      <el-form-item label="选项 D" prop="option_d">
        <el-input v-model="form.option_d" placeholder="选项 D 的内容" />
      </el-form-item>
      <el-form-item label="正确答案" prop="correct_answer">
        <el-radio-group v-model="form.correct_answer">
          <el-radio label="A">A</el-radio>
          <el-radio label="B">B</el-radio>
          <el-radio label="C">C</el-radio>
          <el-radio label="D">D</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="题目解析">
        <el-input type="textarea" v-model="form.explanation" :rows="2" placeholder="题目解析（选填）" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { createQuestion, getQuestion, updateQuestion } from '@/api/question'
import { getAllCategories } from '@/api/category'

export default {
  name: 'QuestionEdit',
  data() {
    return {
      isEdit: false,
      questionId: null,
      categories: [],
      submitLoading: false,
      form: {
        category_id: null,
        subject: '',
        difficulty: 'medium',
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_answer: 'A',
        explanation: '',
      },
      rules: {
        question_text: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
        option_a: [{ required: true, message: '请输入选项 A', trigger: 'blur' }],
        option_b: [{ required: true, message: '请输入选项 B', trigger: 'blur' }],
        option_c: [{ required: true, message: '请输入选项 C', trigger: 'blur' }],
        option_d: [{ required: true, message: '请输入选项 D', trigger: 'blur' }],
        correct_answer: [{ required: true, message: '请选择正确答案', trigger: 'change' }],
      },
    }
  },
  created() {
    this.loadCategories()
    const id = this.$route.params.id
    if (id) {
      this.isEdit = true
      this.questionId = Number(id)
      this.loadQuestion()
    }
  },
  methods: {
    async loadCategories() {
      try {
        const res = await getAllCategories()
        this.categories = res.data
      } catch { /* ignore */ }
    },
    async loadQuestion() {
      try {
        const res = await getQuestion(this.questionId)
        const q = res.data
        this.form = {
          category_id: q.category_id || null,
          subject: q.subject || '',
          difficulty: q.difficulty,
          question_text: q.question_text,
          option_a: q.option_a,
          option_b: q.option_b,
          option_c: q.option_c,
          option_d: q.option_d,
          correct_answer: q.correct_answer,
          explanation: q.explanation,
        }
      } catch {
        this.$message.error('加载题目失败')
        this.$router.push('/questions')
      }
    },
    async handleSubmit() {
      const valid = await this.$refs.form.validate().catch(() => false)
      if (!valid) return
      this.submitLoading = true
      try {
        if (this.isEdit) {
          await updateQuestion(this.questionId, this.form)
          this.$message.success('更新成功')
        } else {
          await createQuestion(this.form)
          this.$message.success('创建成功')
        }
        this.$router.push('/questions')
      } catch {
        // handled by interceptor
      } finally {
        this.submitLoading = false
      }
    },
  },
}
</script>

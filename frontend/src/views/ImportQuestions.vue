<template>
  <div>
    <el-card>
      <div slot="header">
        <span>题库导入</span>
      </div>

      <el-alert
        title="支持格式说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template slot>
          <p>支持的导入格式：<el-tag type="success" size="small" v-for="fmt in supportedFormats" :key="fmt" style="margin-right: 4px">{{ fmt }}</el-tag></p>
          <p>文件要求：表头需包含字段名（不区分大小写）：question_text, option_a, option_b, option_c, option_d, correct_answer, subject, difficulty, explanation</p>
          <p>correct_answer 取值范围：A / B / C / D</p>
          <p>difficulty 取值范围：easy / medium / hard（可选，默认 medium）</p>
        </template>
      </el-alert>

      <!-- Upload -->
      <el-upload
        ref="upload"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        accept=".xlsx,.xls,.csv,.json"
        :auto-upload="false"
        :show-file-list="true"
        drag
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击选择文件</em></div>
        <div class="el-upload__tip" slot="tip">仅支持 .xlsx / .xls / .csv / .json 格式，单次导入最大 50MB</div>
      </el-upload>

      <div style="margin-top: 20px; text-align: center">
        <el-button type="primary" icon="el-icon-upload2" :loading="uploading" @click="submitUpload">
          开始导入
        </el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>

    <!-- Result Dialog -->
    <el-dialog title="导入结果" :visible.sync="resultVisible" width="600px">
      <el-alert
        v-if="importResult"
        :type="importResult.fail_count > 0 ? 'warning' : 'success'"
        :closable="false"
        show-icon
      >
        <template slot>
          <p>成功导入：<strong style="color: #67c23a">{{ importResult.success_count }}</strong> 条</p>
          <p v-if="importResult.fail_count > 0">导入失败：<strong style="color: #f56c6c">{{ importResult.fail_count }}</strong> 条</p>
        </template>
      </el-alert>

      <div v-if="importResult && importResult.errors.length > 0" style="margin-top: 12px">
        <p><strong>错误详情：</strong></p>
        <el-table :data="importResult.errors.map((e, i) => ({ idx: i + 1, msg: e }))" size="small" max-height="300">
          <el-table-column prop="idx" label="#" width="50" />
          <el-table-column prop="msg" label="错误信息" />
        </el-table>
      </div>

      <span slot="footer">
        <el-button type="primary" @click="resultVisible = false">确定</el-button>
      </span>
    </el-dialog>

    <!-- Download template -->
    <el-card style="margin-top: 20px">
      <div slot="header"><span>模板下载</span></div>
      <p>可下载导入模板，按模板格式填写后进行导入：</p>
      <el-button type="success" icon="el-icon-download" @click="downloadTemplate">下载 Excel 模板</el-button>
    </el-card>
  </div>
</template>

<script>
import { getImportFormats } from '@/api/import_'

export default {
  name: 'ImportQuestions',
  data() {
    return {
      supportedFormats: [],
      uploading: false,
      resultVisible: false,
      importResult: null,
    }
  },
  computed: {
    uploadUrl() {
      return `${window.location.protocol}//${window.location.host}/api/questions/import`
    },
    uploadHeaders() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },
  },
  created() {
    this.fetchFormats()
  },
  methods: {
    async fetchFormats() {
      try {
        const res = await getImportFormats()
        this.supportedFormats = res.data.formats
      } catch {
        this.supportedFormats = ['.xlsx', '.csv', '.json']
      }
    },
    beforeUpload(file) {
      this.uploading = true
      return true
    },
    submitUpload() {
      if (!this.$refs.upload.uploadFiles.length) {
        this.$message.warning('请先选择文件')
        return
      }
      this.$refs.upload.submit()
    },
    handleSuccess(response) {
      this.uploading = false
      this.importResult = response
      this.$refs.upload.clearFiles()
      this.resultVisible = true
      if (response.success_count > 0) {
        this.$message.success(`成功导入 ${response.success_count} 道题目`)
      }
    },
    handleError(err) {
      this.uploading = false
      this.$refs.upload.clearFiles()
      this.$message.error('导入失败，请检查文件格式')
    },
    downloadTemplate() {
      /* Generate a simple xlsx template */
      const XLSX_DATA = [
        ['subject', 'difficulty', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation'],
        ['数学', 'easy', '1+1=？', '1', '2', '3', '4', 'B', '1+1=2，故选B'],
        ['英语', 'medium', 'What is the meaning of "apple"?', '香蕉', '苹果', '橘子', '葡萄', 'B', 'Apple 意为苹果'],
      ]
      // Use a minimal CSV for template since we can't generate xlsx in browser without a lib
      const csvContent = XLSX_DATA.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = '导入模板.csv'
      link.click()
      URL.revokeObjectURL(link.href)
    },
  },
}
</script>

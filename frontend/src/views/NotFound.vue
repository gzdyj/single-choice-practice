<template>
  <div class="not-found-container">
    <el-result icon="warning" title="404" subTitle="页面不存在">
      <template slot="extra">
        <el-button type="primary" @click="$router.push('/practice')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
</style>

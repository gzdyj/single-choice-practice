<template>
  <el-container style="min-height: 100vh">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-header">
        <span v-show="!sidebarCollapsed" class="sidebar-title">刷题系统</span>
        <span v-show="sidebarCollapsed" class="sidebar-title">S</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/practice">
          <i class="el-icon-edit"></i>
          <span slot="title">刷题练习</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <i class="el-icon-time"></i>
          <span slot="title">练习记录</span>
        </el-menu-item>
        <el-submenu v-if="isTeacher" index="question-mgmt">
          <template slot="title">
            <i class="el-icon-document"></i>
            <span slot="title">题库管理</span>
          </template>
          <el-menu-item index="/questions">题目列表</el-menu-item>
          <el-menu-item index="/questions/create">新增题目</el-menu-item>
          <el-menu-item index="/import">题库导入</el-menu-item>
        </el-submenu>
        <el-menu-item v-if="isAdmin" index="/users">
          <i class="el-icon-user"></i>
          <span slot="title">用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <!-- Header -->
      <el-header class="header">
        <div class="header-left">
          <i :class="toggleIcon" class="toggle-btn" @click="toggleSidebar"></i>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              {{ userInfo?.nickname || userInfo?.username }}
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item disabled>
                <span style="color: #909399">{{ roleName }}</span>
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'Layout',
  computed: {
    ...mapState('app', ['sidebarCollapsed']),
    ...mapState('user', ['userInfo']),
    ...mapGetters(['isAdmin', 'isTeacher', 'roleName']),
    sidebarWidth() {
      return this.sidebarCollapsed ? '64px' : '220px'
    },
    toggleIcon() {
      return this.sidebarCollapsed ? 'el-icon-s-unfold' : 'el-icon-s-fold'
    },
    activeMenu() {
      return this.$route.path
    },
  },
  methods: {
    ...mapActions('app', ['toggleSidebar']),
    handleCommand(command) {
      if (command === 'logout') {
        this.$store.dispatch('user/logout')
        this.$router.push('/login')
        this.$message.success('已退出登录')
      }
    },
  },
}
</script>

<style scoped>
.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.sidebar-header {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.header-left {
  display: flex;
  align-items: center;
}
.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}
.toggle-btn:hover {
  color: #409eff;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-dropdown {
  cursor: pointer;
  color: #303133;
  font-size: 14px;
}
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
.el-menu {
  border-right: none;
}
</style>

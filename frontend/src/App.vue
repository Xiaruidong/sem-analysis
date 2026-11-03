<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>金相晶粒识别系统</h1>
          <el-menu mode="horizontal" :default-active="currentPath" router>
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/analysis">图像分析</el-menu-item>
            <el-menu-item index="/history">历史记录</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPath = computed(() => route.path)
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0 40px 0 20px;
  font-size: 24px;
}

.el-menu {
  border: none;
  background: transparent;
}

.el-menu-item {
  color: white;
  border-bottom: 2px solid transparent !important;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 2px solid white !important;
}

.el-main {
  max-width: 1400px;
  margin: 20px auto;
  padding: 20px;
}
</style>

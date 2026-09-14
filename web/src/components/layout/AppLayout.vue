<template>
  <el-container class="layout">
    <AppSidebar />
    <el-container class="right">
      <el-header class="header-slot">
        <AppHeader />
      </el-header>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade-up" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.layout {
  height: 100vh;
}
.right {
  flex-direction: column;
  overflow: hidden;
}
.main {
  overflow-y: auto;
  background: transparent;
}
</style>
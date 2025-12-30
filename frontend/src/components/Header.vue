<template>
  <header class="header">
    <div class="header-left">
      <input 
        type="text" 
        placeholder="Search detections, logs..." 
        class="search-input"
      />
    </div>
    <div class="header-right">
      <div class="user-menu">
        <span class="user-name">System Admin</span>
        <div class="notification-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span class="badge-count" v-if="notificationCount > 0">{{ notificationCount }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const notificationCount = ref(0)

onMounted(async () => {
  try {
    const stats = await api.getDashboardStats()
    notificationCount.value = stats.critical_alerts || 0
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
})
</script>

<style scoped>
.header {
  height: 64px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 90;
  width: 100%;
}

.header-left {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.9375rem;
  background: var(--bg-secondary);
  color: var(--text);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  font-size: 0.9375rem;
  color: var(--text);
  font-weight: 500;
}

.notification-badge {
  position: relative;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.notification-badge:hover {
  color: var(--text);
}

.notification-badge svg {
  width: 20px;
  height: 20px;
}

.badge-count {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--danger);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

</style>


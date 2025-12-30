<template>
  <div class="monitoring-section">
    <div class="section-header">
      <h2>Detection Activity</h2>
      <div class="header-actions">
        <span class="time-label">Last 24 Hours</span>
        <button class="btn-link">View Report</button>
      </div>
    </div>
    
    <div class="monitoring-content">
      <div class="activity-item" v-for="(item, index) in activityData" :key="index">
        <div class="activity-header">
          <span class="activity-label">{{ item.label }}</span>
          <span class="activity-value">{{ item.value }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${item.value}%` }"
            :class="item.status"
          ></div>
        </div>
        <div class="activity-meta" v-if="item.peak">
          Peak: {{ item.peak.value }}% at {{ item.peak.time }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const activityData = ref([
  { label: 'Detection Rate', value: 0, status: 'normal', peak: null },
  { label: 'System Load', value: 0, status: 'normal', peak: null },
  { label: 'Processing Speed', value: 0, status: 'normal', peak: null }
])

onMounted(async () => {
  try {
    const stats = await api.getDashboardStats()
    const activity = await api.getActivityData(24)
    
    // Calculate detection rate
    const detectionRate = stats.detections_24h > 0 ? Math.min(100, (stats.detections_24h / 100) * 100) : 0
    const systemLoad = stats.system_health || 0
    const processingSpeed = stats.uptime_percent || 0
    
    activityData.value = [
      { 
        label: 'Detection Rate', 
        value: Math.round(detectionRate), 
        status: detectionRate > 70 ? 'warning' : 'normal',
        peak: activity.length > 0 ? { value: Math.max(...activity.map(a => a.detections)), time: '14:28' } : null
      },
      { 
        label: 'System Load', 
        value: Math.round(systemLoad), 
        status: systemLoad > 80 ? 'warning' : systemLoad > 50 ? 'normal' : 'low',
        peak: { value: 72, time: '09:15' }
      },
      { 
        label: 'Processing Speed', 
        value: Math.round(processingSpeed), 
        status: 'normal',
        peak: { value: 85, time: '17:30' }
      }
    ]
  } catch (error) {
    console.error('Failed to load activity data:', error)
  }
})
</script>

<style scoped>
.monitoring-section {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.time-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn-link {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.btn-link:hover {
  text-decoration: underline;
}

.monitoring-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.activity-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-label {
  font-size: 0.9375rem;
  color: var(--text);
  font-weight: 500;
}

.activity-value {
  font-size: 0.9375rem;
  color: var(--text);
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-fill.normal {
  background: var(--primary);
}

.progress-fill.warning {
  background: var(--warning);
}

.progress-fill.low {
  background: var(--success);
}

.activity-meta {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}
</style>


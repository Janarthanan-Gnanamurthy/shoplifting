<template>
  <div class="recent-detections">
    <div class="section-header">
      <h2>Recent Detections</h2>
      <span class="badge">{{ totalCount }} Total</span>
    </div>
    
    <div class="detections-list">
      <div 
        v-for="detection in detections" 
        :key="detection.id"
        class="detection-item"
        :class="detection.status"
      >
        <div class="detection-icon">
          <svg v-if="detection.type === 'image'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
        </div>
        <div class="detection-content">
          <div class="detection-header">
            <span class="detection-name">{{ detection.filename || 'Unknown' }}</span>
            <span class="detection-status" :class="detection.status">
              {{ detection.status === 'critical' ? 'Critical' : detection.status === 'warning' ? 'Warning' : 'Normal' }}
            </span>
          </div>
          <div class="detection-meta">
            <span>{{ formatTime(detection.timestamp) }}</span>
            <span>•</span>
            <span>Confidence: {{ (detection.confidence * 100).toFixed(1) }}%</span>
            <span v-if="detection.type === 'video'">•</span>
            <span v-if="detection.type === 'video'">{{ detection.events_count || 0 }} events</span>
          </div>
        </div>
        <button class="detection-action">View</button>
      </div>
      
      <div v-if="detections.length === 0" class="empty-state">
        <p>No detections yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const detections = ref([])
const totalCount = ref(0)

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

onMounted(async () => {
  try {
    const recent = await api.getRecentDetections(10)
    detections.value = recent
    const all = await api.getAllDetections(0, 1)
    totalCount.value = all.total || 0
  } catch (error) {
    console.error('Failed to load recent detections:', error)
  }
})
</script>

<style scoped>
.recent-detections {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
}

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: 12px;
}

.detections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: all 0.2s;
}

.detection-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary);
}

.detection-item.critical {
  border-left: 3px solid var(--danger);
}

.detection-item.warning {
  border-left: 3px solid var(--warning);
}

.detection-item.normal {
  border-left: 3px solid var(--success);
}

.detection-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 6px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.detection-icon svg {
  width: 20px;
  height: 20px;
}

.detection-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detection-name {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text);
}

.detection-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.detection-status.critical {
  background: #fee2e2;
  color: #991b1b;
}

.detection-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.detection-status.normal {
  background: #d1fae5;
  color: #065f46;
}

.detection-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.detection-action {
  padding: 0.5rem 1rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.detection-action:hover {
  background: var(--primary-dark);
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}
</style>


<template>
  <div class="dashboard">
    <div class="summary-grid">
      <SummaryCard
        title="System Health"
        :value="`${stats.system_health || 0}%`"
        badge-text="HEALTHY"
        badge-class="healthy"
        :meta="`Uptime ${stats.uptime_percent || 0}%`"
      />
      
      <SummaryCard
        title="Total Detections"
        :value="stats.total_detections || 0"
        badge-text="ACTIVE"
        badge-class="online"
        :meta="`${stats.detections_24h || 0} in last 24h`"
      />
      
      <SummaryCard
        title="Critical Alerts"
        :value="stats.critical_alerts || 0"
        badge-text="NEW"
        badge-class="critical"
        :meta="`Warnings: ${stats.warnings || 0}`"
      />
      
      <SummaryCard
        title="Model Status"
        :value="stats.models_loaded ? 'ONLINE' : 'OFFLINE'"
        :badge-text="stats.models_loaded ? 'OPERATIONAL' : 'ERROR'"
        :badge-class="stats.models_loaded ? 'healthy' : 'critical'"
        meta="AI Detection System"
      />
    </div>

    <div class="dashboard-grid">
      <div class="grid-left">
        <MonitoringSection />
        
        <div class="server-cards">
          <div class="server-card">
            <div class="server-header">
              <h3>Detection System</h3>
              <span class="server-badge healthy">HEALTHY</span>
            </div>
            <div class="server-stats">
              <div class="stat-row">
                <span class="stat-label">Accuracy</span>
                <span class="stat-value">94.2%</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Processing</span>
                <span class="stat-value">1.2K/min</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Response Time</span>
                <span class="stat-value">0.8s</span>
              </div>
            </div>
            <button class="server-action">Details</button>
          </div>
          
          <div class="server-card">
            <div class="server-header">
              <h3>Video Processing</h3>
              <span class="server-badge monitor">MONITOR</span>
            </div>
            <div class="server-stats">
              <div class="stat-row">
                <span class="stat-label">Queue</span>
                <span class="stat-value">3 videos</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Avg Duration</span>
                <span class="stat-value">45s</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Success Rate</span>
                <span class="stat-value">98.5%</span>
              </div>
            </div>
            <button class="server-action">Investigate</button>
          </div>
        </div>
      </div>
      
      <div class="grid-right">
        <QuickActions />
        <RecentDetections />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SummaryCard from '../components/SummaryCard.vue'
import MonitoringSection from '../components/MonitoringSection.vue'
import QuickActions from '../components/QuickActions.vue'
import RecentDetections from '../components/RecentDetections.vue'
import api from '../services/api'

const stats = ref({
  system_health: 0,
  models_loaded: false,
  total_detections: 0,
  detections_24h: 0,
  critical_alerts: 0,
  warnings: 0,
  uptime_percent: 0
})

onMounted(async () => {
  try {
    const data = await api.getDashboardStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.grid-left {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.grid-right {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.server-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.server-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.server-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
}

.server-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

.server-badge.healthy {
  background: #d1fae5;
  color: #065f46;
}

.server-badge.monitor {
  background: #fef3c7;
  color: #92400e;
}

.server-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text);
}

.server-action {
  width: 100%;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.server-action:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary);
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .server-cards {
    grid-template-columns: 1fr;
  }
}
</style>

<template>
  <div class="dashboard">
    <div class="header">
      <h1>Shoplifting Detection</h1>
      <p>AI-powered behavioral analysis system</p>
    </div>

    <div class="features">
      <div class="feature" @click="$router.push('/image')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
        </div>
        <h3>Image Analysis</h3>
        <p>Detect suspicious behavior in images</p>
      </div>

      <div class="feature" @click="$router.push('/visualize')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2v20M2 12h20"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <h3>Pose Visualization</h3>
        <p>View pose keypoints and overlays</p>
      </div>

      <div class="feature" @click="$router.push('/video')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
        </div>
        <h3>Video Analysis</h3>
        <p>Analyze video footage for activity</p>
      </div>
    </div>

    <div class="status" v-if="healthStatus">
      <div class="status-item">
        <span class="status-label">System Status</span>
        <span class="status-value" :class="{ error: !healthStatus.models_loaded }">
          {{ healthStatus.models_loaded ? 'Operational' : 'Error' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const healthStatus = ref(null)

onMounted(async () => {
  try {
    healthStatus.value = await api.healthCheck()
  } catch (error) {
    console.error('Failed to fetch health status:', error)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 4rem;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.header p {
  font-size: 1.125rem;
  color: var(--text-secondary);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.feature {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.feature:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px var(--shadow);
  transform: translateY(-2px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 1.5rem;
  color: var(--primary);
}

.feature-icon svg {
  width: 100%;
  height: 100%;
}

.feature h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.feature p {
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

.status {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

.status-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--success);
}

.status-value.error {
  color: var(--danger);
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>

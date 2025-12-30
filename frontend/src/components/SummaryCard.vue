<template>
  <div class="summary-card">
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <span class="card-badge" :class="badgeClass">{{ badgeText }}</span>
    </div>
    <div class="card-value">{{ value }}</div>
    <div class="card-footer">
      <span class="card-meta">{{ meta }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  badgeText: String,
  badgeClass: String,
  meta: String
})
</script>

<style scoped>
.summary-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.summary-card:hover {
  box-shadow: 0 4px 12px var(--shadow);
  border-color: var(--primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

.card-badge.healthy {
  background: #d1fae5;
  color: #065f46;
}

.card-badge.monitor {
  background: #fef3c7;
  color: #92400e;
}

.card-badge.critical {
  background: #fee2e2;
  color: #991b1b;
}

.card-badge.online {
  background: #d1fae5;
  color: #065f46;
}

.card-value {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.card-footer {
  margin-top: 0.5rem;
}

.card-meta {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
</style>


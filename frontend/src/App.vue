<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <span class="brand-text">ShopliftGuard</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Dashboard</router-link>
          <router-link to="/image" class="nav-link">Image</router-link>
          <router-link to="/visualize" class="nav-link">Visualize</router-link>
          <router-link to="/video" class="nav-link">Video</router-link>
        </div>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import api from './services/api'

onMounted(async () => {
  try {
    const health = await api.healthCheck()
    if (!health.models_loaded) {
      console.warn('Models not loaded:', health.error)
    }
  } catch (error) {
    console.error('Health check failed:', error)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #2563eb;
  --primary-dark: #1e40af;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --text-light: #9ca3af;
  --bg: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --border: #e5e7eb;
  --border-light: #f3f4f6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --shadow: rgba(0, 0, 0, 0.05);
  --shadow-md: rgba(0, 0, 0, 0.1);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.95);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
}

.brand-text {
  color: var(--primary);
}

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: color 0.2s;
  position: relative;
  padding: 0.5rem 0;
}

.nav-link:hover {
  color: var(--text);
}

.nav-link.router-link-active {
  color: var(--primary);
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 3rem 2rem;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 1.5rem;
  }
  
  .nav-links {
    gap: 1.5rem;
  }
  
  .main-content {
    padding: 2rem 1.5rem;
  }
}
</style>

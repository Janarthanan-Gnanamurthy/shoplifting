<template>
  <div class="image-analysis">
    <div class="page-header">
      <h1>Image Analysis</h1>
      <p>Upload an image to detect suspicious behavior</p>
    </div>

    <div class="content">
      <div class="upload-section">
        <div 
          class="upload-area" 
          :class="{ 'drag-over': isDragging, 'has-image': previewUrl }"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @click="triggerFileInput"
        >
          <input 
            ref="fileInput"
            type="file" 
            accept="image/*" 
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div v-if="!previewUrl" class="upload-placeholder">
            <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p class="upload-text">Drop image or click to browse</p>
            <p class="upload-hint">JPG, PNG, WebP</p>
          </div>
          
          <img v-if="previewUrl" :src="previewUrl" alt="Preview" class="preview-image" />
        </div>

        <div class="actions" v-if="previewUrl">
          <button @click="analyzeImage" :disabled="loading" class="btn btn-primary">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Analyze</span>
          </button>
          <button @click="clearImage" class="btn btn-secondary">Clear</button>
        </div>
      </div>

      <div class="results" v-if="results">
        <div class="result-card">
          <h2>Results</h2>
          
          <div class="result-content">
            <div class="prediction">
              <span class="prediction-label">Prediction</span>
              <span class="prediction-value" :class="results.prediction === 'Shoplifting' ? 'danger' : 'success'">
                {{ results.prediction }}
              </span>
            </div>
            
            <div class="confidence">
              <div class="confidence-header">
                <span>Confidence</span>
                <span class="confidence-percent">{{ (results.shoplifting_probability * 100).toFixed(1) }}%</span>
              </div>
              <div class="confidence-bar">
                <div 
                  class="confidence-fill" 
                  :style="{ width: `${results.shoplifting_probability * 100}%` }"
                  :class="results.shoplifting_probability > 0.5 ? 'danger' : 'success'"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="error" v-if="error">
        <span class="error-text">{{ error }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const fileInput = ref(null)
const previewUrl = ref(null)
const selectedFile = ref(null)
const results = ref(null)
const loading = ref(false)
const error = ref(null)
const isDragging = ref(false)

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  if (!file.type.startsWith('image/')) {
    error.value = 'Please select a valid image file'
    return
  }
  
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  results.value = null
  error.value = null
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const clearImage = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = null
  selectedFile.value = null
  results.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const analyzeImage = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = null
  results.value = null
  
  try {
    const response = await api.predictImage(selectedFile.value)
    results.value = response
  } catch (err) {
    error.value = err.message || 'Failed to analyze image'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.image-analysis {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 3rem;
  text-align: center;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1rem;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.upload-area {
  background: var(--bg-secondary);
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--primary);
  background: var(--bg-tertiary);
}

.upload-area.drag-over {
  border-color: var(--primary);
  background: var(--bg-tertiary);
}

.upload-area.has-image {
  padding: 0;
  border-style: solid;
  background: var(--bg);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: var(--text-light);
}

.upload-text {
  font-size: 1rem;
  color: var(--text);
  font-weight: 500;
}

.upload-hint {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.preview-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  object-fit: contain;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 2rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg);
  color: var(--text);
}

.btn-primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary:hover {
  border-color: var(--text-light);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.results {
  margin-top: 1rem;
}

.result-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
}

.result-card h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 1.5rem;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.prediction {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.prediction-label {
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

.prediction-value {
  font-size: 1.125rem;
  font-weight: 600;
}

.prediction-value.success {
  color: var(--success);
}

.prediction-value.danger {
  color: var(--danger);
}

.confidence {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

.confidence-percent {
  font-weight: 600;
  color: var(--text);
}

.confidence-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.confidence-fill.success {
  background: var(--success);
}

.confidence-fill.danger {
  background: var(--danger);
}

.error {
  padding: 1rem 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: var(--danger);
  font-size: 0.9375rem;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.75rem;
  }
  
  .upload-area {
    min-height: 250px;
    padding: 2rem;
  }
}
</style>

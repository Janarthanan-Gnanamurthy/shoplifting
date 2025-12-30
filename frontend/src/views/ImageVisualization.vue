<template>
  <div class="image-visualization">
    <div class="page-header">
      <h1>Pose Visualization</h1>
      <p>Visualize pose keypoints and detection overlays</p>
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
            <p class="upload-hint">Visualize pose detection</p>
          </div>
          
          <img v-if="previewUrl && !visualizedUrl" :src="previewUrl" alt="Preview" class="preview-image" />
          <img v-if="visualizedUrl" :src="visualizedUrl" alt="Visualized" class="preview-image" />
        </div>

        <div class="controls" v-if="previewUrl">
          <div class="control-group">
            <label for="threshold">Threshold: {{ threshold.toFixed(2) }}</label>
            <input 
              type="range" 
              id="threshold" 
              v-model.number="threshold" 
              min="0" 
              max="1" 
              step="0.05"
              class="slider"
            />
          </div>
          
          <div class="actions">
            <button @click="visualizeImage" :disabled="loading" class="btn btn-primary">
              <span v-if="loading" class="spinner"></span>
              <span v-else>Generate</span>
            </button>
            <button @click="clearImage" class="btn btn-secondary">Clear</button>
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
const visualizedUrl = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const error = ref(null)
const isDragging = ref(false)
const threshold = ref(0.5)

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
  visualizedUrl.value = null
  error.value = null
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const clearImage = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  if (visualizedUrl.value) {
    URL.revokeObjectURL(visualizedUrl.value)
  }
  previewUrl.value = null
  visualizedUrl.value = null
  selectedFile.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const visualizeImage = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const url = await api.visualizeImage(selectedFile.value, threshold.value)
    if (visualizedUrl.value) {
      URL.revokeObjectURL(visualizedUrl.value)
    }
    visualizedUrl.value = url
  } catch (err) {
    error.value = err.message || 'Failed to visualize image'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.image-visualization {
  max-width: 1000px;
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
  max-height: 600px;
  border-radius: 8px;
  object-fit: contain;
}

.controls {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.control-group label {
  font-size: 0.9375rem;
  color: var(--text);
  font-weight: 500;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-tertiary);
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.1);
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

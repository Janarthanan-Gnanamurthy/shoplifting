<template>
  <div class="video-analysis">
    <div class="page-header">
      <h1>Video Analysis</h1>
      <p>Analyze video footage for suspicious activity</p>
    </div>

    <div class="content">
      <div class="upload-section">
        <div 
          class="upload-area" 
          :class="{ 'drag-over': isDragging, 'has-video': previewUrl }"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @click="triggerFileInput"
        >
          <input 
            ref="fileInput"
            type="file" 
            accept="video/*" 
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div v-if="!previewUrl" class="upload-placeholder">
            <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            <p class="upload-text">Drop video or click to browse</p>
            <p class="upload-hint">MP4, MOV, AVI</p>
          </div>
          
          <video v-if="previewUrl" :src="previewUrl" controls class="preview-video"></video>
        </div>

        <div class="controls" v-if="previewUrl">
          <div class="control-group">
            <div class="control-item">
              <label for="frameSkip">Frame Skip: {{ frameSkip }}</label>
              <input 
                type="range" 
                id="frameSkip" 
                v-model.number="frameSkip" 
                min="1" 
                max="10" 
                step="1"
                class="slider"
              />
              <span class="control-hint">Lower = more accurate, slower</span>
            </div>
            
            <div class="control-item">
              <label for="confidence">Confidence Threshold: {{ confidenceThreshold.toFixed(2) }}</label>
              <input 
                type="range" 
                id="confidence" 
                v-model.number="confidenceThreshold" 
                min="0" 
                max="1" 
                step="0.05"
                class="slider"
              />
              <span class="control-hint">Minimum probability to flag</span>
            </div>
          </div>
          
          <div class="actions">
            <button @click="analyzeVideo" :disabled="loading" class="btn btn-primary">
              <span v-if="loading" class="spinner"></span>
              <span v-else>Analyze</span>
            </button>
            <button @click="clearVideo" class="btn btn-secondary">Clear</button>
          </div>
        </div>
      </div>

      <div class="results" v-if="results">
        <div class="result-card">
          <h2>Results</h2>
          
          <div class="result-content">
            <div class="summary">
              <div class="summary-item">
                <span class="summary-label">Prediction</span>
                <span class="summary-value" :class="results.overall_prediction === 'Shoplifting Detected' ? 'danger' : 'success'">
                  {{ results.overall_prediction }}
                </span>
              </div>
              
              <div class="summary-item">
                <span class="summary-label">Max Confidence</span>
                <span class="summary-value">{{ (results.max_confidence * 100).toFixed(1) }}%</span>
              </div>
              
              <div class="summary-item">
                <span class="summary-label">Duration</span>
                <span class="summary-value">{{ formatTime(results.duration_seconds) }}</span>
              </div>
              
              <div class="summary-item">
                <span class="summary-label">Detections</span>
                <span class="summary-value">{{ results.raw_detections_count }} frames</span>
              </div>
            </div>

            <div class="timeline" v-if="results.timeline_events && results.timeline_events.length > 0">
              <h3>Timeline</h3>
              <div class="timeline-list">
                <div 
                  v-for="(event, index) in results.timeline_events" 
                  :key="index"
                  class="timeline-item"
                >
                  <div class="timeline-time">
                    {{ formatTime(event.start) }} - {{ formatTime(event.end) }}
                  </div>
                  <div class="timeline-duration">
                    {{ (event.end - event.start).toFixed(1) }}s
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="no-events">
              <p>No suspicious activity detected</p>
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
const frameSkip = ref(5)
const confidenceThreshold = ref(0.7)

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('video/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  if (!file.type.startsWith('video/')) {
    error.value = 'Please select a valid video file'
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

const clearVideo = () => {
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

const analyzeVideo = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = null
  results.value = null
  
  try {
    const response = await api.analyzeVideo(selectedFile.value, frameSkip.value, confidenceThreshold.value)
    results.value = response
  } catch (err) {
    error.value = err.message || 'Failed to analyze video'
  } finally {
    loading.value = false
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.video-analysis {
  max-width: 900px;
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

.upload-area.has-video {
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

.preview-video {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
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
  gap: 1.5rem;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-item label {
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

.control-hint {
  font-size: 0.8125rem;
  color: var(--text-secondary);
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

.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
}

.summary-value.success {
  color: var(--success);
}

.summary-value.danger {
  color: var(--danger);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.timeline-time {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text);
}

.timeline-duration {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.no-events {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-radius: 6px;
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
  
  .summary {
    grid-template-columns: 1fr;
  }
}
</style>

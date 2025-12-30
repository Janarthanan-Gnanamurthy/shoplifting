const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.json()
  }

  async predictImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to predict image')
    }
    
    return response.json()
  }

  async visualizeImage(file, threshold = 0.5) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('threshold', threshold.toString())
    
    const response = await fetch(`${API_BASE_URL}/visualize`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to visualize image')
    }
    
    const blob = await response.blob()
    return URL.createObjectURL(blob)
  }

  async analyzeVideo(file, frameSkip = 5, confidenceThreshold = 0.7) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('frame_skip', frameSkip.toString())
    formData.append('confidence_threshold', confidenceThreshold.toString())
    
    const response = await fetch(`${API_BASE_URL}/analyze_video`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to analyze video')
    }
    
    return response.json()
  }

  async getDashboardStats() {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`)
    if (!response.ok) throw new Error('Failed to fetch dashboard stats')
    return response.json()
  }

  async getRecentDetections(limit = 10) {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/recent?limit=${limit}`)
    if (!response.ok) throw new Error('Failed to fetch recent detections')
    return response.json()
  }

  async getActivityData(hours = 24) {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/activity?hours=${hours}`)
    if (!response.ok) throw new Error('Failed to fetch activity data')
    return response.json()
  }

  async getAllDetections(skip = 0, limit = 50) {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/detections?skip=${skip}&limit=${limit}`)
    if (!response.ok) throw new Error('Failed to fetch detections')
    return response.json()
  }
}

export default new ApiService()


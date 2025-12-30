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
}

export default new ApiService()


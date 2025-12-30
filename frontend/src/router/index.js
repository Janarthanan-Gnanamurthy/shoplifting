import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ImageAnalysis from '../views/ImageAnalysis.vue'
import ImageVisualization from '../views/ImageVisualization.vue'
import VideoAnalysis from '../views/VideoAnalysis.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/image',
      name: 'image-analysis',
      component: ImageAnalysis
    },
    {
      path: '/visualize',
      name: 'image-visualization',
      component: ImageVisualization
    },
    {
      path: '/video',
      name: 'video-analysis',
      component: VideoAnalysis
    }
  ],
})

export default router

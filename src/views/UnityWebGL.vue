<template>
  <div class="unity-webgl-container">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
        <span>返回数字化展示</span>
      </button>
    </div>
    
    <div class="unity-content">
      <!-- Unity WebGL 内容将通过iframe加载 -->
      <iframe 
        :src="unityWebGLUrl" 
        frameborder="0" 
        class="unity-iframe"
        allow="accelerometer; autoplay; gyroscope; xr-spatial-tracking"
        xr-spatial-tracking="inline"
        execution-while-out-of-viewport="true"
        execution-while-not-rendered="true"
        loading="lazy"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Unity WebGL文件的URL路径
const unityWebGLUrl = ref('')

// 返回上一页
const goBack = () => {
  router.back()
}

// 组件挂载时设置Unity WebGL URL
onMounted(() => {
  // 在开发环境中，我们需要设置一个合适的URL来访问Unity WebGL内容
  // 由于Unity WebGL内容位于HX_project/static/webgl目录中
  // 我们需要通过合适的路径来访问它
  
  // 这里我们使用绝对路径，假设项目在本地运行
  // 在实际部署时，可能需要调整这个路径
  unityWebGLUrl.value = 'http://localhost:5173/unity-webgl/index.html'
})
</script>

<style scoped>
/* 返回按钮样式 */
.back-button-container {
  position: fixed;
  top: 2rem;
  left: 2rem;
  z-index: 1000;
}

.back-button {
  background: #C8102E;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
}

.back-button:hover {
  background: #a60e24;
  transform: translateX(-5px) scale(1.05);
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.4);
  animation: backButtonFloat 1.5s infinite;
}

.back-button i {
  font-size: 1.1rem;
}

@keyframes backButtonFloat {
  0%, 100% {
    transform: translateX(-5px) scale(1.05);
  }
  50% {
    transform: translateX(0px) scale(1.05);
  }
}

.unity-webgl-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.unity-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.unity-iframe {
  width: 100%;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .back-button {
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .back-button {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
}
</style>
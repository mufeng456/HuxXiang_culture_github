<template>
  <div class="ai-assistant-page">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
        <span>返回数字化展示</span>
      </button>
    </div>

    <!-- 主标题区域 -->
    <div class="section-title">
      <div class="title-badge">
        <i class="fas fa-robot"></i>
      </div>
      <h2>AI文化助手</h2>
      <p>智能问答系统，解答您的湖湘文化问题</p>
    </div>

    <!-- AI助手主体 -->
    <div class="ai-assistant-container">
      <!-- 左侧：分类 + 对话历史 -->
      <div class="ai-sidebar">
        <button class="new-chat-btn" @click="showCategoryModal = true">
          <i class="fas fa-plus"></i>
          <span>新建对话</span>
        </button>

        <div class="sidebar-section-title">分类</div>
        <div class="category-list">
          <div
            v-for="cat in categories"
            :key="cat.name"
            class="category-item"
            :class="{ active: currentCategory === cat.name && !currentConversationId }"
            @click="quickNewChat(cat.name)"
          >
            <i :class="cat.icon"></i>
            <span>{{ cat.name }}</span>
          </div>
        </div>

        <div class="sidebar-section-title">历史对话</div>

        <div class="conversation-list">
          <div v-if="conversations.length === 0" class="empty-hint">
            暂无对话记录
          </div>
          <div
            v-for="conv in conversations"
            :key="conv.id"
            class="conversation-item"
            :class="{ active: currentConversationId === conv.id }"
            @click="loadConversation(conv)"
          >
            <div class="conv-icon">
              <i :class="getCategoryIcon(conv.category)"></i>
            </div>
            <div class="conv-info">
              <div class="conv-title">{{ conv.title }}</div>
              <div class="conv-meta">{{ conv.category }} · {{ formatTime(conv.updated_at) }}</div>
            </div>
            <button class="conv-delete" @click.stop="deleteConversation(conv.id)" title="删除">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 聊天界面 -->
      <div class="chat-container">
        <div class="chat-header">
          <h4>{{ currentCategory }}</h4>
          <span v-if="currentConversationId" class="chat-id">对话 #{{ currentConversationId }}</span>
        </div>

        <div class="chat-messages" ref="chatMessages">
          <!-- 欢迎消息 -->
          <div class="message system-message">
            <div class="message-bubble">
              <p>您好！我是AI文化助手，很高兴为您解答湖湘文化相关问题。</p>
            </div>
          </div>

          <!-- 对话消息 -->
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']">
            <div class="message-bubble">
              <p v-if="msg.role === 'user'">{{ msg.content }}</p>
              <div v-else class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            </div>
          </div>

          <!-- 流式输出中 -->
          <div v-if="isStreaming" class="message ai-message">
            <div class="message-bubble">
              <div class="markdown-body" v-html="renderMarkdown(streamingContent)"></div>
              <span class="cursor">|</span>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <input
            type="text"
            v-model="inputMessage"
            :placeholder="isStreaming ? 'AI 正在回复...' : '输入您的问题...'"
            :disabled="isStreaming"
            @keyup.enter="sendMessage"
            class="chat-input"
          />
          <button class="send-btn" @click="sendMessage" :disabled="isStreaming || !inputMessage.trim()">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 分类选择弹窗 -->
    <div v-if="showCategoryModal" class="modal-overlay" @click.self="showCategoryModal = false">
      <div class="modal-box">
        <h3>选择对话分类</h3>
        <div class="category-grid">
          <div
            v-for="cat in categories"
            :key="cat.name"
            class="category-card"
            :class="{ selected: selectedCategory === cat.name }"
            @click="selectedCategory = cat.name"
          >
            <i :class="cat.icon"></i>
            <span>{{ cat.name }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showCategoryModal = false">取消</button>
          <button class="btn btn-primary" @click="startNewConversation">开始对话</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api'

const router = useRouter()

// 分类配置
const categories = [
  { name: '文化问答', icon: 'fas fa-question-circle' },
  { name: '历史人物', icon: 'fas fa-user-circle' },
  { name: '文化遗产', icon: 'fas fa-university' },
  { name: '传统习俗', icon: 'fas fa-calendar-alt' },
  { name: '湖湘美食', icon: 'fas fa-utensils' },
  { name: '旅游景点', icon: 'fas fa-map-marker-alt' },
]

// 状态
const currentCategory = ref('文化问答')
const selectedCategory = ref('文化问答')
const currentConversationId = ref(null)
const conversations = ref([])
const messages = ref([])
const inputMessage = ref('')
const chatMessages = ref(null)
const isStreaming = ref(false)
const streamingContent = ref('')
const showCategoryModal = ref(false)

const getCategoryIcon = (cat) => {
  const found = categories.find(c => c.name === cat)
  return found ? found.icon : 'fas fa-comment'
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString('zh-CN')
}

// 简单 Markdown 渲染：加粗、列表、换行
const renderMarkdown = (text) => {
  if (!text) return ''
  // 转义 HTML
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  // 加粗 **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 斜体 *text*
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // 无序列表 - item
  const lines = html.split('\n')
  let inList = false
  const result = []
  for (const line of lines) {
    const listMatch = line.match(/^\s*[-*]\s+(.+)$/)
    if (listMatch) {
      if (!inList) {
        result.push('<ul>')
        inList = true
      }
      result.push(`<li>${listMatch[1]}</li>`)
    } else {
      if (inList) {
        result.push('</ul>')
        inList = false
      }
      if (line.trim()) {
        result.push(`<p>${line}</p>`)
      }
    }
  }
  if (inList) result.push('</ul>')
  return result.join('')
}

const goBack = () => router.back()

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

// 加载对话列表
const loadConversations = async () => {
  try {
    const res = await request('/ai/conversations', 'GET')
    conversations.value = res.conversations || []
  } catch (e) {
    // 未登录时不显示历史
    conversations.value = []
  }
}

// 加载单个对话
const loadConversation = async (conv) => {
  try {
    const res = await request(`/ai/conversations/${conv.id}`, 'GET')
    currentConversationId.value = conv.id
    currentCategory.value = conv.category
    messages.value = (res.messages || []).map(m => ({
      role: m.role,
      content: m.content,
    }))
    scrollToBottom()
  } catch (e) {
    console.error('加载对话失败', e)
  }
}

// 快速新建对话（点击分类）
const quickNewChat = (category) => {
  currentCategory.value = category
  selectedCategory.value = category
  currentConversationId.value = null
  messages.value = []
  streamingContent.value = ''
  scrollToBottom()
}

// 新建对话
const startNewConversation = () => {
  currentCategory.value = selectedCategory.value
  currentConversationId.value = null
  messages.value = []
  streamingContent.value = ''
  showCategoryModal.value = false
  scrollToBottom()
}

// 删除对话
const deleteConversation = async (id) => {
  if (!confirm('确定删除这个对话吗？')) return
  try {
    await request(`/ai/conversations/${id}`, 'DELETE')
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentConversationId.value === id) {
      currentConversationId.value = null
      messages.value = []
    }
  } catch (e) {
    console.error('删除失败', e)
  }
}

// 发送消息（流式）
const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text || isStreaming.value) return

  messages.value.push({ role: 'user', content: text })
  inputMessage.value = ''
  scrollToBottom()

  isStreaming.value = true
  streamingContent.value = ''

  try {
    const history = messages.value.map(m => ({ role: m.role, content: m.content }))

    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/ai/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        messages: history,
        category: currentCategory.value,
        conversation_id: currentConversationId.value,
      }),
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          if (data.error) {
            throw new Error(data.error)
          }
          if (data.content) {
            streamingContent.value += data.content
            scrollToBottom()
          }
          if (data.conversation_id && !currentConversationId.value) {
            currentConversationId.value = data.conversation_id
          }
          if (data.done) {
            // 流式结束，保存最终消息
            messages.value.push({ role: 'assistant', content: streamingContent.value })
            streamingContent.value = ''
            loadConversations()
          }
        }
      }
    }
  } catch (error) {
    streamingContent.value = ''
    messages.value.push({
      role: 'assistant',
      content: error.message.includes('未配置') ? '请先在管理后台配置 AI 服务商 API Key' : `出错了：${error.message}`,
    })
  } finally {
    isStreaming.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
.ai-assistant-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF5F5 0%, #F9FAFB 300px);
  padding: 5rem 2rem 2rem;
}

/* 返回按钮 - 统一项目风格 */
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
  padding: 0.75rem 1.5rem;
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
  transform: translateX(-3px);
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.4);
}

.section-title {
  text-align: center;
  margin-bottom: 2rem;
}

.title-badge {
  width: 56px;
  height: 56px;
  margin: 0 auto 0.8rem;
  background: linear-gradient(135deg, #C8102E, #8B0A1F);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 4px 16px rgba(200, 16, 46, 0.3);
}

.section-title h2 {
  font-size: 2rem;
  color: #1F2937;
  margin: 0 0 0.4rem 0;
  letter-spacing: 0.02em;
}

.section-title p {
  color: #6B7280;
  margin: 0;
  font-size: 0.95rem;
}

.ai-assistant-container {
  display: flex;
  gap: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 280px);
  min-height: 520px;
}

/* 左侧边栏 */
.ai-sidebar {
  width: 280px;
  background: white;
  border-radius: 16px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid rgba(200, 16, 46, 0.06);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(135deg, #C8102E, #8B0A1F);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.25);
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.35);
}

.sidebar-section-title {
  font-size: 0.8rem;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 1.2rem 0 0.6rem;
  padding: 0 0.25rem;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  color: #4B5563;
  transition: all 0.15s;
}

.category-item:hover {
  background: #F3F4F6;
  color: #C8102E;
}

.category-item.active {
  background: rgba(200, 16, 46, 0.08);
  color: #C8102E;
  font-weight: 500;
}

.category-item i {
  width: 18px;
  text-align: center;
  font-size: 0.85rem;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.empty-hint {
  text-align: center;
  color: #9CA3AF;
  font-size: 0.85rem;
  padding: 2rem 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 0.2rem;
}

.conversation-item:hover {
  background: #F3F4F6;
}

.conversation-item.active {
  background: rgba(200, 16, 46, 0.08);
}

.conv-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C8102E;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.conversation-item.active .conv-icon {
  background: rgba(200, 16, 46, 0.15);
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1F2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-meta {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin-top: 0.15rem;
}

.conv-delete {
  background: none;
  border: none;
  color: #9CA3AF;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s;
}

.conversation-item:hover .conv-delete {
  opacity: 1;
}

.conv-delete:hover {
  color: #C8102E;
  background: rgba(200, 16, 46, 0.1);
}

/* 聊天区 */
.chat-container {
  flex: 1;
  background: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid rgba(200, 16, 46, 0.06);
  overflow: hidden;
}

.chat-header {
  padding: 1.1rem 1.5rem;
  border-bottom: 1px solid #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, rgba(200, 16, 46, 0.03), transparent);
}

.chat-header h4 {
  margin: 0;
  color: #1F2937;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chat-header h4::before {
  content: '';
  width: 4px;
  height: 18px;
  background: #C8102E;
  border-radius: 2px;
}

.chat-id {
  font-size: 0.8rem;
  color: #9CA3AF;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.message {
  display: flex;
  margin-bottom: 1rem;
}

.user-message {
  justify-content: flex-end;
}

.ai-message, .system-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 75%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  line-height: 1.6;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #C8102E, #8B0A1F);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-bubble {
  background: #F3F4F6;
  color: #1F2937;
  border-bottom-left-radius: 4px;
}

.system-message .message-bubble {
  background: #EFF6FF;
  color: #1E40AF;
  font-size: 0.9rem;
}

.message-bubble p {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.markdown-body {
  line-height: 1.7;
}

.markdown-body p {
  margin: 0 0 0.6rem 0;
}

.markdown-body p:last-child {
  margin-bottom: 0;
}

.markdown-body strong {
  color: #C8102E;
  font-weight: 600;
}

.markdown-body ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown-body li {
  margin-bottom: 0.3rem;
}

.cursor {
  animation: blink 1s infinite;
  color: #C8102E;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 输入区 */
.chat-input-area {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #E5E7EB;
}

.chat-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #C8102E;
}

.chat-input:disabled {
  background: #F9FAFB;
  color: #9CA3AF;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #C8102E, #8B0A1F);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 分类弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  width: 480px;
  max-width: 90vw;
}

.modal-box h3 {
  margin: 0 0 1.2rem 0;
  color: #1F2937;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  border: 2px solid #E5E7EB;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  color: #4B5563;
}

.category-card:hover {
  border-color: #C8102E;
  color: #C8102E;
}

.category-card.selected {
  border-color: #C8102E;
  background: rgba(200, 16, 46, 0.05);
  color: #C8102E;
}

.category-card i {
  font-size: 1.3rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
}

.btn-primary {
  background: linear-gradient(135deg, #C8102E, #8B0A1F);
  color: white;
}

.btn-secondary {
  background: #F3F4F6;
  color: #4B5563;
}
</style>

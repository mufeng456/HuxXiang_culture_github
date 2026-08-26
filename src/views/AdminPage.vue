<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1>管理中心</h1>
        <p>欢迎回来，{{ user?.username }}！您可以在这里管理平台的各项内容。</p>
      </div>

      <div class="admin-stats">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-landmark"></i></div>
          <div class="stat-content">
            <div class="stat-number">{{ resourceCount }}</div>
            <div class="stat-label">文化资源</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-project-diagram"></i></div>
          <div class="stat-content">
            <div class="stat-number">{{ graphNodeCount }}</div>
            <div class="stat-label">知识图谱节点</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-comments"></i></div>
          <div class="stat-content">
            <div class="stat-number">{{ postCount }}</div>
            <div class="stat-label">社区帖子</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-users"></i></div>
          <div class="stat-content">
            <div class="stat-number">{{ userCount }}</div>
            <div class="stat-label">注册用户</div>
          </div>
        </div>
      </div>

      <div class="admin-tabs">
        <button class="tab-button" :class="{ active: activeTab === 'resources' }" @click="activeTab = 'resources'">
          <i class="fas fa-landmark"></i> 文化资源管理
        </button>
        <button class="tab-button" :class="{ active: activeTab === 'knowledge-graph' }" @click="activeTab = 'knowledge-graph'">
          <i class="fas fa-project-diagram"></i> 知识图谱管理
        </button>
        <button class="tab-button" :class="{ active: activeTab === 'community' }" @click="activeTab = 'community'">
          <i class="fas fa-comments"></i> 互动社区管理
        </button>
        <button class="tab-button" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
          <i class="fas fa-users"></i> 用户管理
        </button>
        <button class="tab-button" :class="{ active: activeTab === 'ai-config' }" @click="activeTab = 'ai-config'; loadAIConfig()">
          <i class="fas fa-robot"></i> AI配置
        </button>
      </div>

      <div class="admin-content">
        <div v-if="activeTab === 'resources'" class="tab-content">
          <div class="content-header">
            <h2>文化资源管理</h2>
            <button class="btn btn-primary" @click="showAddResourceModal = true">
              <i class="fas fa-plus"></i> 添加资源
            </button>
          </div>
          <div class="resource-table-container">
            <table class="admin-table">
              <thead>
                <tr><th>ID</th><th>标题</th><th>类型</th><th>创建时间</th><th>状态</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr v-for="resource in resources" :key="resource.id">
                  <td>{{ resource.id }}</td>
                  <td>{{ resource.title }}</td>
                  <td>{{ resource.type }}</td>
                  <td>{{ formatDate(resource.createdAt) }}</td>
                  <td><span :class="['status-badge', resource.status]">{{ resource.status === 'published' ? '已发布' : '草稿' }}</span></td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="editResource(resource)"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-danger" @click="deleteResource(resource.id)"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'knowledge-graph'" class="tab-content">
          <div class="content-header">
            <h2>知识图谱管理</h2>
            <button class="btn btn-primary" @click="openAddNodeModal"><i class="fas fa-plus"></i> 添加节点</button>
          </div>
          <div class="graph-table-container">
            <table class="admin-table">
              <thead>
                <tr><th>ID</th><th>节点名称</th><th>分类</th><th>类型</th><th>描述</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr v-for="node in graphNodes" :key="node.id">
                  <td>{{ node.id }}</td>
                  <td>{{ node.name }}</td>
                  <td><span class="status-badge" :style="{ backgroundColor: node.color, color: 'white' }">{{ node.category }}</span></td>
                  <td>{{ nodeTypeLabel(node.node_type) }}</td>
                  <td class="node-desc">{{ node.description || '-' }}</td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="editNode(node)"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-danger" @click="deleteNode(node.id)"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="showAddNodeModal" class="modal-overlay" @click.self="showAddNodeModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ nodeForm.id ? '编辑节点' : '添加节点' }}</h3>
              <button class="modal-close" @click="showAddNodeModal = false">&times;</button>
            </div>
            <div class="modal-body">
              <div v-if="nodeFormError" class="error-message">{{ nodeFormError }}</div>
              <div class="form-group">
                <label>节点名称 <span class="required">*</span></label>
                <input type="text" v-model="nodeForm.name" placeholder="如：柳宗元" maxlength="50" />
              </div>
              <div class="form-group">
                <label>分类</label>
                <select v-model="nodeForm.category" @change="onCategoryChange">
                  <option v-for="cat in kgCategories" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>节点类型</label>
                <select v-model="nodeForm.node_type">
                  <option value="person">person（人物）</option>
                  <option value="place">place（地点）</option>
                  <option value="concept">concept（概念）</option>
                  <option value="culture">culture（文化）</option>
                </select>
              </div>
              <div class="form-group">
                <label>描述</label>
                <textarea v-model="nodeForm.description" rows="3" placeholder="节点简介（选填）"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline" @click="showAddNodeModal = false">取消</button>
              <button class="btn btn-primary" @click="saveNode" :disabled="nodeSaving">{{ nodeSaving ? '保存中...' : '保存' }}</button>
            </div>
          </div>
        </div>

        <div v-if="showAddUserModal" class="modal-overlay" @click.self="showAddUserModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ userForm.id ? '编辑用户' : '添加用户' }}</h3>
              <button class="modal-close" @click="showAddUserModal = false">&times;</button>
            </div>
            <div class="modal-body">
              <div v-if="userFormError" class="error-message">{{ userFormError }}</div>
              <div class="form-group">
                <label>用户名 <span class="required">*</span></label>
                <input type="text" v-model="userForm.username" placeholder="至少3个字符" maxlength="80" />
              </div>
              <div class="form-group">
                <label>邮箱 <span class="required">*</span></label>
                <input type="email" v-model="userForm.email" placeholder="user@example.com" maxlength="120" />
              </div>
              <div class="form-group">
                <label>密码 {{ userForm.id ? '（留空则不修改）' : '*' }}</label>
                <input type="password" v-model="userForm.password" placeholder="至少6个字符" />
              </div>
              <div class="form-group">
                <label>角色</label>
                <select v-model="userForm.role">
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="form-group">
                <label>账号状态</label>
                <select v-model="userForm.is_active">
                  <option :value="true">正常</option>
                  <option :value="false">禁用</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline" @click="showAddUserModal = false">取消</button>
              <button class="btn btn-primary" @click="saveUser" :disabled="userSaving">{{ userSaving ? '保存中...' : '保存' }}</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'community'" class="tab-content">
          <div class="content-header">
            <h2>互动社区管理</h2>
            <div class="filter-buttons">
              <button class="btn btn-sm btn-outline" :class="{ active: postFilter === 'all' }" @click="postFilter = 'all'">全部</button>
              <button class="btn btn-sm btn-outline" :class="{ active: postFilter === 'pending' }" @click="postFilter = 'pending'">待审核</button>
              <button class="btn btn-sm btn-outline" :class="{ active: postFilter === 'approved' }" @click="postFilter = 'approved'">已审核</button>
            </div>
          </div>
          <div class="post-table-container">
            <table class="admin-table">
              <thead>
                <tr><th>ID</th><th>标题</th><th>作者</th><th>发布时间</th><th>状态</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr v-for="post in filteredPosts" :key="post.id">
                  <td>{{ post.id }}</td>
                  <td>{{ post.title }}</td>
                  <td>{{ post.author }}</td>
                  <td>{{ formatDate(post.createdAt) }}</td>
                  <td><span :class="['status-badge', post.status]">{{ post.status === 'approved' ? '已审核' : '待审核' }}</span></td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="viewPost(post.id)"><i class="fas fa-eye"></i></button>
                    <button class="btn btn-sm btn-warning" v-if="post.status !== 'approved'" @click="approvePost(post.id)"><i class="fas fa-check"></i></button>
                    <button class="btn btn-sm btn-danger" @click="deletePost(post.id)"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'users'" class="tab-content">
          <div class="content-header">
            <h2>用户管理</h2>
            <button class="btn btn-primary" @click="userForm = { id: null, username: '', email: '', password: '', role: 'user', is_active: true }; userFormError = ''; showAddUserModal = true">
              <i class="fas fa-plus"></i> 添加用户
            </button>
          </div>
          <div class="user-table-container">
            <table class="admin-table">
              <thead>
                <tr><th>ID</th><th>用户名</th><th>邮箱</th><th>注册时间</th><th>角色</th><th>状态</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id" :class="{ 'admin-row': user.role === 'admin' }">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td><span :class="['status-badge', user.role === 'admin' ? 'admin' : 'user']">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span></td>
                  <td><span :class="['status-badge', user.is_active ? 'active' : 'inactive']">{{ user.is_active ? '正常' : '禁用' }}</span></td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="editUser(user)"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-danger" @click="deleteUser(user)" :disabled="user.role === 'admin' && user.username === currentUser.username"><i class="fas fa-trash"></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'ai-config'" class="tab-content">
          <div class="content-header">
            <h2>AI 服务商配置</h2>
            <div class="header-actions">
              <button class="btn btn-outline" @click="testAIConnection" :disabled="aiConfigTesting">
                <i class="fas fa-plug"></i> {{ aiConfigTesting ? '测试中...' : '测试连接' }}
              </button>
              <button class="btn btn-danger-outline" @click="clearAIConfig" :disabled="aiConfigSaving">
                <i class="fas fa-eraser"></i> 清除配置
              </button>
              <button class="btn btn-primary" @click="saveAIConfig" :disabled="aiConfigSaving">
                <i class="fas fa-save"></i> {{ aiConfigSaving ? '保存中...' : '保存配置' }}
              </button>
            </div>
          </div>
          <div v-if="aiConfigError" class="ai-config-error">{{ aiConfigError }}</div>
          <div v-if="aiConfigSuccess" class="ai-config-success">{{ aiConfigSuccess }}</div>
          <div class="ai-config-card">
            <div class="ai-config-card-header">
              <i class="fas fa-robot"></i>
              <div>
                <h3>大模型接口配置</h3>
                <p>支持所有 OpenAI 兼容格式的服务商（豆包、通义千问、文心一言、OpenAI 等）</p>
              </div>
            </div>
            <div class="ai-config-body">
              <div class="form-row">
                <div class="form-group">
                  <label>服务商预设</label>
                  <select v-model="selectedPreset" @change="applyPreset">
                    <option value="">手动配置</option>
                    <option v-for="p in aiPresets" :key="p.name" :value="p.name">{{ p.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>服务商名称</label>
                  <input type="text" v-model="aiConfig.provider_name" placeholder="如：字节豆包" />
                </div>
              </div>
              <div class="form-group">
                <label>接口地址 (Base URL)</label>
                <input type="text" v-model="aiConfig.api_base_url" placeholder="https://ark.cn-beijing.volces.com/api/v3" />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>模型名称</label>
                  <input type="text" v-model="aiConfig.model" placeholder="如：doubao-pro-32k" />
                </div>
                <div class="form-group">
                  <label>API Key</label>
                  <input type="text" v-model="aiConfig.api_key" placeholder="输入 API Key" />
                </div>
              </div>
              <div class="ai-config-hint">
                <i class="fas fa-info-circle"></i>
                <span>配置保存后立即生效，无需重启。API Key 已脱敏存储，仅显示后4位。</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api'

const mockAdminService = {
  getStats: async () => ({ resourceCount: 42, graphNodeCount: 128, postCount: 256, userCount: 1024 }),
  getResources: async () => [
    { id: 1, title: '岳麓书院历史', type: '历史建筑', createdAt: '2024-01-15T08:30:00', status: 'published' },
    { id: 2, title: '岳阳楼记赏析', type: '文学作品', createdAt: '2024-01-16T14:20:00', status: 'published' },
    { id: 3, title: '湘菜文化研究', type: '饮食文化', createdAt: '2024-01-17T10:15:00', status: 'draft' }
  ],
  getPosts: async () => [
    { id: 1, title: '讨论湖湘文化的现代意义', author: 'user1', createdAt: '2024-01-18T09:45:00', status: 'approved' },
    { id: 2, title: '请教关于曾国藩家训的解读', author: 'user2', createdAt: '2024-01-18T11:30:00', status: 'pending' },
    { id: 3, title: '分享一次湖南文化之旅', author: 'user3', createdAt: '2024-01-18T15:20:00', status: 'approved' }
  ]
}

export default {
  name: 'AdminPage',
  setup() {
    const router = useRouter()
    const activeTab = ref('resources')
    const postFilter = ref('all')
    const resourceCount = ref(0)
    const graphNodeCount = ref(0)
    const postCount = ref(0)
    const userCount = ref(0)
    const resources = ref([])
    const graphNodes = ref([])
    const posts = ref([])
    const users = ref([])
    const user = ref(null)
    const currentUser = ref(null)
    const showAddResourceModal = ref(false)
    const showAddNodeModal = ref(false)
    const showAddUserModal = ref(false)
    const userForm = ref({ id: null, username: '', email: '', password: '', role: 'user', is_active: true })
    const userFormError = ref('')
    const userSaving = ref(false)
    const kgCategories = ref([
      { name: '历史人物', color: '#2ecc71', nodeType: 'person' },
      { name: '历史遗迹', color: '#e74c3c', nodeType: 'place' },
      { name: '文化遗产', color: '#9b59b6', nodeType: 'culture' },
      { name: '文学艺术', color: '#f39c12', nodeType: 'culture' },
      { name: '哲学思想', color: '#3498db', nodeType: 'concept' },
    ])
    const nodeForm = ref({ id: null, name: '', description: '', category: '历史人物', node_type: 'person', color: '#2ecc71' })
    const nodeFormError = ref('')
    const nodeSaving = ref(false)
    const aiPresets = [
      { name: '字节豆包', api_base_url: 'https://ark.cn-beijing.volces.com/api/v3', model: 'doubao-pro-32k' },
      { name: '阿里通义千问', api_base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-turbo' },
      { name: '百度文心一言', api_base_url: 'https://qianfan.baidubce.com/v2', model: 'ernie-3.5-turbo' },
      { name: 'OpenAI', api_base_url: 'https://api.openai.com/v1', model: 'gpt-3.5-turbo' },
    ]
    const selectedPreset = ref('')
    const aiConfig = ref({ provider_name: '', api_base_url: '', api_key: '', model: '' })
    const aiConfigSaving = ref(false)
    const aiConfigTesting = ref(false)
    const aiConfigError = ref('')
    const aiConfigSuccess = ref('')

    const applyPreset = () => {
      if (!selectedPreset.value) return
      const preset = aiPresets.find(p => p.name === selectedPreset.value)
      if (preset) {
        aiConfig.value.provider_name = preset.name
        aiConfig.value.api_base_url = preset.api_base_url
        aiConfig.value.model = preset.model
      }
    }
    const filteredPosts = computed(() => postFilter.value === 'all' ? posts.value : posts.value.filter(p => p.status === postFilter.value))
    const formatDate = (ds) => {
      if (!ds) return ''
      return new Date(ds).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    }
    const nodeTypeLabel = (type) => ({ person: '人物', place: '地点', concept: '概念', culture: '文化', category: '分类' }[type] || type || '-')

    const loadData = async () => {
      try {
        const stats = await mockAdminService.getStats()
        resourceCount.value = stats.resourceCount
        graphNodeCount.value = stats.graphNodeCount
        postCount.value = stats.postCount
        userCount.value = stats.userCount
        resources.value = await mockAdminService.getResources()
        const kgRes = await request('/knowledge/nodes', 'GET')
        if (kgRes.success) { graphNodes.value = kgRes.data.filter(n => n.level !== 1); graphNodeCount.value = graphNodes.value.length }
        posts.value = await mockAdminService.getPosts()
        await loadUsers()
        const storedUser = localStorage.getItem('user')
        if (storedUser) { currentUser.value = JSON.parse(storedUser); user.value = currentUser.value }
      } catch (e) { console.error('加载管理数据失败:', e) }
    }
    const editResource = (r) => { alert(`编辑资源: ${r.title}`) }
    const deleteResource = (id) => { if (confirm('确定要删除这个资源吗？')) { resources.value = resources.value.filter(r => r.id !== id); resourceCount.value--; alert('资源已删除') } }
    const openAddNodeModal = () => { nodeForm.value = { id: null, name: '', description: '', category: '历史人物', node_type: 'person', color: '#2ecc71' }; nodeFormError.value = ''; showAddNodeModal.value = true }
    const editNode = (node) => { nodeForm.value = { id: node.id, name: node.name, description: node.description || '', category: node.category, node_type: node.node_type, color: node.color || '#95a5a6' }; nodeFormError.value = ''; showAddNodeModal.value = true }
    const onCategoryChange = () => { const cat = kgCategories.value.find(c => c.name === nodeForm.value.category); if (cat) { nodeForm.value.node_type = cat.nodeType; nodeForm.value.color = cat.color } }
    const saveNode = async () => {
      if (!nodeForm.value.name.trim()) { nodeFormError.value = '节点名称不能为空'; return }
      nodeSaving.value = true; nodeFormError.value = ''
      try {
        const payload = { name: nodeForm.value.name.trim(), description: nodeForm.value.description, category: nodeForm.value.category, node_type: nodeForm.value.node_type, color: nodeForm.value.color, level: 2 }
        if (nodeForm.value.id) await request(`/knowledge/nodes/${nodeForm.value.id}`, 'PUT', payload)
        else await request('/knowledge/nodes', 'POST', payload)
        showAddNodeModal.value = false
        const kgRes = await request('/knowledge/nodes', 'GET')
        if (kgRes.success) { graphNodes.value = kgRes.data.filter(n => n.level !== 1); graphNodeCount.value = graphNodes.value.length }
      } catch (err) { nodeFormError.value = err.message || '保存失败' }
      finally { nodeSaving.value = false }
    }
    const deleteNode = async (id) => {
      if (!confirm('确定要删除这个节点吗？关联的连线也会一并删除。')) return
      try { await request(`/knowledge/nodes/${id}`, 'DELETE'); graphNodes.value = graphNodes.value.filter(n => n.id !== id); graphNodeCount.value = graphNodes.value.length }
      catch (err) { alert('删除失败: ' + (err.message || '未知错误')) }
    }
    const viewPost = (id) => { alert(`查看帖子ID: ${id}`) }
    const approvePost = (id) => { const p = posts.value.find(x => x.id === id); if (p) { p.status = 'approved'; alert('帖子已审核通过') } }
    const deletePost = (id) => { if (confirm('确定要删除这个帖子吗？')) { posts.value = posts.value.filter(p => p.id !== id); postCount.value--; alert('帖子已删除') } }
    const loadUsers = async () => { try { const res = await request('/admin/users/?page=1&per_page=50', 'GET'); users.value = res.users || []; userCount.value = res.total || 0 } catch (e) { console.error('加载用户列表失败:', e) } }
    const editUser = (u) => { userForm.value = { id: u.id, username: u.username, email: u.email, password: '', role: u.role, is_active: u.is_active }; userFormError.value = ''; showAddUserModal.value = true }
    const saveUser = async () => {
      userFormError.value = ''
      if (!userForm.value.username || userForm.value.username.length < 3) { userFormError.value = '用户名至少3个字符'; return }
      if (!userForm.value.email || !userForm.value.email.includes('@')) { userFormError.value = '邮箱格式不正确'; return }
      if (!userForm.value.id && (!userForm.value.password || userForm.value.password.length < 6)) { userFormError.value = '密码至少6个字符'; return }
      userSaving.value = true
      try {
        const payload = { username: userForm.value.username, email: userForm.value.email, role: userForm.value.role, is_active: userForm.value.is_active }
        if (userForm.value.password) payload.password = userForm.value.password
        if (userForm.value.id) await request(`/admin/users/${userForm.value.id}`, 'PUT', payload)
        else await request('/admin/users/', 'POST', payload)
        showAddUserModal.value = false; await loadUsers()
      } catch (e) { userFormError.value = e.response?.data?.message || '保存失败' }
      finally { userSaving.value = false }
    }
    const deleteUser = async (u) => {
      if (u.role === 'admin' && u.username === currentUser.value?.username) { alert('无法删除当前登录的管理员账号'); return }
      if (!confirm(`确定要删除用户 ${u.username} 吗？`)) return
      try { await request(`/admin/users/${u.id}`, 'DELETE'); await loadUsers() }
      catch (e) { alert('删除失败: ' + (e.response?.data?.message || e.message)) }
    }
    const loadAIConfig = async () => {
      aiConfigError.value = ''; aiConfigSuccess.value = ''
      try {
        const res = await request('/admin/ai-config/', 'GET')
        aiConfig.value = { provider_name: res.provider_name || '', api_base_url: res.api_base_url || '', api_key: res.api_key || '', model: res.model || '' }
        const match = aiPresets.find(p => p.api_base_url === res.api_base_url)
        selectedPreset.value = match ? match.name : ''
      } catch (e) { aiConfigError.value = e.response?.data?.message || '加载配置失败' }
    }
    const saveAIConfig = async () => {
      aiConfigError.value = ''; aiConfigSuccess.value = ''; aiConfigSaving.value = true
      try { await request('/admin/ai-config/', 'PUT', { ...aiConfig.value }); aiConfigSuccess.value = '配置保存成功，已立即生效'; setTimeout(() => { aiConfigSuccess.value = '' }, 3000) }
      catch (e) { aiConfigError.value = e.message || '保存失败' }
      finally { aiConfigSaving.value = false }
    }
    const testAIConnection = async () => {
      aiConfigError.value = ''; aiConfigSuccess.value = ''; aiConfigTesting.value = true
      try { const res = await request('/admin/ai-config/test', 'POST', {}); aiConfigSuccess.value = `连接成功！AI 回复：${res.reply || res.message}`; setTimeout(() => { aiConfigSuccess.value = '' }, 5000) }
      catch (e) { aiConfigError.value = `连接失败：${e.message || '未知错误'}` }
      finally { aiConfigTesting.value = false }
    }
    const clearAIConfig = async () => {
      if (!confirm('确定要清除所有 AI 配置吗？API Key 将被清空。')) return
      aiConfigError.value = ''; aiConfigSuccess.value = ''; aiConfigSaving.value = true
      try { const res = await request('/admin/ai-config/', 'DELETE'); aiConfig.value = { provider_name: res.config.provider_name, api_base_url: res.config.api_base_url, api_key: res.config.api_key, model: res.config.model }; selectedPreset.value = ''; aiConfigSuccess.value = '配置已清除'; setTimeout(() => { aiConfigSuccess.value = '' }, 3000) }
      catch (e) { aiConfigError.value = e.message || '清除失败' }
      finally { aiConfigSaving.value = false }
    }
    watch(activeTab, (t) => { if (t === 'ai-config') loadAIConfig() })
    onMounted(() => { loadData() })
    return {
      activeTab, postFilter, resourceCount, graphNodeCount, postCount, userCount,
      resources, graphNodes, posts, users, user, currentUser,
      showAddResourceModal, showAddNodeModal, showAddUserModal,
      userForm, userFormError, userSaving,
      kgCategories, nodeForm, nodeFormError, nodeSaving,
      openAddNodeModal, onCategoryChange, saveNode, nodeTypeLabel,
      filteredPosts, formatDate,
      editResource, deleteResource, editNode, deleteNode,
      viewPost, approvePost, deletePost,
      editUser, deleteUser, saveUser, loadUsers,
      aiPresets, selectedPreset, aiConfig, aiConfigSaving, aiConfigTesting, aiConfigError, aiConfigSuccess,
      applyPreset, loadAIConfig, saveAIConfig, testAIConnection, clearAIConfig
    }
  }
}
</script>

<style scoped>
:root {
  --primary-color: #C8102E; --secondary-color: #1E40AF; --accent-color: #D97706;
  --bg-color: #F9FAFB; --text-color: #1F2937; --light-text: #6B7280; --border-color: #E5E7EB;
  --success-color: #10B981; --warning-color: #F59E0B; --danger-color: #EF4444; --info-color: #3B82F6;
}
.admin-page { padding: 2rem 0; min-height: calc(100vh - 100px); background-color: var(--bg-color); }
.admin-container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }
.admin-header { margin-bottom: 2rem; text-align: center; }
.admin-header h1 { font-size: 2.5rem; color: black; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.admin-header p { color: var(--light-text); font-size: 1.1rem; }
.admin-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 1rem; transition: transform .2s, box-shadow .2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
.stat-icon { font-size: 2rem; color: var(--primary-color); background: rgba(200,16,46,0.1); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.stat-content { flex: 1; }
.stat-number { font-size: 2rem; font-weight: bold; color: var(--text-color); line-height: 1; }
.stat-label { color: var(--light-text); font-size: 0.9rem; margin-top: 0.25rem; }
.admin-tabs { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.tab-button { padding: 0.75rem 1.5rem; border: 1px solid var(--border-color); background: white; color: var(--text-color); border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: 500; transition: all .2s; display: flex; align-items: center; gap: 0.5rem; }
.tab-button:hover { background: var(--primary-color); color: white; border-color: var(--primary-color); }
.tab-button.active { background: var(--primary-color); color: white; border-color: var(--primary-color); }
.admin-content { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 2rem; }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.content-header h2 { color: var(--text-color); font-size: 1.5rem; margin: 0; }
.filter-buttons { display: flex; gap: 0.5rem; }
.admin-table { width: 100%; border-collapse: collapse; }
.admin-table th { background: var(--bg-color); padding: 1rem; text-align: left; font-weight: 600; color: var(--text-color); border-bottom: 2px solid var(--border-color); }
.admin-table td { padding: 1rem; border-bottom: 1px solid var(--border-color); }
.admin-table tr:hover { background: var(--bg-color); }
.admin-table tr.admin-row { background: rgba(200,16,46,0.05); }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 500; }
.status-badge.published, .status-badge.approved { background: rgba(16,185,129,0.1); color: var(--success-color); }
.status-badge.draft, .status-badge.pending { background: rgba(245,158,11,0.1); color: var(--warning-color); }
.status-badge.admin { background: rgba(200,16,46,0.1); color: var(--primary-color); }
.status-badge.user { background: rgba(59,130,246,0.1); color: var(--info-color); }
.status-badge.active { background: rgba(16,185,129,0.1); color: var(--success-color); }
.status-badge.inactive { background: rgba(107,114,128,0.1); color: var(--light-text); }
.btn { padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; cursor: pointer; transition: all .2s; border: none; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.5rem; }
.btn-primary { background: var(--primary-color); color: white; }
.btn-primary:hover { background: #A80D27; }
.btn-outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-color); }
.btn-outline:hover { background: var(--primary-color); color: white; border-color: var(--primary-color); }
.btn-outline.active { background: var(--primary-color); color: white; border-color: var(--primary-color); }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.8rem; }
.btn-info { background: var(--info-color); color: white; }
.btn-info:hover { background: #2563EB; }
.btn-danger { background: var(--danger-color); color: white; }
.btn-danger:hover { background: #DC2626; }
.btn-danger:disabled { background: var(--light-text); cursor: not-allowed; }
.btn-warning { background: var(--warning-color); color: white; }
.btn-warning:hover { background: #D97706; }
.admin-table .btn-sm.btn-info { background: #3B82F6 !important; color: #fff !important; padding: 0.3rem 0.5rem; margin-right: 0.4rem; }
.admin-table .btn-sm.btn-info:hover { background: #2563EB !important; }
.admin-table .btn-sm.btn-danger { background: #EF4444 !important; color: #fff !important; padding: 0.3rem 0.5rem; }
.admin-table .btn-sm.btn-danger:hover { background: #DC2626 !important; }
.admin-table .btn-sm.btn-danger:disabled { background: #9CA3AF !important; color: #fff !important; }
@media (max-width: 768px) {
  .admin-stats { grid-template-columns: 1fr; }
  .admin-tabs { justify-content: center; }
  .content-header { flex-direction: column; align-items: flex-start; }
  .admin-table { display: block; overflow-x: auto; }
}
.node-desc { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--light-text); font-size: 0.85rem; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-content { background: white; border-radius: 12px; width: 90%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.2rem 1.5rem; border-bottom: 1px solid var(--border-color); }
.modal-header h3 { margin: 0; font-size: 1.15rem; color: var(--text-color); }
.modal-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--light-text); padding: 0; line-height: 1; }
.modal-close:hover { color: var(--text-color); }
.modal-body { padding: 1.5rem; }
.modal-body .form-group { margin-bottom: 1rem; }
.modal-body label { display: block; margin-bottom: 0.4rem; font-weight: 600; font-size: 0.9rem; color: var(--text-color); }
.modal-body .required { color: var(--danger-color); }
.modal-body input, .modal-body select, .modal-body textarea { width: 100%; padding: 0.55rem 0.75rem; border: 1px solid var(--border-color); border-radius: 6px; font-size: 0.9rem; font-family: inherit; box-sizing: border-box; }
.modal-body input:focus, .modal-body select:focus, .modal-body textarea:focus { outline: none; border-color: var(--primary-color); }
.modal-body .error-message { background: #fef2f2; color: var(--danger-color); padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.85rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid var(--border-color); }
.ai-config-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; width: 100%; }
.ai-config-card-header { display: flex; align-items: center; gap: 1rem; padding: 1.5rem 2rem; background: linear-gradient(135deg, #C8102E 0%, #8B0A1F 100%); color: white; }
.ai-config-card-header i { font-size: 2rem; opacity: 0.9; }
.ai-config-card-header h3 { margin: 0 0 0.2rem 0; font-size: 1.15rem; }
.ai-config-card-header p { margin: 0; font-size: 0.85rem; opacity: 0.85; }
.ai-config-body { padding: 2rem; }
.ai-config-body .form-row { display: flex; gap: 1.5rem; margin-bottom: 1.2rem; }
.ai-config-body .form-row .form-group { flex: 1; }
.ai-config-body .form-group { margin-bottom: 1.2rem; }
.ai-config-body label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem; color: var(--text-color); }
.ai-config-body input, .ai-config-body select { width: 100%; padding: 0.65rem 0.85rem !important; border: 1.5px solid #E5E7EB !important; border-radius: 8px !important; font-size: 0.9rem !important; box-sizing: border-box; transition: border-color .2s; background: white !important; color: var(--text-color) !important; }
.ai-config-body input:focus, .ai-config-body select:focus { outline: none !important; border-color: #C8102E !important; box-shadow: 0 0 0 3px rgba(200,16,46,0.1) !important; }
.ai-config-hint { display: flex; align-items: center; gap: 0.5rem; margin-top: 1.5rem; padding: 0.8rem 1rem; background: rgba(30,64,175,0.06); border-left: 3px solid var(--secondary-color); border-radius: 6px; font-size: 0.85rem; color: var(--light-text); }
.ai-config-hint i { color: var(--secondary-color); }
.ai-config-error { background: #fef2f2; color: #C8102E; padding: 0.85rem 1.2rem; border-radius: 8px; margin-bottom: 1.2rem; font-size: 0.9rem; border-left: 3px solid #C8102E; }
.ai-config-success { background: #ecfdf5; color: #059669; padding: 0.85rem 1.2rem; border-radius: 8px; margin-bottom: 1.2rem; font-size: 0.9rem; border-left: 3px solid #059669; }
.header-actions { display: flex; gap: 0.6rem; }
.btn-danger-outline { background: white; color: #EF4444; border: 1.5px solid #FECACA; padding: 0.55rem 1rem; border-radius: 8px; font-size: 0.88rem; cursor: pointer; font-weight: 500; transition: all .2s; display: inline-flex; align-items: center; gap: 0.4rem; }
.btn-danger-outline:hover:not(:disabled) { background: #FEF2F2; border-color: #EF4444; }
.btn-danger-outline:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

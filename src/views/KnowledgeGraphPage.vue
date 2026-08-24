<template>
  <div class="knowledge-graph-container">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
        <span>返回数字化展示</span>
      </button>
    </div>
    
    <div class="knowledge-graph-wrapper">
      <!-- 图谱头部 -->
      <div class="graph-header">
        <h1>湖湘文化知识图谱</h1>
        <p>探索湖湘文化中的人物、事件、地点和文化元素之间的关联关系</p>
      </div>

      <!-- 控制按钮 -->
      <div class="graph-controls">
        <button class="btn btn-primary" @click="resetGraph">重置视图</button>
        <button class="btn btn-outline" @click="zoomIn">放大</button>
        <button class="btn btn-outline" @click="zoomOut">缩小</button>
        <button class="btn btn-outline" @click="toggleAnimation">{{ isAnimating ? '暂停动画' : '播放动画' }}</button>
      </div>

      <!-- 图谱画布 -->
      <div class="graph-canvas" ref="graphCanvas" @wheel.prevent="handleWheel">
        <svg id="graph-svg" ref="graphSvg" @mousedown="startDrag" @mousemove="handleDrag" @mouseup="endDrag" @mouseleave="endDrag"></svg>
        <div v-if="isLoading" class="graph-loading">
          <div class="loading-spinner"></div>
        </div>
        <div v-if="hasError" class="graph-error">
          <div class="graph-error-content">
            <div class="graph-error-icon">
              <i class="fas fa-exclamation-circle"></i>
            </div>
            <h3>加载失败</h3>
            <p>无法加载知识图谱数据，请稍后重试。</p>
            <button class="btn btn-primary" @click="loadGraphData">重试</button>
          </div>
        </div>
        <div class="zoom-hint">
          <i class="fas fa-search-plus"></i> 鼠标滚轮缩放 | <i class="fas fa-hand-pointer"></i> 拖拽移动
        </div>
        <!-- 图例 -->
        <div class="graph-legend">
          <h4>图例</h4>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #2ecc71;"></div>
            <span>历史人物</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #e74c3c;"></div>
            <span>历史遗迹</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #9b59b6;"></div>
            <span>文化遗产</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #f39c12;"></div>
            <span>文学艺术</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: #3498db;"></div>
            <span>哲学思想</span>
          </div>
        </div>
      </div>

      <!-- 节点详情面板 -->
      <transition name="slide">
        <div v-if="showNodeDetail && selectedNode" class="node-detail-panel">
          <div class="detail-header" :style="{ borderLeftColor: selectedNode.color || '#95a5a6' }">
            <div class="detail-title-row">
              <span class="detail-category-badge" :style="{ backgroundColor: selectedNode.color || '#95a5a6' }">
                {{ selectedNode.category || '未分类' }}
              </span>
              <button class="detail-close" @click="closeNodeDetail">&times;</button>
            </div>
            <h2 class="detail-name">{{ selectedNode.name }}</h2>
            <p class="detail-type">类型：{{ nodeTypeLabel(selectedNode.node_type) }}</p>
          </div>
          <div class="detail-body">
            <div v-if="selectedNode.description" class="detail-description">
              <h4>节点介绍</h4>
              <p>{{ selectedNode.description }}</p>
            </div>
            <div v-else class="detail-empty">
              <i class="fas fa-info-circle"></i>
              <p>暂无节点介绍</p>
            </div>
          </div>
        </div>
      </transition>
      <div v-if="showNodeDetail" class="detail-overlay" @click="closeNodeDetail"></div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api'
import '../assets/css/knowledge-graph.css'

export default {
  name: 'KnowledgeGraphPage',

  setup() {
    // 获取全局事件总线和路由实例
    const eventBus = inject('$eventBus')
    const router = useRouter()
    
    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    // 显示提示消息
    const showAlert = (message, type = 'info') => {
      if (eventBus) {
        eventBus.emit('show-alert', { message, type })
      } else {
        // 如果没有eventBus，不显示任何弹窗，只在控制台打印消息
        console.log(`[${type}] ${message}`)
      }
    }
    
    // 引用
    const graphCanvas = ref(null)
    const graphSvg = ref(null)

    // 状态
    const nodes = ref([])
    const links = ref([])
    const isLoading = ref(true)
    const hasError = ref(false)
    const isAnimating = ref(false)
    const isDragging = ref(false)
    const dragStart = ref({ x: 0, y: 0 })
    const transform = ref({ x: 0, y: 0, scale: 0.9 })
    const centerPos = ref({ x: 0, y: 0 })

    // 单个节点拖拽
    const draggedNode = ref(null)
    const nodeDragMoved = ref(false)
    const dragCache = ref({ rect: null, links: [] })

    // 节点类型中英文映射
    const nodeTypeLabel = (type) => {
      const map = { person: '人物', place: '地点', concept: '概念', culture: '文化', category: '分类' }
      return map[type] || type || '-'
    }

    // 节点详情面板
    const selectedNode = ref(null)
    const showNodeDetail = ref(false)

    const openNodeDetail = (node) => {
      selectedNode.value = node
      showNodeDetail.value = true
    }

    const closeNodeDetail = () => {
      showNodeDetail.value = false
      selectedNode.value = null
    }

    // 导览动画相关
    const nodeElements = new Map() // id -> { circle, text, baseRadius }
    const highlightedNodeId = ref(null)
    let animationTimer = null

    // 加载图谱数据
    const loadGraphData = async () => {
      isLoading.value = true
      hasError.value = false

      try {
        const res = await request('/knowledge/graph', 'GET')
        if (res.success && res.data) {
          nodes.value = res.data.nodes.map(n => ({
            id: n.id,
            name: n.name,
            level: n.level,
            x: n.x || 0,
            y: n.y || 0,
            color: n.color || '#95a5a6',
            description: n.description || '',
            node_type: n.node_type || '',
            category: n.category || '',
            is_virtual: n.is_virtual || false,
          }))
          links.value = res.data.links.map(l => ({
            source: l.source,
            target: l.target,
            level: l.level || 3,
            relationship_type: l.relationship_type || '',
          }))
          calculateNodePositions()
          renderGraph()
        } else {
          throw new Error('接口返回数据异常')
        }
      } catch (error) {
        console.error('加载知识图谱数据失败:', error)
        hasError.value = true
        showAlert('知识图谱加载失败，请稍后重试', 'error')
      } finally {
        isLoading.value = false
      }
    }

    // 径向树布局：根节点居中，分类节点环形分布，子节点在各自扇区内排列
    const calculateNodePositions = () => {
      const nodeMap = new Map()
      nodes.value.forEach(node => nodeMap.set(node.id, node))

      // 父节点 -> 子节点映射（只统计 level2->level3 的层级连线）
      const parentToChildren = new Map()
      links.value.forEach(link => {
        const src = nodeMap.get(link.source)
        const tgt = nodeMap.get(link.target)
        if (src && tgt && src.level === 2 && tgt.level === 3) {
          if (!parentToChildren.has(link.source)) {
            parentToChildren.set(link.source, [])
          }
          parentToChildren.get(link.source).push(link.target)
        }
      })

      // 第一层：根节点居中
      const rootNode = nodes.value.find(n => n.level === 1)
      if (rootNode) {
        rootNode.x = 0
        rootNode.y = 0
      }

      // 第二层：分类节点，按子节点数量分配角度扇区
      const categoryNodes = nodes.value.filter(n => n.level === 2).sort((a, b) => {
        const ca = parentToChildren.get(a.id)?.length || 0
        const cb = parentToChildren.get(b.id)?.length || 0
        return cb - ca
      })

      const totalChildren = categoryNodes.reduce((sum, c) =>
        sum + (parentToChildren.get(c.id)?.length || 0), 0)
      const categoryRadius = 180
      const childRadius = 400
      const gapAngle = Math.PI / 22.5 // 扇区间8°间隙
      const usableAngle = Math.PI * 2 - gapAngle * categoryNodes.length

      let currentAngle = -Math.PI / 2 // 从正上方开始
      categoryNodes.forEach(catNode => {
        const childCount = parentToChildren.get(catNode.id)?.length || 1
        // 按子节点数量比例分配扇区
        const sectorAngle = (childCount / totalChildren) * usableAngle
        const centerAngle = currentAngle + sectorAngle / 2

        // 分类节点位置
        catNode.x = Math.cos(centerAngle) * categoryRadius
        catNode.y = Math.sin(centerAngle) * categoryRadius

        // 第三层：子节点在该扇区内均匀分布
        const children = parentToChildren.get(catNode.id) || []
        children.forEach((childId, idx) => {
          const childNode = nodeMap.get(childId)
          if (childNode) {
            const childAngle = currentAngle + (idx + 0.5) * (sectorAngle / children.length)
            childNode.x = Math.cos(childAngle) * childRadius
            childNode.y = Math.sin(childAngle) * childRadius
          }
        })

        currentAngle += sectorAngle + gapAngle
      })
    }

    // 渲染图谱
    const renderGraph = () => {
      if (!graphSvg.value) return

      const svg = graphSvg.value
      svg.innerHTML = ''
      nodeElements.clear()

      // 设置SVG视口
      const { width, height } = graphCanvas.value.getBoundingClientRect()
      svg.setAttribute('width', width)
      svg.setAttribute('height', height)
      
      // 创建变换组
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
      g.setAttribute('id', 'graph-group')
      // 调整y坐标使图谱向上移动，距离画布上边框20px
      const translateY = 20 + (height * 0.4); // 20px边距 + 画布高度的40%
      centerPos.value = { x: width / 2, y: translateY }
      // 首次渲染或重置后，初始化为居中
      if (transform.value.x === 0 && transform.value.y === 0) {
        transform.value.x = centerPos.value.x
        transform.value.y = centerPos.value.y
      }
      g.setAttribute('transform', `translate(${transform.value.x}, ${transform.value.y}) scale(${transform.value.scale})`)
      svg.appendChild(g)

      // 创建箭头标记
      createArrowMarkers(svg)

      // 绘制连接线
      links.value.forEach(link => {
        const source = nodes.value.find(n => n.id === link.source)
        const target = nodes.value.find(n => n.id === link.target)
        
        if (source && target) {
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'path')
          
          // 计算贝塞尔曲线控制点
          const dx = target.x - source.x
          const dy = target.y - source.y
          const length = Math.sqrt(dx * dx + dy * dy)
          const tx = source.x + dx * 0.3
          const ty = source.y + dy * 0.3
          const tx2 = source.x + dx * 0.7
          const ty2 = source.y + dy * 0.7
          
          // 设置路径
          const d = `M ${source.x},${source.y} C ${tx},${ty} ${tx2},${ty2} ${target.x},${target.y}`
          line.setAttribute('d', d)
          line.setAttribute('class', `graph-link`)
          line.setAttribute('id', `graph-link-${link.source}-${link.target}`)
          line.setAttribute('data-source', link.source)
          line.setAttribute('data-target', link.target)
          // 统一使用浅灰色连接线
          line.setAttribute('stroke', '#95a5a6')
          line.setAttribute('stroke-width', '2px')
          line.setAttribute('fill', 'none')
          line.setAttribute('opacity', '0.7')
          
          // 添加点击事件
          line.addEventListener('click', () => {
            showAlert(`查看关系: ${source.name} -> ${target.name}`, 'info')
          })
          
          g.appendChild(line)
        }
      })

      // 绘制节点
      nodes.value.forEach(node => {
        // 每个节点用一个 <g> 包裹圆圈和文字，hover 时整体缩放
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
        nodeGroup.setAttribute('class', 'graph-node-group')
        nodeGroup.style.cursor = 'pointer'

        // 创建节点圆圈
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
        circle.setAttribute('cx', node.x)
        circle.setAttribute('cy', node.y)

        // 根据文本长度动态设置节点大小和字号
        const textLength = node.name.length;
        // 按字数分级字号，长文本自动缩小
        let fontSize = '14px'
        if (textLength >= 6) fontSize = '11px'
        else if (textLength >= 5) fontSize = '12px'
        else if (textLength >= 4) fontSize = '13px'
        // 半径根据字号和字数计算，确保文字不溢出
        const charWidth = parseInt(fontSize)
        const radius = Math.max(20, Math.ceil((textLength * charWidth) / 2) + 10);

        circle.setAttribute('r', radius);
        circle.setAttribute('class', `graph-node`);
        circle.setAttribute('fill', node.color || '#95a5a6');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '2px');

        // 创建节点文本
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        text.setAttribute('x', node.x)
        text.setAttribute('y', node.y)
        text.setAttribute('class', 'graph-node-text')
        text.textContent = node.name
        text.setAttribute('font-size', fontSize)
        text.setAttribute('font-family', '"Microsoft YaHei", "SimHei", sans-serif')
        text.setAttribute('fill', 'white')
        text.setAttribute('font-weight', '700')
        text.setAttribute('text-anchor', 'middle')
        text.setAttribute('dy', '0.35em')

        nodeGroup.appendChild(circle)
        nodeGroup.appendChild(text)
        g.appendChild(nodeGroup)

        // 存储元素引用，供导览动画使用
        nodeElements.set(node.id, { circle, text, group: nodeGroup, baseRadius: radius, fontSize })

        // 点击事件 - 打开节点详情（拖拽后不触发）
        nodeGroup.addEventListener('click', () => {
          if (nodeDragMoved.value) return
          openNodeDetail(node)
        })

        // 悬停时整组一起缩放（绕节点中心）
        const hoverTransform = `translate(${node.x}, ${node.y}) scale(1.15) translate(${-node.x}, ${-node.y})`
        nodeGroup.addEventListener('mouseenter', () => {
          if (isAnimating.value || draggedNode.value) return
          nodeGroup.setAttribute('transform', hoverTransform)
          circle.setAttribute('stroke-width', '3px')
        })
        nodeGroup.addEventListener('mouseleave', () => {
          if (draggedNode.value === node) return
          nodeGroup.removeAttribute('transform')
          circle.setAttribute('stroke-width', '2px')
        })

        // 节点拖拽开始
        nodeGroup.addEventListener('mousedown', (e) => {
          e.stopPropagation()
          draggedNode.value = node
          nodeDragMoved.value = false
          // 移除 hover transform，避免干扰拖拽位置
          nodeGroup.removeAttribute('transform')
          circle.setAttribute('stroke-width', '2px')
          // 直接禁用过渡动画（inline style 优先级最高）
          nodeGroup.style.transition = 'none'
          circle.style.transition = 'none'
          text.style.transition = 'none'
          document.body.classList.add('node-dragging')
          // 缓存 SVG 位置和相关连线，避免 mousemove 时重复查询
          if (graphSvg.value) {
            const rect = graphSvg.value.getBoundingClientRect()
            const group = graphSvg.value.querySelector('#graph-group')
            const links = group ? Array.from(group.querySelectorAll('path.graph-link')).filter(p => {
              const s = parseInt(p.getAttribute('data-source'))
              const t = parseInt(p.getAttribute('data-target'))
              return s === node.id || t === node.id
            }) : []
            // 给相关连线也禁用 transition
            links.forEach(p => { p.style.transition = 'none' })
            dragCache.value = { rect, links }
          }
        })

        // 应用当前高亮状态
        if (highlightedNodeId.value !== null) {
          if (node.id === highlightedNodeId.value) {
            circle.setAttribute('r', radius * 1.5)
            circle.setAttribute('stroke', '#f1c40f')
            circle.setAttribute('stroke-width', '4px')
            circle.setAttribute('opacity', '1')
            text.setAttribute('font-size', (parseInt(fontSize) + 2) + 'px')
            text.setAttribute('fill', '#f1c40f')
          } else {
            circle.setAttribute('opacity', '0.35')
            text.setAttribute('opacity', '0.35')
          }
        }
      })
    }

    // 创建箭头标记
    const createArrowMarkers = (svg) => {
      for (let i = 1; i <= 5; i++) {
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker')
        marker.setAttribute('id', `arrowhead-${i}`)
        marker.setAttribute('viewBox', '0 0 10 10')
        marker.setAttribute('refX', '8')
        marker.setAttribute('refY', '5')
        marker.setAttribute('markerWidth', '6')
        marker.setAttribute('markerHeight', '6')
        marker.setAttribute('orient', 'auto-start-reverse')
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        path.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z')
        path.setAttribute('class', `arrowhead arrowhead-level-${i}`)
        
        marker.appendChild(path)
        svg.appendChild(marker)
      }
    }

    // 重置图谱视图
    const resetGraph = () => {
      transform.value = { x: centerPos.value.x, y: centerPos.value.y, scale: 0.9 }
      calculateNodePositions()
      renderGraph()
      showAlert('图谱视图已重置！', 'info')
    }

    // 放大
    const zoomIn = () => {
      transform.value.scale = Math.min(transform.value.scale * 1.2, 3)
      renderGraph()
    }

    // 缩小
    const zoomOut = () => {
      transform.value.scale = Math.max(transform.value.scale / 1.2, 0.5)
      renderGraph()
    }

    // 处理鼠标滚轮缩放
    const handleWheel = (e) => {
      e.preventDefault()
      const delta = e.deltaY > 0 ? -0.1 : 0.1
      transform.value.scale = Math.max(0.5, Math.min(3, transform.value.scale + delta))
      renderGraph()
    }

    // 开始拖拽
    const startDrag = (e) => {
      if (e.target === graphSvg.value) {
        isDragging.value = true
        dragStart.value = { x: e.clientX - transform.value.x, y: e.clientY - transform.value.y }
      }
    }

    // 处理拖拽
    const handleDrag = (e) => {
      if (isDragging.value) {
        transform.value.x = e.clientX - dragStart.value.x
        transform.value.y = e.clientY - dragStart.value.y
        renderGraph()
      }
    }

    // 结束拖拽
    const endDrag = () => {
      isDragging.value = false
    }

    // 单个节点拖拽：mousemove 处理
    const handleNodeDragMove = (e) => {
      if (!draggedNode.value || !dragCache.value.rect) return
      const rect = dragCache.value.rect
      const scale = transform.value.scale
      // 屏幕坐标 → SVG 坐标系（考虑 graph-group 的 translate 和 scale）
      draggedNode.value.x = (e.clientX - rect.left - transform.value.x) / scale
      draggedNode.value.y = (e.clientY - rect.top - transform.value.y) / scale
      nodeDragMoved.value = true
      // 直接更新节点元素位置
      const el = nodeElements.get(draggedNode.value.id)
      if (el) {
        el.circle.setAttribute('cx', draggedNode.value.x)
        el.circle.setAttribute('cy', draggedNode.value.y)
        el.text.setAttribute('x', draggedNode.value.x)
        el.text.setAttribute('y', draggedNode.value.y)
      }
      // 只更新缓存的相关连线
      const nodeMap = new Map()
      nodes.value.forEach(n => nodeMap.set(n.id, n))
      dragCache.value.links.forEach(path => {
        const srcId = parseInt(path.getAttribute('data-source'))
        const tgtId = parseInt(path.getAttribute('data-target'))
        const src = nodeMap.get(srcId)
        const tgt = nodeMap.get(tgtId)
        if (src && tgt) {
          const dx = tgt.x - src.x
          const dy = tgt.y - src.y
          const tx = src.x + dx * 0.3
          const ty = src.y + dy * 0.3
          const tx2 = src.x + dx * 0.7
          const ty2 = src.y + dy * 0.7
          path.setAttribute('d', `M ${src.x},${src.y} C ${tx},${ty} ${tx2},${ty2} ${tgt.x},${tgt.y}`)
        }
      })
    }

    // 单个节点拖拽：mouseup 处理
    const handleNodeDragEnd = () => {
      if (draggedNode.value) {
        document.body.classList.remove('node-dragging')
        // 恢复元素的 transition 内联样式
        const el = nodeElements.get(draggedNode.value.id)
        if (el) {
          el.group.style.transition = ''
          el.circle.style.transition = ''
          el.text.style.transition = ''
        }
        dragCache.value.links.forEach(p => { p.style.transition = '' })
        if (nodeDragMoved.value) {
          // 拖拽过，延迟阻止 click 触发详情面板
          setTimeout(() => { nodeDragMoved.value = false }, 150)
        }
        draggedNode.value = null
      }
    }

    // 构建导览顺序：根节点 → 每个分类(先分类节点后子节点)
    const buildTourSequence = () => {
      const root = nodes.value.find(n => n.level === 1)
      const categories = nodes.value.filter(n => n.level === 2)
      const sequence = []
      if (root) sequence.push(root.id)
      categories.forEach(cat => {
        sequence.push(cat.id)
        const children = links.value
          .filter(l => l.source === cat.id)
          .map(l => l.target)
        sequence.push(...children)
      })
      return sequence
    }

    // 高亮指定节点，其余变暗
    const highlightNode = (nodeId) => {
      highlightedNodeId.value = nodeId
      nodeElements.forEach((el, id) => {
        el.group.removeAttribute('transform')
        if (id === nodeId) {
          el.circle.setAttribute('r', el.baseRadius * 1.5)
          el.circle.setAttribute('stroke', '#f1c40f')
          el.circle.setAttribute('stroke-width', '4px')
          el.circle.setAttribute('opacity', '1')
          el.text.setAttribute('opacity', '1')
          el.text.setAttribute('font-size', (parseInt(el.fontSize) + 2) + 'px')
          el.text.setAttribute('fill', '#f1c40f')
        } else {
          el.circle.setAttribute('r', el.baseRadius)
          el.circle.setAttribute('stroke', 'white')
          el.circle.setAttribute('stroke-width', '2px')
          el.circle.setAttribute('opacity', '0.35')
          el.text.setAttribute('opacity', '0.35')
          el.text.setAttribute('font-size', el.fontSize)
          el.text.setAttribute('fill', 'white')
        }
      })
    }

    // 恢复所有节点正常显示
    const resetHighlight = () => {
      highlightedNodeId.value = null
      nodeElements.forEach((el) => {
        el.group.removeAttribute('transform')
        el.circle.setAttribute('r', el.baseRadius)
        el.circle.setAttribute('stroke', 'white')
        el.circle.setAttribute('stroke-width', '2px')
        el.circle.setAttribute('opacity', '1')
        el.text.setAttribute('opacity', '1')
        el.text.setAttribute('font-size', el.fontSize)
        el.text.setAttribute('fill', 'white')
      })
    }

    // 切换导览动画
    const toggleAnimation = () => {
      if (isAnimating.value) {
        // 停止
        isAnimating.value = false
        if (animationTimer) {
          clearTimeout(animationTimer)
          animationTimer = null
        }
        resetHighlight()
        showAlert('导览已暂停', 'info')
        return
      }

      // 开始
      const sequence = buildTourSequence()
      if (sequence.length === 0) {
        showAlert('暂无数据可导览', 'warning')
        return
      }

      isAnimating.value = true
      let index = 0

      const step = () => {
        if (!isAnimating.value || index >= sequence.length) {
          isAnimating.value = false
          animationTimer = null
          resetHighlight()
          showAlert('导览结束', 'info')
          return
        }
        highlightNode(sequence[index])
        const node = nodes.value.find(n => n.id === sequence[index])
        // 根节点和分类节点停留久一点
        const delay = (node && node.level <= 2) ? 1600 : 1100
        index++
        animationTimer = setTimeout(step, delay)
      }
      step()
    }

    // 窗口大小变化时重新渲染
    const handleResize = () => {
      if (nodes.value.length > 0) {
        renderGraph()
      }
    }

    // 组件挂载
    onMounted(() => {
      loadGraphData()
      window.addEventListener('resize', handleResize)
      document.addEventListener('mousemove', handleNodeDragMove)
      document.addEventListener('mouseup', handleNodeDragEnd)
    })

    // 组件卸载
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      document.removeEventListener('mousemove', handleNodeDragMove)
      document.removeEventListener('mouseup', handleNodeDragEnd)
      if (animationTimer) {
        clearTimeout(animationTimer)
        animationTimer = null
      }
    })

    return {
      graphCanvas,
      graphSvg,
      nodes,
      links,
      isLoading,
      hasError,
      isAnimating,
      loadGraphData,
      resetGraph,
      zoomIn,
      zoomOut,
      handleWheel,
      startDrag,
      handleDrag,
      endDrag,
      toggleAnimation,
      goBack,
      selectedNode,
      showNodeDetail,
      openNodeDetail,
      closeNodeDetail,
      centerPos,
      nodeTypeLabel
    }
  }
}
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

/* 知识图谱容器样式补充 */
.knowledge-graph-container {
  padding-top: 20px;
  padding-bottom: 50px;
  background-color: white;
  min-height: 100vh;
}

/* 加载状态和错误状态样式补充 */
.graph-loading,
.graph-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 图谱头部样式补充 */
.graph-header {
  margin-bottom: 30px;
  text-align: center;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* 控制按钮样式补充 */
.graph-controls {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* 图谱画布样式 */
.graph-canvas {
    width: 1400px;
    height: 900px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    background-color: #f8f9fa;
    position: relative;
  }
  
  /* 知识图谱包装器样式 */
  .knowledge-graph-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 1600px;
    margin: 0 auto;
    padding: 20px;
  }

/* 响应式调整 */
@media (max-width: 1450px) {
  .graph-canvas {
    width: 95%;
  }
  
  .knowledge-graph-wrapper {
    padding: 10px;
  }
}

@media (max-width: 768px) {
  .graph-canvas {
    height: 700px !important;
  }
  
  .graph-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .graph-controls .btn {
    width: 200px;
    margin: 5px 0;
  }
}

/* 节点详情面板 */
.detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  z-index: 999;
}

.node-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  max-width: 90vw;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.detail-header {
  padding: 1.5rem 1.5rem 1.2rem;
  border-left: 5px solid #95a5a6;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  flex-shrink: 0;
}

.detail-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}

.detail-category-badge {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 12px;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
}

.detail-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  line-height: 1;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.detail-close:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #333;
}

.detail-name {
  margin: 0 0 0.3rem 0;
  font-size: 1.5rem;
  color: #1a1a2e;
}

.detail-type {
  margin: 0;
  font-size: 0.85rem;
  color: #6c757d;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.detail-description h4 {
  margin: 0 0 0.6rem 0;
  font-size: 0.95rem;
  color: #495057;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.4rem;
}

.detail-description p {
  margin: 0;
  line-height: 1.8;
  color: #333;
  font-size: 0.95rem;
}

.detail-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #adb5bd;
}

.detail-empty i {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
  display: block;
}

.detail-empty p {
  margin: 0;
  font-size: 0.9rem;
}
</style>
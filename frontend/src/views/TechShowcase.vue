<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <router-link to="/" class="text-gray-400 hover:text-gray-600 transition">← 返回首页</router-link>
          <span class="text-gray-300">|</span>
          <h1 class="text-lg font-bold text-gray-900">技术架构与创新亮点</h1>
        </div>
        <span class="text-xs text-gray-400 font-mono">v0.3.0 · FastAPI + Vue3 + Edge AI</span>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-12 space-y-16">

      <!-- 系统全景架构 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">系统全景架构</h2>
        <p class="text-gray-500 mb-8">四层架构 · 边云协同 · 隐私原生</p>
        <div class="bg-white rounded-2xl shadow-sm p-8 space-y-6">
          <!-- 层级 -->
          <div v-for="layer in archLayers" :key="layer.name" class="flex items-start gap-4">
            <div class="w-32 shrink-0 text-right">
              <span class="inline-block px-3 py-1 rounded-lg text-xs font-bold" :class="layer.badge">{{ layer.name }}</span>
            </div>
            <div class="flex-1">
              <div class="flex flex-wrap gap-2">
                <div v-for="mod in layer.modules" :key="mod.name"
                  class="px-3 py-2 rounded-lg text-sm border" :class="layer.modClass">
                  <span class="font-semibold">{{ mod.name }}</span>
                  <span class="text-xs opacity-70 ml-1">{{ mod.tech }}</span>
                </div>
              </div>
            </div>
          </div>
          <!-- 数据流箭头 -->
          <div class="flex items-center justify-center gap-2 text-gray-400 text-xs py-2">
            <span>边缘设备</span>
            <span>→ 匿名骨骼坐标 →</span>
            <span>AI分析层</span>
            <span>→ 风险特征 →</span>
            <span>精算引擎</span>
            <span>→ 预警/定价 →</span>
            <span>四方终端</span>
          </div>
        </div>
      </section>

      <!-- 创新一：隐私优先的边缘计算 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">创新一：隐私优先的边缘视觉AI</h2>
        <p class="text-gray-500 mb-8">原始视频永远不离开本地设备，云端只处理匿名坐标</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h3 class="font-bold text-gray-900 mb-4">数据流对比</h3>
            <div class="space-y-4">
              <div class="p-4 bg-red-50 rounded-xl border border-red-100">
                <p class="text-sm font-bold text-red-700 mb-2">❌ 传统方案</p>
                <div class="flex items-center gap-2 text-xs text-red-600">
                  <span class="px-2 py-1 bg-white rounded">摄像头</span>→
                  <span class="px-2 py-1 bg-white rounded font-bold">完整视频上云</span>→
                  <span class="px-2 py-1 bg-white rounded">云端AI分析</span>
                </div>
                <p class="text-xs text-red-500 mt-2">隐私风险：视频泄露=生物信息泄露，违反PIPL</p>
              </div>
              <div class="p-4 bg-green-50 rounded-xl border border-green-100">
                <p class="text-sm font-bold text-green-700 mb-2">✅ 银龄精算师</p>
                <div class="flex items-center gap-2 text-xs text-green-600">
                  <span class="px-2 py-1 bg-white rounded">摄像头</span>→
                  <span class="px-2 py-1 bg-white rounded font-bold">边缘姿态提取</span>→
                  <span class="px-2 py-1 bg-white rounded">17个匿名坐标</span>→
                  <span class="px-2 py-1 bg-white rounded">云端分析</span>
                </div>
                <p class="text-xs text-green-500 mt-2">95%数据在边缘处理，云端仅收到无法逆向还原的坐标序列</p>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h3 class="font-bold text-gray-900 mb-4">边缘处理管线</h3>
            <div class="space-y-3">
              <div v-for="(step, i) in edgePipeline" :key="i" class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-sm font-bold text-indigo-600">{{ i + 1 }}</div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-800">{{ step.name }}</p>
                  <p class="text-xs text-gray-500">{{ step.desc }}</p>
                </div>
                <span class="text-xs font-mono text-gray-400">{{ step.latency }}</span>
              </div>
            </div>
            <div class="mt-4 p-3 bg-indigo-50 rounded-lg text-xs text-indigo-700">
              端到端延迟 &lt; 200ms · 支持离线运行 · 符合 PIPL / GDPR
            </div>
          </div>
        </div>
      </section>

      <!-- 创新二：多模态视觉AI管线 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">创新二：多模态视觉AI分析管线</h2>
        <p class="text-gray-500 mb-8">三层级服务架构，从姿态估计到行为识别</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-2xl shadow-sm p-6 border-t-4 border-blue-500">
            <h3 class="font-bold text-blue-900 mb-3">PoseEstimationService</h3>
            <p class="text-sm text-gray-600 mb-4">17个关键点实时姿态估计</p>
            <div class="space-y-2 text-xs text-gray-700">
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>鼻-眼-耳-肩-肘-腕-髋-膝-踝</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>OpenPose / MediaPipe 兼容</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>30 FPS 实时推理</div>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6 border-t-4 border-rose-500">
            <h3 class="font-bold text-rose-900 mb-3">FallDetectionService</h3>
            <p class="text-sm text-gray-600 mb-4">4特征融合跌倒检测算法</p>
            <div class="space-y-2 text-xs text-gray-700">
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>重心高度骤降检测 (Δy &gt; 阈值)</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>躯干角度偏转 (&gt;60°)</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>速度突变检测</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>持续不动判定 (&gt;10s)</div>
            </div>
            <p class="text-xs text-gray-500 mt-3">4/4特征命中 → 确认跌倒 · 2/4 → 疑似</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6 border-t-4 border-green-500">
            <h3 class="font-bold text-green-900 mb-3">ActivityRecognitionService</h3>
            <p class="text-sm text-gray-600 mb-4">5类日常活动分类</p>
            <div class="space-y-2 text-xs text-gray-700">
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>行走 · 站立 · 坐姿</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>躺卧 · 运动/锻炼</div>
              <div class="flex items-center gap-2"><span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>时序活动模式异常检测</div>
            </div>
            <p class="text-xs text-gray-500 mt-3">日常模式偏差 → 早期衰弱信号</p>
          </div>
        </div>
      </section>

      <!-- 创新三：精算模型引擎 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">创新三：学术级精算模型引擎</h2>
        <p class="text-gray-500 mb-8">首次将保险精算方法融入居家养老风控</p>
        <div class="bg-white rounded-2xl shadow-sm p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-4">
              <div class="p-4 bg-indigo-50 rounded-xl">
                <h4 class="font-bold text-indigo-800 mb-2">Gompertz 死亡力模型</h4>
                <p class="font-mono text-sm text-indigo-900">h(t) = α · e<sup>β·t</sup></p>
                <p class="font-mono text-sm text-indigo-900 mt-1">S(t) = exp[-(α/β)(e<sup>β·t</sup> - 1)]</p>
                <p class="text-xs text-indigo-600 mt-2">参数通过极大似然估计(MLE)拟合，描述风险随年龄的指数增长</p>
              </div>
              <div class="p-4 bg-emerald-50 rounded-xl">
                <h4 class="font-bold text-emerald-800 mb-2">Cox 比例风险回归</h4>
                <p class="font-mono text-sm text-emerald-900">h(t|X) = h₀(t) · exp(β₁X₁ + ... + β₈X₈)</p>
                <p class="text-xs text-emerald-600 mt-2">8个协变量：年龄/步态/跌倒史/睡眠/用药/活动量/认知/环境</p>
              </div>
              <div class="p-4 bg-rose-50 rounded-xl">
                <h4 class="font-bold text-rose-800 mb-2">Kaplan-Meier 生存估计</h4>
                <p class="font-mono text-sm text-rose-900">Ŝ(t) = Π<sub>tᵢ≤t</sub>(1 - dᵢ/nᵢ)</p>
                <p class="text-xs text-rose-600 mt-2">非参数法 + Greenwood方差估计 + RMST受限平均生存时间</p>
              </div>
            </div>
            <div class="space-y-4">
              <div class="p-4 bg-amber-50 rounded-xl">
                <h4 class="font-bold text-amber-800 mb-2">PremiumPricingEngine 保费定价</h4>
                <p class="text-xs text-amber-700 mb-3">基于精算三支柱的科学定价流程</p>
                <div class="space-y-2 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 bg-amber-200 rounded flex items-center justify-center font-bold text-amber-800">1</span>
                    <span class="text-gray-700">Gompertz 计算基准风险率</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 bg-amber-200 rounded flex items-center justify-center font-bold text-amber-800">2</span>
                    <span class="text-gray-700">Cox PH 生成个性化风险比 (HR)</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 bg-amber-200 rounded flex items-center justify-center font-bold text-amber-800">3</span>
                    <span class="text-gray-700">纯保费 = 风险率 × 赔付金额</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 bg-amber-200 rounded flex items-center justify-center font-bold text-amber-800">4</span>
                    <span class="text-gray-700">毛保费 = 纯保费 / (1 - 费用率)</span>
                  </div>
                </div>
              </div>
              <div class="p-4 bg-gray-100 rounded-xl">
                <h4 class="font-bold text-gray-800 mb-2">风控闭环</h4>
                <div class="flex flex-wrap gap-2 text-xs">
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">📹 检测</span>
                  <span class="text-gray-400">→</span>
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">🔍 验证</span>
                  <span class="text-gray-400">→</span>
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">🚨 预警</span>
                  <span class="text-gray-400">→</span>
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">📋 调度</span>
                  <span class="text-gray-400">→</span>
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">💊 干预</span>
                  <span class="text-gray-400">→</span>
                  <span class="px-2 py-1 bg-white rounded-lg shadow-sm">📊 反馈</span>
                  <span class="text-gray-400">→</span>
                  <span class="text-xs text-gray-500 italic">循环优化</span>
                </div>
                <p class="text-xs text-gray-600 mt-3">干预结果反馈至模型，持续校准精算参数，准确率逐周提升</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 技术栈一览 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">技术栈一览</h2>
        <p class="text-gray-500 mb-8">现代化全栈技术选型</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="stack in techStacks" :key="stack.category" class="bg-white rounded-xl p-4 shadow-sm">
            <h3 class="text-xs font-bold text-gray-500 mb-3 uppercase">{{ stack.category }}</h3>
            <div class="space-y-2">
              <div v-for="tech in stack.items" :key="tech" class="text-sm text-gray-800 font-medium">{{ tech }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- API 规模 -->
      <section class="bg-indigo-900 text-white -mx-6 px-6 py-16 rounded-2xl">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold mb-2">系统规模</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-6 text-center">
          <div><p class="text-3xl font-extrabold">40+</p><p class="text-sm text-indigo-300">API 端点</p></div>
          <div><p class="text-3xl font-extrabold">10</p><p class="text-sm text-indigo-300">路由模块</p></div>
          <div><p class="text-3xl font-extrabold">7</p><p class="text-sm text-indigo-300">前端API服务</p></div>
          <div><p class="text-3xl font-extrabold">4</p><p class="text-sm text-indigo-300">角色终端</p></div>
          <div><p class="text-3xl font-extrabold">3</p><p class="text-sm text-indigo-300">精算模型</p></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const archLayers = ref([
  {
    name: '感知层',
    badge: 'bg-blue-100 text-blue-700',
    modClass: 'bg-blue-50 border-blue-200 text-blue-800',
    modules: [
      { name: '边缘摄像头', tech: 'ARM/NVIDIA Jetson' },
      { name: '姿态提取', tech: 'PoseEstimation' },
      { name: '本地推理', tech: 'TFLite/ONNX' }
    ]
  },
  {
    name: 'AI分析层',
    badge: 'bg-rose-100 text-rose-700',
    modClass: 'bg-rose-50 border-rose-200 text-rose-800',
    modules: [
      { name: '跌倒检测', tech: '4特征融合' },
      { name: '活动识别', tech: '5类分类' },
      { name: '异常检测', tech: '时序模式' },
      { name: '多模态验证', tech: '交叉确认' }
    ]
  },
  {
    name: '精算层',
    badge: 'bg-emerald-100 text-emerald-700',
    modClass: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    modules: [
      { name: 'Gompertz', tech: '死亡力模型' },
      { name: 'Cox PH', tech: '比例风险' },
      { name: 'Kaplan-Meier', tech: '生存分析' },
      { name: 'PremiumEngine', tech: '保费定价' }
    ]
  },
  {
    name: '应用层',
    badge: 'bg-purple-100 text-purple-700',
    modClass: 'bg-purple-50 border-purple-200 text-purple-800',
    modules: [
      { name: '子女端', tech: '远程守护' },
      { name: '医生端', tech: '辅助诊断' },
      { name: '机构端', tech: '风控管理' },
      { name: '保险端', tech: '精算定价' }
    ]
  }
])

const edgePipeline = ref([
  { name: '视频采集', desc: '本地摄像头30FPS采集，不压缩不上传', latency: '0ms' },
  { name: '姿态估计', desc: '边缘端提取17个人体关键点坐标', latency: '~33ms' },
  { name: '视频丢弃', desc: '原始帧立即销毁，仅保留匿名坐标', latency: '~0ms' },
  { name: '特征计算', desc: '计算重心、躯干角度、速度、不动时长', latency: '~5ms' },
  { name: '本地判定', desc: '4特征融合跌倒初筛，紧急事件本地报警', latency: '~2ms' },
  { name: '坐标上传', desc: '仅上传匿名骨骼坐标序列至云端', latency: '~50ms' }
])

const techStacks = ref([
  { category: '后端', items: ['FastAPI 0.104', 'Python 3.11', 'Pydantic v2', 'Uvicorn'] },
  { category: '前端', items: ['Vue 3.4', 'Vite 5', 'TailwindCSS', 'Pinia'] },
  { category: 'AI/ML', items: ['OpenPose/MediaPipe', 'NumPy/SciPy', 'Lifelines', 'ONNX Runtime'] },
  { category: '基础设施', items: ['Docker', 'NVIDIA Jetson', 'WebSocket', 'RESTful API'] }
])
</script>

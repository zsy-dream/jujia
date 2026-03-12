<template>
  <div v-if="isActive" class="fixed inset-0 z-50 bg-gray-900/95 backdrop-blur-sm">
    <!-- 演示控制栏 -->
    <div class="absolute top-0 left-0 right-0 bg-gray-800/90 text-white px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
          <span class="font-medium">演示模式</span>
        </div>
        <div class="h-6 w-px bg-gray-600"></div>
        <span class="text-sm text-gray-300">{{ currentScene?.name || '准备中' }}</span>
      </div>
      
      <div class="flex items-center gap-4">
        <!-- 章节导航 -->
        <div class="flex items-center gap-2">
          <button 
            v-for="(scene, index) in scenes" 
            :key="scene.id"
            @click="jumpToScene(index)"
            class="w-8 h-8 rounded-full text-sm font-medium transition-all"
            :class="currentSceneIndex === index ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-400 hover:bg-gray-600'"
          >
            {{ index + 1 }}
          </button>
        </div>
        
        <div class="h-6 w-px bg-gray-600"></div>
        
        <!-- 控制按钮 -->
        <button 
          @click="togglePause"
          class="p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <svg v-if="isPaused" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
        
        <button 
          @click="exitDemo"
          class="p-2 rounded-lg hover:bg-red-600/20 text-red-400 hover:text-red-300 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 演示内容区 -->
    <div class="absolute top-16 left-0 right-0 bottom-0 overflow-auto p-8">
      <div class="max-w-6xl mx-auto">
        <!-- 场景标题 -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center gap-3 px-6 py-3 bg-blue-500/20 rounded-full mb-4">
            <span class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
              {{ currentSceneIndex + 1 }}
            </span>
            <span class="text-blue-400 font-medium">{{ currentScene?.subtitle }}</span>
          </div>
          <h2 class="text-3xl font-bold text-white mb-2">{{ currentScene?.title }}</h2>
          <p class="text-gray-400 text-lg">{{ currentScene?.description }}</p>
        </div>

        <!-- 场景内容 -->
        <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <!-- 场景1: 系统概览 -->
          <div v-if="currentScene?.id === 'overview'" class="p-8">
            <div class="grid grid-cols-2 gap-8">
              <div class="space-y-6">
                <div class="flex items-start gap-4">
                  <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">银龄精算师是什么？</h3>
                    <p class="text-gray-600">国内首个基于多模态视觉AI与精算模型的居家养老风控闭环系统。我们不是简单的"监控摄像头"，而是能够预测风险、主动干预、闭环学习的智能养老解决方案。</p>
                  </div>
                </div>
                
                <div class="flex items-start gap-4">
                  <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">核心创新点</h3>
                    <ul class="space-y-2 text-gray-600">
                      <li class="flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        精算AI融合模型：预测7/30天风险概率，可定价
                      </li>
                      <li class="flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        边缘隐私计算：原始视频永不离开本地
                      </li>
                      <li class="flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        风控闭环：从监测到干预到学习的完整链条
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div class="bg-gray-50 rounded-xl p-6">
                <h4 class="font-semibold text-gray-800 mb-4">系统架构概览</h4>
                <div class="space-y-3">
                  <div class="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">1</div>
                    <span class="text-sm text-gray-700">多模态数据采集（视觉+可穿戴+环境）</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">2</div>
                    <span class="text-sm text-gray-700">边缘AI处理（YOLOv8+OpenPose本地推理）</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">3</div>
                    <span class="text-sm text-gray-700">精算风险评估（Gompertz模型+动态学习）</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">4</div>
                    <span class="text-sm text-gray-700">智能干预执行（灯光+语音+通知）</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">5</div>
                    <span class="text-sm text-gray-700">闭环反馈优化（事件记录+模型校准）</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 场景2: 实时监测展示 -->
          <div v-if="currentScene?.id === 'monitoring'" class="p-8">
            <div class="grid grid-cols-3 gap-6">
              <div class="col-span-2 space-y-4">
                <div class="bg-gray-900 rounded-xl p-4 aspect-video flex items-center justify-center relative overflow-hidden">
                  <div class="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900"></div>
                  <div class="relative z-10 text-center">
                    <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <p class="text-white font-medium">实时视频流（模拟）</p>
                    <p class="text-gray-400 text-sm">边缘设备处理中，仅上传行为标签</p>
                  </div>
                  <!-- 骨架叠加层示意 -->
                  <div class="absolute inset-0 opacity-30">
                    <svg class="w-full h-full" viewBox="0 0 400 300">
                      <circle cx="200" cy="80" r="20" fill="none" stroke="#10B981" stroke-width="2"/>
                      <line x1="200" y1="100" x2="200" y2="180" stroke="#10B981" stroke-width="2"/>
                      <line x1="200" y1="120" x2="150" y2="160" stroke="#10B981" stroke-width="2"/>
                      <line x1="200" y1="120" x2="250" y2="160" stroke="#10B981" stroke-width="2"/>
                      <line x1="200" y1="180" x2="170" y2="240" stroke="#10B981" stroke-width="2"/>
                      <line x1="200" y1="180" x2="230" y2="240" stroke="#10B981" stroke-width="2"/>
                    </svg>
                  </div>
                </div>
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-blue-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-blue-600">5,420</p>
                    <p class="text-sm text-gray-600">今日步数</p>
                  </div>
                  <div class="bg-purple-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-purple-600">6.8h</p>
                    <p class="text-sm text-gray-600">昨夜睡眠</p>
                  </div>
                  <div class="bg-green-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-green-600">128/82</p>
                    <p class="text-sm text-gray-600">当前血压</p>
                  </div>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="bg-gray-50 rounded-xl p-4">
                  <h4 class="font-semibold text-gray-800 mb-3">设备状态</h4>
                  <div class="space-y-2">
                    <div class="flex items-center justify-between p-2 bg-white rounded-lg">
                      <span class="text-sm text-gray-600">智能手环</span>
                      <span class="flex items-center gap-1 text-xs text-green-600">
                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                        在线
                      </span>
                    </div>
                    <div class="flex items-center justify-between p-2 bg-white rounded-lg">
                      <span class="text-sm text-gray-600">智能床垫</span>
                      <span class="flex items-center gap-1 text-xs text-green-600">
                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                        在线
                      </span>
                    </div>
                    <div class="flex items-center justify-between p-2 bg-white rounded-lg">
                      <span class="text-sm text-gray-600">跌倒检测摄像头</span>
                      <span class="flex items-center gap-1 text-xs text-green-600">
                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                        在线
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="bg-amber-50 rounded-xl p-4 border border-amber-200">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="font-medium text-amber-800">智能提醒</span>
                  </div>
                  <p class="text-sm text-amber-700">已连续静坐2小时，建议起身活动</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 场景3: 精算风险评估 -->
          <div v-if="currentScene?.id === 'actuarial'" class="p-8">
            <div class="grid grid-cols-2 gap-8">
              <div>
                <div class="bg-indigo-50 rounded-xl p-6 mb-6">
                  <h3 class="text-lg font-semibold text-indigo-900 mb-4">当前风险评估</h3>
                  <div class="grid grid-cols-3 gap-4">
                    <div class="text-center">
                      <div class="w-20 h-20 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-2">
                        <span class="text-2xl font-bold text-amber-600">28%</span>
                      </div>
                      <p class="text-sm text-gray-600">跌倒风险</p>
                      <p class="text-xs text-amber-600">中高风险</p>
                    </div>
                    <div class="text-center">
                      <div class="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-2">
                        <span class="text-2xl font-bold text-blue-600">18%</span>
                      </div>
                      <p class="text-sm text-gray-600">住院风险</p>
                      <p class="text-xs text-gray-500">未来30天</p>
                    </div>
                    <div class="text-center">
                      <div class="w-20 h-20 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-2">
                        <span class="text-2xl font-bold text-purple-600">0.42</span>
                      </div>
                      <p class="text-sm text-gray-600">衰弱指数</p>
                      <p class="text-xs text-gray-500">中度衰弱</p>
                    </div>
                  </div>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-xl p-4">
                  <h4 class="font-semibold text-gray-800 mb-3">精算公式</h4>
                  <div class="font-mono text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                    <p>P(跌倒) = Σ(wᵢ × xᵢ) × F(年龄, 性别, 病史)</p>
                    <p class="mt-2 text-xs text-gray-500">基于Gompertz生存模型，引入动态时变参数</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 class="font-semibold text-gray-800 mb-4">风险因子分解</h4>
                <div class="space-y-3">
                  <div>
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm text-gray-600">步态稳定性</span>
                      <span class="text-sm font-medium text-gray-800">35%</span>
                    </div>
                    <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-indigo-500 rounded-full" style="width: 35%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm text-gray-600">夜间活动量</span>
                      <span class="text-sm font-medium text-gray-800">25%</span>
                    </div>
                    <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-blue-500 rounded-full" style="width: 25%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm text-gray-600">睡眠质量</span>
                      <span class="text-sm font-medium text-gray-800">20%</span>
                    </div>
                    <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-purple-500 rounded-full" style="width: 20%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm text-gray-600">环境因素</span>
                      <span class="text-sm font-medium text-gray-800">12%</span>
                    </div>
                    <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-amber-500 rounded-full" style="width: 12%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm text-gray-600">历史跌倒记录</span>
                      <span class="text-sm font-medium text-gray-800">8%</span>
                    </div>
                    <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-rose-500 rounded-full" style="width: 8%"></div>
                    </div>
                  </div>
                </div>
                
                <div class="mt-6 p-4 bg-green-50 rounded-xl border border-green-200">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="font-medium text-green-800">模型校准状态</span>
                  </div>
                  <p class="text-sm text-green-700">过去30天预测准确率 87%，模型持续学习优化中</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 场景4: 智能干预闭环 -->
          <div v-if="currentScene?.id === 'intervention'" class="p-8">
            <div class="mb-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-2">干预执行链演示：夜间防跌倒</h3>
              <p class="text-gray-600">当系统检测到夜间离床+步态不稳时，自动启动防护干预链</p>
            </div>
            
            <div class="relative">
              <!-- 连接线 -->
              <div class="absolute left-6 top-8 bottom-8 w-0.5 bg-gray-200"></div>
              
              <div class="space-y-4">
                <div 
                  v-for="(step, index) in interventionSteps" 
                  :key="step.id"
                  class="flex items-start gap-4 relative"
                >
                  <div 
                    class="w-12 h-12 rounded-full flex items-center justify-center z-10 flex-shrink-0 transition-all"
                    :class="currentInterventionStep >= index ? 'bg-green-500' : 'bg-gray-300'"
                  >
                    <svg v-if="currentInterventionStep > index" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else-if="currentInterventionStep === index" class="w-6 h-6 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span v-else class="text-white font-medium">{{ index + 1 }}</span>
                  </div>
                  
                  <div class="flex-1 p-4 rounded-xl transition-all"
                    :class="currentInterventionStep >= index ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'"
                  >
                    <div class="flex items-center justify-between">
                      <h4 class="font-medium" :class="currentInterventionStep >= index ? 'text-green-800' : 'text-gray-600'">{{ step.name }}</h4>
                      <span v-if="currentInterventionStep > index" class="text-xs text-green-600">已完成</span>
                      <span v-else-if="currentInterventionStep === index" class="text-xs text-green-600 animate-pulse">执行中...</span>
                    </div>
                    <p class="text-sm mt-1" :class="currentInterventionStep >= index ? 'text-green-700' : 'text-gray-500'">{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium text-blue-800">干预效果</h4>
                  <p class="text-sm text-blue-600">通过智能灯光引导和语音提醒，成功降低跌倒风险 46%</p>
                </div>
                <div class="text-right">
                  <p class="text-2xl font-bold text-blue-600">8秒</p>
                  <p class="text-xs text-blue-500">系统响应时间</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 场景5: 多角色协同 -->
          <div v-if="currentScene?.id === 'collaboration'" class="p-8">
            <div class="grid grid-cols-4 gap-4">
              <div 
                v-for="role in roles" 
                :key="role.id"
                class="p-4 rounded-xl border-2 transition-all"
                :class="activeRole === role.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'"
                @click="activeRole = role.id"
              >
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-3"
                  :class="role.iconBg"
                >
                  <svg class="w-6 h-6" :class="role.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="role.id === 'elder'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    <path v-else-if="role.id === 'family'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    <path v-else-if="role.id === 'doctor'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m8-10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h4 class="font-semibold text-gray-800">{{ role.name }}</h4>
                <p class="text-sm text-gray-500 mt-1">{{ role.subtitle }}</p>
              </div>
            </div>
            
            <div class="mt-6 p-6 bg-gray-50 rounded-xl">
              <div v-if="activeRole === 'elder'">
                <h4 class="font-semibold text-gray-800 mb-3">老人端特色</h4>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    零操作界面：无需学习，系统自动感知
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    AI语音交互：自然语言查询健康数据
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    环境智能：灯光、窗帘自动响应
                  </li>
                </ul>
              </div>
              <div v-else-if="activeRole === 'family'">
                <h4 class="font-semibold text-gray-800 mb-3">子女端特色</h4>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    情感化设计："关爱妈妈"而非"监控系统"
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    实时守护：移动端随时查看老人状态
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    一键视频：快速与老人视频通话
                  </li>
                </ul>
              </div>
              <div v-else-if="activeRole === 'doctor'">
                <h4 class="font-semibold text-gray-800 mb-3">医生端特色</h4>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    精算风险摘要：一目了然的风险评估
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    快速批注：模板化医学建议
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    患者排序：按风险优先级管理签约患者
                  </li>
                </ul>
              </div>
              <div v-else>
                <h4 class="font-semibold text-gray-800 mb-3">机构端特色</h4>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    风险热力图：整栋楼住户风险可视化
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    护理任务联动：自动生成并派发护理任务
                  </li>
                  <li class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    精算定价支持：为保险产品提供精算数据
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 进度指示器 -->
        <div class="mt-8 flex items-center justify-center gap-4">
          <span class="text-gray-400 text-sm">{{ currentSceneIndex + 1 }} / {{ scenes.length }}</span>
          <div class="flex gap-2">
            <div 
              v-for="(scene, index) in scenes" 
              :key="scene.id"
              class="w-12 h-1 rounded-full transition-all"
              :class="index <= currentSceneIndex ? 'bg-blue-500' : 'bg-gray-600'"
            ></div>
          </div>
        </div>

        <!-- 导航提示 -->
        <div class="mt-4 text-center text-gray-400 text-sm">
          按 <kbd class="px-2 py-1 bg-gray-700 rounded">←</kbd> <kbd class="px-2 py-1 bg-gray-700 rounded">→</kbd> 键切换场景，<kbd class="px-2 py-1 bg-gray-700 rounded">ESC</kbd> 退出演示
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  autoPlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const isActive = ref(false)
const isPaused = ref(false)
const currentSceneIndex = ref(0)
const activeRole = ref('elder')
const currentInterventionStep = ref(-1)

const scenes = [
  {
    id: 'overview',
    name: '系统概览',
    subtitle: '场景一',
    title: '银龄精算师：智能养老风控专家',
    description: '国内首个将保险精算模型与多模态视觉AI深度融合的居家养老解决方案'
  },
  {
    id: 'monitoring',
    name: '实时监测',
    subtitle: '场景二',
    title: '多模态数据采集与边缘计算',
    description: '智能手环+床垫+摄像头+环境传感器，全方位守护老人安全'
  },
  {
    id: 'actuarial',
    name: '精算评估',
    subtitle: '场景三',
    title: '基于精算模型的动态风险评估',
    description: '不是简单的阈值报警，而是可定价的风险概率预测'
  },
  {
    id: 'intervention',
    name: '智能干预',
    subtitle: '场景四',
    title: '风控闭环：从预警到干预',
    description: '监测→评估→预警→干预→响应→学习的完整链条'
  },
  {
    id: 'collaboration',
    name: '多角色协同',
    subtitle: '场景五',
    title: '老人·家属·医生·机构四位一体',
    description: '每个角色都有专属界面，形成完整的照护网络'
  }
]

const currentScene = computed(() => scenes[currentSceneIndex.value])

const interventionSteps = [
  { id: 'detect', name: '风险检测', description: '床垫传感器检测到离床+摄像头检测步态不稳' },
  { id: 'assess', name: '精算评估', description: '实时计算跌倒风险概率：从12%升至28%' },
  { id: 'light', name: '智能灯光', description: '自动开启柔光夜灯，引导至卫生间' },
  { id: 'voice', name: '语音提醒', description: '播放语音："张奶奶，请小心慢行"' },
  { id: 'notify', name: '家属通知', description: '向儿子李明发送通知：检测到夜间活动' },
  { id: 'care', name: '护理响应', description: '社区护理人员收到预警，准备上门' },
  { id: 'feedback', name: '闭环反馈', description: '记录事件，模型学习优化预测参数' }
]

const roles = [
  { id: 'elder', name: '老人端', subtitle: '零操作智能界面', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  { id: 'family', name: '子女端', subtitle: '情感化移动应用', iconBg: 'bg-green-100', iconColor: 'text-green-600' },
  { id: 'doctor', name: '医生端', subtitle: '专业评估工作台', iconBg: 'bg-purple-100', iconColor: 'text-purple-600' },
  { id: 'institution', name: '机构端', subtitle: 'B2B管理后台', iconBg: 'bg-amber-100', iconColor: 'text-amber-600' }
]

// 干预演示动画
let interventionInterval = null
function startInterventionDemo() {
  currentInterventionStep.value = -1
  interventionInterval = setInterval(() => {
    if (!isPaused.value && currentInterventionStep.value < interventionSteps.length - 1) {
      currentInterventionStep.value++
    } else {
      clearInterval(interventionInterval)
    }
  }, 1500)
}

// 自动播放
let autoPlayInterval = null
function startAutoPlay() {
  if (!props.autoPlay) return
  
  autoPlayInterval = setInterval(() => {
    if (!isPaused.value) {
      nextScene()
    }
  }, 8000)
}

function nextScene() {
  if (currentSceneIndex.value < scenes.length - 1) {
    currentSceneIndex.value++
    if (currentScene.value.id === 'intervention') {
      startInterventionDemo()
    }
  } else {
    // 演示结束，回到开头或退出
    currentSceneIndex.value = 0
  }
}

function prevScene() {
  if (currentSceneIndex.value > 0) {
    currentSceneIndex.value--
  }
}

function jumpToScene(index) {
  currentSceneIndex.value = index
  isPaused.value = true
  if (currentScene.value.id === 'intervention') {
    startInterventionDemo()
  }
}

function togglePause() {
  isPaused.value = !isPaused.value
}

function exitDemo() {
  isActive.value = false
  clearInterval(autoPlayInterval)
  clearInterval(interventionInterval)
  emit('close')
}

function start() {
  isActive.value = true
  currentSceneIndex.value = 0
  isPaused.value = false
  startAutoPlay()
}

// 键盘控制
function handleKeydown(e) {
  if (!isActive.value) return
  
  switch (e.key) {
    case 'ArrowRight':
      nextScene()
      isPaused.value = true
      break
    case 'ArrowLeft':
      prevScene()
      isPaused.value = true
      break
    case 'Escape':
      exitDemo()
      break
    case ' ':
      e.preventDefault()
      togglePause()
      break
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearInterval(autoPlayInterval)
  clearInterval(interventionInterval)
})

// 暴露方法
defineExpose({
  start,
  exitDemo
})
</script>

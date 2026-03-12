<template>
  <div class="min-h-screen bg-white">
    <!-- Hero -->
    <section class="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-blue-900 to-blue-800 text-white">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div class="absolute bottom-20 right-10 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style="animation-delay: 2s"></div>
      </div>
      <nav class="relative z-10 max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center text-xl">🛡️</div>
          <span class="text-lg font-bold">银龄精算师</span>
        </div>
        <div class="flex items-center gap-4">
          <router-link to="/dashboard" class="px-4 py-2 bg-white/20 backdrop-blur rounded-lg text-sm font-medium hover:bg-white/30 transition">进入系统</router-link>
        </div>
      </nav>
      <div class="relative z-10 max-w-7xl mx-auto px-6 py-20 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur rounded-full text-sm mb-8">
          <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          第十二届中国国际大学生创新大赛参赛项目
        </div>
        <h1 class="text-5xl md:text-6xl font-extrabold mb-6 leading-tight">银龄精算师</h1>
        <p class="text-xl md:text-2xl text-blue-200 mb-4 max-w-3xl mx-auto">基于多模态视觉AI与精算模型的居家养老风控闭环系统</p>
        <p class="text-lg text-blue-300 mb-10 max-w-2xl mx-auto">不是"跌倒了再报警"，而是<span class="text-white font-semibold">提前30天预测风险并主动干预</span></p>
        <div class="flex justify-center gap-4">
          <router-link to="/dashboard" class="px-8 py-3 bg-white text-blue-900 rounded-xl font-semibold hover:bg-blue-50 transition shadow-lg shadow-blue-900/30">体验演示</router-link>
        </div>
      </div>
    </section>

    <!-- 社会痛点 -->
    <section class="max-w-7xl mx-auto px-6 py-20">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">2.97亿老年人的安全守护难题</h2>
        <p class="text-gray-600 max-w-2xl mx-auto">中国已进入深度老龄化社会，传统养老模式面临巨大挑战</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="text-center p-6 bg-red-50 rounded-2xl">
          <p class="text-4xl font-extrabold text-red-600 mb-2">4000万+</p>
          <p class="text-sm text-gray-700 font-medium">每年老年人跌倒人次</p>
          <p class="text-xs text-gray-500 mt-1">跌倒是65岁以上老人意外死亡首因</p>
        </div>
        <div class="text-center p-6 bg-amber-50 rounded-2xl">
          <p class="text-4xl font-extrabold text-amber-600 mb-2">90%</p>
          <p class="text-sm text-gray-700 font-medium">居家养老占比</p>
          <p class="text-xs text-gray-500 mt-1">但缺乏专业监测手段</p>
        </div>
        <div class="text-center p-6 bg-blue-50 rounded-2xl">
          <p class="text-4xl font-extrabold text-blue-600 mb-2">72小时</p>
          <p class="text-sm text-gray-700 font-medium">跌倒后黄金救治窗口</p>
          <p class="text-xs text-gray-500 mt-1">独居老人平均发现时间远超此值</p>
        </div>
        <div class="text-center p-6 bg-purple-50 rounded-2xl">
          <p class="text-4xl font-extrabold text-purple-600 mb-2">万亿级</p>
          <p class="text-sm text-gray-700 font-medium">养老服务市场规模</p>
          <p class="text-xs text-gray-500 mt-1">2025年预计突破12万亿元</p>
        </div>
      </div>
    </section>

    <!-- 三大核心创新 -->
    <section class="bg-gray-50 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">三大核心创新</h2>
          <p class="text-gray-600">区别于传统"事后报警"方案的颠覆性技术路径</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow">
            <div class="w-14 h-14 bg-indigo-100 rounded-2xl flex items-center justify-center mb-6">
              <svg class="w-7 h-7 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">隐私优先的视觉AI</h3>
            <p class="text-gray-600 mb-4">原始视频<span class="font-semibold text-gray-900">永远不离开本地设备</span>。边缘端提取17个匿名骨骼关键点，云端仅处理坐标数据。</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>4特征融合跌倒检测（重心+躯干+速度+不动）</div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>5类日常活动实时识别</div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>95%边缘处理，符合PIPL/GDPR</div>
            </div>
          </div>
          <div class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow">
            <div class="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mb-6">
              <svg class="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">学术级精算引擎</h3>
            <p class="text-gray-600 mb-4">首次将保险精算方法融入养老风控——从<span class="font-semibold text-gray-900">"事后报警"到"事前定价"</span>。</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>Gompertz死亡力模型 h(t) = αe<sup>βt</sup></div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>Kaplan-Meier生存分析 + Greenwood 95%CI</div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>Cox比例风险 → 个性化保费定价</div>
            </div>
          </div>
          <div class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow">
            <div class="w-14 h-14 bg-rose-100 rounded-2xl flex items-center justify-center mb-6">
              <svg class="w-7 h-7 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">风控闭环系统</h3>
            <p class="text-gray-600 mb-4">检测→验证→预警→调度→干预→反馈，形成<span class="font-semibold text-gray-900">完整闭环</span>，不断自我优化。</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>多模态交叉验证降低误报率</div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>自动响应协议编排</div>
              <div class="flex items-center gap-2 text-gray-700"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span>子女/医生/机构/保险四方协同</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 四大用户角色 -->
    <section class="max-w-7xl mx-auto px-6 py-20">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">服务四大核心用户</h2>
        <p class="text-gray-600">每个角色都有专属界面和差异化价值</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <router-link to="/family" class="group p-6 bg-white border-2 border-gray-100 rounded-2xl hover:border-blue-500 hover:shadow-lg transition-all">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-500 transition-colors">
            <svg class="w-6 h-6 text-blue-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
          </div>
          <h3 class="font-bold text-gray-900 mb-2">子女端</h3>
          <p class="text-sm text-gray-600">实时状态、风险预警、远程通话、健康周报</p>
          <p class="text-xs text-blue-600 mt-3 font-medium">查看演示 →</p>
        </router-link>
        <router-link to="/doctor" class="group p-6 bg-white border-2 border-gray-100 rounded-2xl hover:border-green-500 hover:shadow-lg transition-all">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-green-500 transition-colors">
            <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
          </div>
          <h3 class="font-bold text-gray-900 mb-2">医生端</h3>
          <p class="text-sm text-gray-600">精算辅助诊断、衰弱追踪、康复方案生成</p>
          <p class="text-xs text-green-600 mt-3 font-medium">查看演示 →</p>
        </router-link>
        <router-link to="/institution" class="group p-6 bg-white border-2 border-gray-100 rounded-2xl hover:border-purple-500 hover:shadow-lg transition-all">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-purple-500 transition-colors">
            <svg class="w-6 h-6 text-purple-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m8-10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
          </div>
          <h3 class="font-bold text-gray-900 mb-2">机构端</h3>
          <p class="text-sm text-gray-600">风险热力图、自动排期、合规报告、KPI管理</p>
          <p class="text-xs text-purple-600 mt-3 font-medium">查看演示 →</p>
        </router-link>
        <router-link to="/data-privacy" class="group p-6 bg-white border-2 border-gray-100 rounded-2xl hover:border-amber-500 hover:shadow-lg transition-all">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-amber-500 transition-colors">
            <svg class="w-6 h-6 text-amber-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
          </div>
          <h3 class="font-bold text-gray-900 mb-2">保险端</h3>
          <p class="text-sm text-gray-600">人群风险画像、精算定价、理赔验证</p>
          <p class="text-xs text-amber-600 mt-3 font-medium">查看演示 →</p>
        </router-link>
      </div>
    </section>

    <!-- 技术架构流水线 -->
    <section class="bg-gray-900 text-white py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold mb-4">技术架构</h2>
          <p class="text-gray-400">边缘计算 × 精算模型 × 闭环风控</p>
        </div>
        <div class="grid grid-cols-5 gap-2 items-center text-center">
          <div class="bg-gray-800 rounded-2xl p-5"><div class="text-2xl mb-2">📹</div><p class="text-sm font-semibold">边缘设备</p><p class="text-xs text-gray-400 mt-1">姿态提取，视频不上传</p></div>
          <div class="text-gray-500 text-xs">骨骼坐标 →</div>
          <div class="bg-gray-800 rounded-2xl p-5"><div class="text-2xl mb-2">🧠</div><p class="text-sm font-semibold">AI分析层</p><p class="text-xs text-gray-400 mt-1">跌倒检测 + 活动识别</p></div>
          <div class="text-gray-500 text-xs">风险特征 →</div>
          <div class="bg-gray-800 rounded-2xl p-5"><div class="text-2xl mb-2">📊</div><p class="text-sm font-semibold">精算引擎</p><p class="text-xs text-gray-400 mt-1">Gompertz + Cox 定价</p></div>
        </div>
      </div>
    </section>

    <!-- B2B2C 商业模式 -->
    <section class="max-w-7xl mx-auto px-6 py-20">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">B2B2C 三端商业模式</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="border-2 border-blue-100 rounded-2xl p-6 bg-blue-50/30">
          <h3 class="font-bold text-blue-900 mb-3 text-lg">C端 · 家庭订阅</h3>
          <p class="text-3xl font-extrabold text-blue-600 mb-1">¥99<span class="text-base font-normal text-gray-500">/月</span></p>
          <p class="text-sm text-gray-600 mb-4">基础守护套餐</p>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start gap-2"><span class="text-blue-500 mt-0.5">✓</span>24小时跌倒检测与预警</li>
            <li class="flex items-start gap-2"><span class="text-blue-500 mt-0.5">✓</span>每周健康报告推送</li>
            <li class="flex items-start gap-2"><span class="text-blue-500 mt-0.5">✓</span>紧急联系人自动通知</li>
          </ul>
        </div>
        <div class="border-2 border-purple-200 rounded-2xl p-6 bg-purple-50/30 relative">
          <div class="absolute -top-3 right-4 px-3 py-1 bg-purple-600 text-white text-xs rounded-full font-medium">主力营收</div>
          <h3 class="font-bold text-purple-900 mb-3 text-lg">B端 · 机构SaaS</h3>
          <p class="text-3xl font-extrabold text-purple-600 mb-1">¥5<span class="text-base font-normal text-gray-500">/床位/天</span></p>
          <p class="text-sm text-gray-600 mb-4">200床位起</p>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start gap-2"><span class="text-purple-500 mt-0.5">✓</span>住户风险热力图</li>
            <li class="flex items-start gap-2"><span class="text-purple-500 mt-0.5">✓</span>护理任务自动排期</li>
            <li class="flex items-start gap-2"><span class="text-purple-500 mt-0.5">✓</span>合规报告一键生成</li>
          </ul>
        </div>
        <div class="border-2 border-amber-100 rounded-2xl p-6 bg-amber-50/30">
          <h3 class="font-bold text-amber-900 mb-3 text-lg">保险端 · 数据服务</h3>
          <p class="text-3xl font-extrabold text-amber-600 mb-1">按量<span class="text-base font-normal text-gray-500">计费</span></p>
          <p class="text-sm text-gray-600 mb-4">API调用计费</p>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start gap-2"><span class="text-amber-500 mt-0.5">✓</span>匿名化人群风险报告</li>
            <li class="flex items-start gap-2"><span class="text-amber-500 mt-0.5">✓</span>个性化精算定价API</li>
            <li class="flex items-start gap-2"><span class="text-amber-500 mt-0.5">✓</span>理赔验证数据支撑</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 竞品对比 -->
    <section class="bg-gray-50 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">与竞品的本质差异</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-xl p-5">
            <p class="text-sm font-medium text-gray-500 mb-3">能力维度</p>
            <div class="space-y-4 text-sm font-medium text-gray-700">
              <p>隐私保护方式</p><p>风险预测</p><p>精算定价</p><p>闭环干预</p><p>多角色协同</p>
            </div>
          </div>
          <div class="bg-indigo-50 rounded-xl p-5 border-2 border-indigo-200">
            <p class="text-sm font-bold text-indigo-700 mb-3">银龄精算师 ✨</p>
            <div class="space-y-4 text-sm font-semibold text-indigo-800">
              <p>边缘计算+骨骼匿名化</p><p>30天概率预测(Cox)</p><p>Gompertz精算定价</p><p>检测→验证→干预→反馈</p><p>子女/医生/机构/保险</p>
            </div>
          </div>
          <div class="bg-white rounded-xl p-5">
            <p class="text-sm font-medium text-gray-500 mb-3">传统监控方案</p>
            <div class="space-y-4 text-sm text-gray-500">
              <p>视频全量上传云端</p><p>无预测，仅检测</p><p>不具备</p><p>单点报警</p><p>仅机构端</p>
            </div>
          </div>
          <div class="bg-white rounded-xl p-5">
            <p class="text-sm font-medium text-gray-500 mb-3">健康管理App</p>
            <div class="space-y-4 text-sm text-gray-500">
              <p>手动输入数据</p><p>简单阈值告警</p><p>不具备</p><p>无闭环</p><p>仅用户端</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-gradient-to-r from-indigo-600 to-blue-600 text-white py-16">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <h2 class="text-3xl font-bold mb-4">让天下父母老有所护</h2>
        <p class="text-blue-200 mb-8">银龄精算师 —— 用AI精算守护每一位长者的安全与尊严</p>
        <router-link to="/dashboard" class="inline-block px-8 py-3 bg-white text-blue-700 rounded-xl font-semibold hover:bg-blue-50 transition">立即体验</router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-400 py-8">
      <div class="max-w-7xl mx-auto px-6 text-center text-sm">
        <p>银龄精算师 © 2025 · 第十二届中国国际大学生创新大赛参赛作品</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

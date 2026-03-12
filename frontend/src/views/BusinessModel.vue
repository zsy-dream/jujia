<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <router-link to="/" class="text-gray-400 hover:text-gray-600 transition">← 返回首页</router-link>
          <span class="text-gray-300">|</span>
          <h1 class="text-lg font-bold text-gray-900">商业模式与市场分析</h1>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-12 space-y-16">
      <!-- 市场规模 TAM/SAM/SOM -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">市场规模</h2>
        <p class="text-gray-500 mb-8">银发经济万亿赛道，养老风控是关键缺口</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-white rounded-2xl p-6 shadow-sm text-center">
            <div class="w-32 h-32 mx-auto mb-4 rounded-full border-8 border-blue-100 flex items-center justify-center">
              <div>
                <p class="text-3xl font-extrabold text-blue-600">12万亿</p>
                <p class="text-xs text-gray-500">2025E</p>
              </div>
            </div>
            <h3 class="font-bold text-gray-900">TAM · 总可寻址市场</h3>
            <p class="text-sm text-gray-500 mt-1">中国养老服务市场总规模</p>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm text-center">
            <div class="w-32 h-32 mx-auto mb-4 rounded-full border-8 border-indigo-100 flex items-center justify-center">
              <div>
                <p class="text-3xl font-extrabold text-indigo-600">3200亿</p>
                <p class="text-xs text-gray-500">智慧养老</p>
              </div>
            </div>
            <h3 class="font-bold text-gray-900">SAM · 可服务市场</h3>
            <p class="text-sm text-gray-500 mt-1">智慧养老+养老保险科技</p>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm text-center">
            <div class="w-32 h-32 mx-auto mb-4 rounded-full border-8 border-purple-100 flex items-center justify-center">
              <div>
                <p class="text-3xl font-extrabold text-purple-600">80亿</p>
                <p class="text-xs text-gray-500">首期目标</p>
              </div>
            </div>
            <h3 class="font-bold text-gray-900">SOM · 可获取市场</h3>
            <p class="text-sm text-gray-500 mt-1">居家+机构养老风控SaaS</p>
          </div>
        </div>
      </section>

      <!-- B2B2C 收入模型 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">B2B2C 三端收入模型</h2>
        <p class="text-gray-500 mb-8">多元化收入结构，降低单一渠道依赖</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-2xl p-6 shadow-sm border-t-4 border-blue-500">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-blue-900 text-lg">C端 · 家庭守护</h3>
              <span class="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">占比 25%</span>
            </div>
            <p class="text-3xl font-extrabold text-gray-900 mb-4">¥99-299<span class="text-sm font-normal text-gray-500">/月</span></p>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between"><span class="text-gray-600">基础版</span><span class="font-medium">¥99/月 · 跌倒检测+周报</span></div>
              <div class="flex justify-between"><span class="text-gray-600">专业版</span><span class="font-medium">¥199/月 · +精算报告</span></div>
              <div class="flex justify-between"><span class="text-gray-600">旗舰版</span><span class="font-medium">¥299/月 · +医生对接</span></div>
            </div>
            <div class="mt-4 p-3 bg-blue-50 rounded-lg text-xs text-blue-700">
              目标用户：独居/空巢老人的子女家庭<br>
              获客方式：社区推广+保险渠道分销
            </div>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm border-t-4 border-purple-500">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-purple-900 text-lg">B端 · 机构SaaS</h3>
              <span class="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded-full">占比 55%（主力）</span>
            </div>
            <p class="text-3xl font-extrabold text-gray-900 mb-4">¥5<span class="text-sm font-normal text-gray-500">/床位/天</span></p>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between"><span class="text-gray-600">年费模式</span><span class="font-medium">¥5×床位×365天</span></div>
              <div class="flex justify-between"><span class="text-gray-600">200床标准</span><span class="font-medium">≈36.5万/年/机构</span></div>
              <div class="flex justify-between"><span class="text-gray-600">增值服务</span><span class="font-medium">合规报告+培训</span></div>
            </div>
            <div class="mt-4 p-3 bg-purple-50 rounded-lg text-xs text-purple-700">
              目标用户：中大型养老院、社区养老中心<br>
              核心价值：降低事故率30%+合规自动化
            </div>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm border-t-4 border-amber-500">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-amber-900 text-lg">保险端 · 数据服务</h3>
              <span class="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-full">占比 20%</span>
            </div>
            <p class="text-3xl font-extrabold text-gray-900 mb-4">按量计费</p>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between"><span class="text-gray-600">精算定价API</span><span class="font-medium">¥5/次调用</span></div>
              <div class="flex justify-between"><span class="text-gray-600">人群风险报告</span><span class="font-medium">¥2万/份</span></div>
              <div class="flex justify-between"><span class="text-gray-600">理赔验证</span><span class="font-medium">¥50/单</span></div>
            </div>
            <div class="mt-4 p-3 bg-amber-50 rounded-lg text-xs text-amber-700">
              目标用户：养老保险公司、健康险部门<br>
              核心价值：精算科学定价+理赔欺诈检测
            </div>
          </div>
        </div>
      </section>

      <!-- 财务预测 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">财务预测</h2>
        <p class="text-gray-500 mb-8">保守预估，3年实现盈利</p>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div class="grid grid-cols-4 gap-0">
            <div class="p-4 bg-gray-50 font-semibold text-sm text-gray-700 border-b">指标</div>
            <div class="p-4 bg-gray-50 font-semibold text-sm text-gray-700 text-center border-b">Y1（验证期）</div>
            <div class="p-4 bg-gray-50 font-semibold text-sm text-gray-700 text-center border-b">Y2（扩张期）</div>
            <div class="p-4 bg-gray-50 font-semibold text-sm text-gray-700 text-center border-b">Y3（盈利期）</div>
            <div class="p-4 text-sm text-gray-600 border-b">C端付费家庭</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">2,000户</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">15,000户</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">80,000户</div>
            <div class="p-4 text-sm text-gray-600 border-b">B端合作机构</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">20家</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">150家</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">600家</div>
            <div class="p-4 text-sm text-gray-600 border-b">保险合作方</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">2家</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">8家</div>
            <div class="p-4 text-sm text-center text-gray-900 font-medium border-b">20家</div>
            <div class="p-4 text-sm text-gray-600 border-b">预计营收</div>
            <div class="p-4 text-sm text-center font-bold text-blue-600 border-b">960万</div>
            <div class="p-4 text-sm text-center font-bold text-blue-600 border-b">7,200万</div>
            <div class="p-4 text-sm text-center font-bold text-blue-600 border-b">3.2亿</div>
            <div class="p-4 text-sm text-gray-600">净利润率</div>
            <div class="p-4 text-sm text-center font-bold text-red-500">-35%</div>
            <div class="p-4 text-sm text-center font-bold text-amber-500">8%</div>
            <div class="p-4 text-sm text-center font-bold text-green-600">25%</div>
          </div>
        </div>
      </section>

      <!-- 五大护城河 -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">五大竞争护城河</h2>
        <p class="text-gray-500 mb-8">构建多维壁垒，先发优势持续放大</p>
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div class="bg-white rounded-xl p-5 shadow-sm text-center">
            <div class="w-12 h-12 bg-indigo-100 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl">🔬</div>
            <h3 class="font-bold text-sm text-gray-900 mb-1">技术壁垒</h3>
            <p class="text-xs text-gray-500">边缘AI+精算引擎的独特技术栈，竞品难以快速复制</p>
          </div>
          <div class="bg-white rounded-xl p-5 shadow-sm text-center">
            <div class="w-12 h-12 bg-blue-100 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl">📊</div>
            <h3 class="font-bold text-sm text-gray-900 mb-1">数据飞轮</h3>
            <p class="text-xs text-gray-500">用户越多→数据越丰富→模型越精准→吸引更多用户</p>
          </div>
          <div class="bg-white rounded-xl p-5 shadow-sm text-center">
            <div class="w-12 h-12 bg-green-100 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl">🏥</div>
            <h3 class="font-bold text-sm text-gray-900 mb-1">渠道网络</h3>
            <p class="text-xs text-gray-500">养老机构+保险公司的B端渠道一旦建立难以替换</p>
          </div>
          <div class="bg-white rounded-xl p-5 shadow-sm text-center">
            <div class="w-12 h-12 bg-amber-100 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl">📜</div>
            <h3 class="font-bold text-sm text-gray-900 mb-1">合规先发</h3>
            <p class="text-xs text-gray-500">PIPL合规的隐私优先架构，政策收紧时成为准入门槛</p>
          </div>
          <div class="bg-white rounded-xl p-5 shadow-sm text-center">
            <div class="w-12 h-12 bg-rose-100 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl">🔄</div>
            <h3 class="font-bold text-sm text-gray-900 mb-1">生态锁定</h3>
            <p class="text-xs text-gray-500">四方协同生态(子女/医生/机构/保险)形成网络效应</p>
          </div>
        </div>
      </section>

      <!-- 社会价值 -->
      <section class="bg-indigo-900 text-white -mx-6 px-6 py-16 rounded-2xl">
        <div class="max-w-4xl mx-auto text-center">
          <h2 class="text-2xl font-bold mb-6">社会价值 × 商业价值</h2>
          <p class="text-indigo-200 mb-8">这不仅是一门生意，更是一份责任</p>
          <div class="grid grid-cols-3 gap-8">
            <div>
              <p class="text-3xl font-extrabold mb-2">减少30%</p>
              <p class="text-sm text-indigo-300">养老机构事故率</p>
            </div>
            <div>
              <p class="text-3xl font-extrabold mb-2">节省50%</p>
              <p class="text-sm text-indigo-300">子女远程守护时间成本</p>
            </div>
            <div>
              <p class="text-3xl font-extrabold mb-2">降低20%</p>
              <p class="text-sm text-indigo-300">保险公司赔付率</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
</script>

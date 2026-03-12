import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import Reports from '../views/Reports.vue'
import Profile from '../views/Profile.vue'
import Settings from '../views/Settings.vue'
import FamilyApp from '../views/FamilyApp.vue'
import InstitutionDashboard from '../views/InstitutionDashboard.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import DataPrivacy from '../views/DataPrivacy.vue'
import BusinessModel from '../views/BusinessModel.vue'
import TechShowcase from '../views/TechShowcase.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '银龄精算师 - 居家养老风控闭环系统' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/family',
    name: 'FamilyApp',
    component: FamilyApp,
    meta: { title: '子女端 - 关爱妈妈' }
  },
  {
    path: '/institution',
    name: 'InstitutionDashboard',
    component: InstitutionDashboard,
    meta: { title: '机构管理后台 - 阳光养老社区' }
  },
  {
    path: '/doctor',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { title: '医生工作台 - 社区卫生服务中心' }
  },
  {
    path: '/privacy',
    name: 'DataPrivacy',
    component: DataPrivacy,
    meta: { title: '数据透明与隐私保护中心' }
  },
  {
    path: '/business',
    name: 'BusinessModel',
    component: BusinessModel,
    meta: { title: '商业模式与市场分析' }
  },
  {
    path: '/tech-showcase',
    name: 'TechShowcase',
    component: TechShowcase,
    meta: { title: '技术架构与创新亮点' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

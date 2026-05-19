import { createRouter, createWebHistory } from 'vue-router'
import RequestListView from '../views/RequestListView.vue'
import LoginView from '../views/LoginView.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
	{ path: '/', redirect: '/login' },
	{ path: '/requests', component: RequestListView },
	{ path: '/requests/:id',
	  name: 'request-detail',
	  component: () => import('../views/RequestDetailView.vue') },
	{ path: '/login', component: LoginView },
    ],
})

router.beforeEach((to) => {
    const userStore = useUserStore()
    userStore.loadUser()
    if (to.path !== '/login' && !userStore.user) {
	return '/login'
    }
})

export default router

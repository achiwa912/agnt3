<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const users = ref([])
const userStore = useUserStore()
const router = useRouter()

function selectUser(user) {
  userStore.setUser(user)
  router.push('/requests')
}

onMounted(async () => {
  const res = await fetch('http://localhost:8001/users')
  users.value = await res.json()
})
</script>

<template>
  <div class="p-6">
    <div class="dropdown">
      <div tabindex="0"  role="button" class="btn m-1">Choose user</div>
      <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box p-2 shadow">
	<li v-for="user in users" :key="user.id">
	  <a @click="selectUser(user)">{{ user.name }}</a>
	</li>
      </ul>
    </div>
  </div>
</template>

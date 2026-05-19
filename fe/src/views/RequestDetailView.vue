<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useUserStore } from '../stores/user'

const request = ref(null)
const records = ref([])
const userStore = useUserStore()
const route = useRoute()

const reqId = route.params.id

onMounted(async () => {
  let res = await fetch(`http://localhost:8001/requests/${reqId}`)
  request.value = await res.json()
  res = await fetch(`http://localhost:8001/requests/${reqId}/records`)
  records.value = await res.json()
})

</script>

<template>
  <!-- Navbar -->
  <div class="navbar bg-primary shadow-sm">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">agnt3</a>
    </div>
    <div class="flex-none pr-4"><RouterLink to="/requests">{{ userStore.user.fullname }}</RouterLink></div>
  </div>



  
</template>

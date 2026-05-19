<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const requests = ref([])
const userStore = useUserStore()
const modalRef = ref(null)
const newreq = ref('')
const loading = ref(false)
const router = useRouter()

const openModal = () => { modalRef.value?.showModal() }
const closeModal = () => { modalRef.value?.close() }
const handleSubmit = async () => {
  if (newreq.value.trim()) {
    loading.value = true
    closeModal()
    const req = newreq.value.trim()
    newreq.value = ''
    const res = await fetch(
      'http://localhost:8001/requests',
      {
	method: 'POST',
	headers: {
	  'Content-Type': 'application/json'
	},
	body: JSON.stringify({
	  user_id: userStore.user.id,
	  req_text: req
	})
      }
    )
    loading.value = false
    const res2 = await fetch(`http://localhost:8001/requests/${userStore.user.id}`)
    requests.value = await res2.json()
  }
}
const denied = computed(() => requests.value.filter(r => r.decision === 'denied').length)
const waiting = computed(() => requests.value.filter(r => r.status !== 'decided').length)

onMounted(async () => {
  const res = await fetch(`http://localhost:8001/users/${userStore.user.id}/requests`)
  requests.value = await res.json()
})

</script>

<template>
  <!-- Navbar -->
  <div class="navbar bg-primary shadow-sm">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">agnt3</a>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
	<li>
	  <details>
	    <summary>{{ userStore.user.fullname }}</summary>
	    <ul class="bg-base-100 rounded-t-none p-2">
	      <li @click="openModal"><a class="whitespace-nowrap">New request</a></li>
	      <li>
		<RouterLink to="/login" class="whitespace-nowrap">
		  Logout
		</RouterLink>
	      </li>
	    </ul>
	  </details>
	</li>
      </ul>
    </div>
  </div>
  <dialog ref="modalRef" class="modal">
    <div class="modal-box">
      <p class="py-4">Enter a new request:</p>
      <form @submit.prevent="handleSubmit">
	<div class="form-control">
	  <input v-model="newreq" type="text" placeholder="Type request" class="input input-bordered w-full" required />
	</div>
	<div class="modal-action">
	  <button type="button" class="btn" @click="closeModal">Cancel</button>
	  <button type="submit" class="btn btn-primary" :disabled="loading">Submit</button>
	</div>
      </form>
    </div>
  </dialog>

  <!-- stats -->
  <div class="flex justify-center p-6">
    <div class="stats shadow">
      <div class="stat">
	<div class="stat-figure">
	  <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="inline-block h-8 w-8 stroke-current"
	  >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
	  </svg>
	</div>
	<div class="stat-title">{{ userStore.user.role }}</div>
	<div class="stat-value">{{ userStore.user.name }}</div>
	<div class="stat-desc">{{ userStore.user.fullname }}</div>
      </div>

      <div class="stat">
	<div class="stat-figure text-primary">
	  <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="inline-block h-8 w-8 stroke-current"
	  >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
            ></path>
	  </svg>
	</div>
	<div class="stat-title">Available</div>
	<div class="stat-value text-primary">
	  {{ userStore.user.pto_assigned - userStore.user.pto_consumed }}
	</div>
	<div class="stat-desc">PTO days</div>
      </div>
      
      <div class="stat">
	<div class="stat-figure text-pink-400">
	  <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="inline-block h-8 w-8 stroke-current"
	  >
	    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
		  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
	  </svg>
	</div>
	<div class="stat-title">Denied</div>
	<div class="stat-value text-pink-400">
	  {{ denied }}
	</div>
	<div class="stat-desc">requests</div>
      </div>
      <div class="stat">
	<div class="stat-figure text-accent">
	  <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="inline-block h-8 w-8 stroke-current"
	  >
	    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
		  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
	  </svg>
	</div>
	<div class="stat-title">Waiting</div>
	<div class="stat-value text-accent">
	  {{ waiting }}
	</div>
	<div class="stat-desc">requests</div>
      </div>
    </div>
  </div>
      
  <!-- Requests table -->
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Requests</h1>
    <table class="table table-zebra w-full">
      <thead>
	<tr>
	  <th>ID</th>
	  <th>Request</th>
	  <th>Status</th>
	  <th>Decision</th>
	  <th>Created</th>
	</tr>
      </thead>
      <tbody>
	<tr v-for="req in requests" :key="req.id" :title="(['pending_manager', 'pending_vp'].includes(req.status)) || (req.decision === 'denied') ? req.reason : ''" @click="router.push(`/requests/${req.id}`)">
	  <td>{{ req.id }}</td>
	  <td>{{ req.request }}</td>
	  <td><span class="badge badge-info">{{ req.status }}</span></td>
	  <td>{{ req.decision }}</td>
	  <td>{{ req.created_at }}</td>
	</tr>
      </tbody>
    </table>
  </div>
</template>

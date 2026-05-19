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
  <nav class="navbar bg-[#f8f9fc] dark:bg-base-100 border-b border-primary/10 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto w-full px-6 py-2">
      <div class="flex items-center justify-between w-full">
      
	<!-- Logo -->
	<a href="/" class="flex items-center gap-2.5">
          <span class="text-2xl font-semibold tracking-tighter text-base-content">agnt3</span>
	</a>

	<!-- Right side -->
	<div class="flex items-center gap-6">
        
          <!-- New Request -->
          <button 
            @click="openModal"
            class="btn btn-primary btn-sm rounded-2xl px-5 py-2.5 text-sm font-medium shadow-sm hover:shadow transition-all active:scale-95">
            + New Request
          </button>

          <!-- User Menu -->
          <div class="dropdown dropdown-end">
            <label tabindex="0" class="flex items-center gap-3 cursor-pointer py-1">
              <div>
		<p class="font-medium text-sm">{{ userStore.user.fullname }}</p>
              </div>
            
              <div class="w-8 h-8 bg-primary/10 text-primary rounded-2xl flex items-center justify-center font-medium border border-primary/20">
		{{ userStore.user.fullname?.charAt(0) }}
              </div>
            </label>

            <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-3xl shadow-lg w-52 p-2 mt-2 border border-base-200">
              <li><a @click="openModal" class="rounded-2xl py-2.5">+ New Request</a></li>
              <li><RouterLink to="/login" class="rounded-2xl py-2.5 text-error">Logout</RouterLink></li>
            </ul>
          </div>
	</div>
      </div>
    </div>
  </nav>
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
    <div class="stats border border-base-200 px-6 py-3 rounded-3xl shadow-sm hover:shadow-2xl transition-all duration-300 overflow-hidden">
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
  <div class="p-6 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-semibold tracking-tight">Requests</h1>
      <!-- Optional: Add filter/search here later -->
    </div>

    <div class="space-y-4">
      <div 
	v-for="req in requests" 
	:key="req.id"
	@click="router.push(`/requests/${req.id}`)"
	class="group bg-base-100 hover:bg-base-200 border border-base-200 rounded-3xl px-6 py-5 
               transition-all duration-300 hover:shadow-xl cursor-pointer flex items-center gap-6"
	:title="(['pending_manager', 'pending_vp'].includes(req.status)) || (req.decision === 'denied') ? req.reason : ''"
      >
      
	<!-- ID -->
	<div class="w-20 font-mono text-sm text-base-content/70">
          #{{ req.id }}
	</div>

	<!-- Main Content -->
	<div class="flex-1 min-w-0">
          <p class="font-medium text-base truncate">{{ req.request }}</p>
          <p class="text-sm text-base-content/60 mt-1">
            {{ req.created_at }}
          </p>
	</div>

	<!-- Status -->
	<div>
          <span 
            class="badge px-5 py-3 text-sm font-medium"
            :class="{
              'badge-info': req.status.includes('pending'),
              'badge-success': req.decision === 'approved',
              'badge-error': req.decision === 'denied',
              'badge-warning': req.status === 'pending_vp'
            }">
            {{ req.status }}
          </span>
	</div>

	<!-- Decision -->
	<div class="w-28 text-center">
          <span 
            class="inline-block px-4 py-1.5 rounded-2xl text-sm font-medium"
            :class="{
              'bg-success/10 text-success': req.decision === 'approved',
              'bg-error/10 text-error': req.decision === 'denied',
              'bg-warning/10 text-warning': !req.decision || req.decision === 'pending'
            }">
            {{ req.decision || '—' }}
          </span>
	</div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useUserStore } from '../stores/user'

const req = ref(null)
const rcrds = ref([])
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const showEditModal = ref(false)
const editForm = ref({ request: '' })
const reqId = route.params.id

const canCancel = () => { return req.value?.status !== 'cancelled' }
const canAppeal = () => { return (req.value?.decision === 'denied' && req.value?.decider_id == 1 && req.value?.status !== 'cancelled') }
const canEdit = () => { return (req.value?.decision !== 'approved' || req.value?.status === 'cancelled') }

const appealRequest = async () => {
  const sts = userStore.user.role === 'employee' ? 'pending_manager' : 'pening_vp'
  const act = userStore.user.role === 'employee' ? 'deferred_to_manager' : 'deferred_to_vp'
  const res = await fetch(
    `http://localhost:8001/requests/${reqId}`,
    {
      method: 'PATCH',
      headers: {
	'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: sts, action: act, action_by: userStore.user.name })
    }
  )
  req.value = await (await fetch(`http://localhost:8001/requests/${reqId}`)).json()
  rcrds.value = await (await fetch(`http://localhost:8001/requests/${reqId}/records`)).json()
}

const cancelRequest = async () => {
  const res = await fetch(
    `http://localhost:8001/requests/${reqId}`,
    {
      method: 'PATCH',
      headers: {
	'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'cancelled', action: 'cancelled', action_by: userStore.user.name })
    }
  )
  req.value = await (await fetch(`http://localhost:8001/requests/${reqId}`)).json()
  rcrds.value = await (await fetch(`http://localhost:8001/requests/${reqId}/records`)).json()
}

const resubmitRequest = async () => {
  const reqtxt = editForm.value.request.trim()
  if (!reqtxt) return

  closeEditModal()
  const res = await fetch(
    `http://localhost:8001/requests/${reqId}`,
    {
      method: 'PATCH',
      headers: {
	'Content-Type': 'application/json'
      },
      body: JSON.stringify({ request: reqtxt, status: 'processing', action: 'resubmitted', action_by: userStore.user.name })
    }
  )
  req.value = await (await fetch(`http://localhost:8001/requests/${reqId}`)).json()
  rcrds.value = await (await fetch(`http://localhost:8001/requests/${reqId}/records`)).json()
}

const openEditModal = () => {
  editForm.value.request = req.value?.request || ''
  showEditModal.value = true
}

const closeEditModal = () => {
  editForm.value.request = ''
  showEditModal.value = false
}

onMounted(async () => {
  userStore.loadUser()
  let res = await fetch(`http://localhost:8001/requests/${reqId}`)
  req.value = await res.json()
  res = await fetch(`http://localhost:8001/requests/${reqId}/records`)
  rcrds.value = await res.json()
  loading.value = false
})

</script>

<template>
  <!-- Navbar -->
  <nav class="navbar bg-[#f8f9fc] dark:bg-base-100 border-b border-primary/10 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto w-full px-6 py-3">
      <div class="flex items-center justify-between w-full">
      
	<!-- Logo -->
	<a href="/" class="flex items-center gap-2.5">
          <span class="text-2xl font-semibold tracking-tighter text-base-content">agnt3</span>
	</a>

	<!-- Right side -->
	<div class="flex items-center gap-6">
	  <RouterLink to="/requests" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
    
	    <!-- Name -->
	    <div class="font-medium text-sm text-right">
	      {{ userStore.user.fullname }}
	    </div>

	    <!-- Avatar -->
	    <div class="w-8 h-8 bg-primary/10 text-primary rounded-2xl flex items-center justify-center font-medium border border-primary/20 flex-shrink-0">
	      {{ userStore.user.fullname?.charAt(0) }}
	    </div>
	    
	  </RouterLink>
	</div>
      </div>
    </div>
  </nav>

  <!-- request detail -->
  <div v-if="!loading" class="p-6 max-w-4xl mx-auto">
    <div class="card bg-base-100 border border-base-200 rounded-3xl shadow-sm overflow-hidden">
    
      <!-- Card Header -->
      <div class="px-8 pt-8 pb-6 border-b border-base-200 bg-base-200/50">
	<div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-base-content/60 font-mono">REQUEST #{{ reqId }}</p>
            <p class="text-xl font-semibold mt-1">{{ req.created_at || '-' }}</p>
          </div>
        
          <!-- Status & Decision Badges -->
          <div class="flex flex-col items-end gap-3">
            <span 
              class="badge px-5 py-2.5 text-sm font-medium"
              :class="{
		'badge-info': req.status?.includes('pending'),
		'badge-success': req.decision === 'approved',
		'badge-error': req.decision === 'denied',
		'badge-warning': req.status?.includes('pending') || req.status?.includes('cancelled')
              }">
              {{ req.status }}
            </span>
          
            <span 
              class="px-5 py-1.5 rounded-2xl text-sm font-medium"
              :class="{
		'bg-success/10 text-success': req.decision === 'approved',
		'bg-error/10 text-error': req.decision === 'denied'
              }">
              {{ req.decision || 'Pending' }}
            </span>
          </div>
	</div>
      </div>

      <!-- Main Content -->
      <div class="p-8 space-y-8">
      
	<!-- Request -->
	<div>
          <p class="uppercase text-xs tracking-widest text-base-content/60 font-medium mb-3">Request</p>
          <p class="text-lg leading-relaxed">{{ req.request }}</p>
	</div>

	<!-- Decision Info -->
	<div v-if="req.decided_by || req.decided_at" class="bg-base-200/50 rounded-2xl p-6">
          <p class="uppercase text-xs tracking-widest text-base-content/60 font-medium mb-2">Decision</p>
          <p class="text-base-content">
            <span class="font-medium">{{ req.decider || '—' }}</span>
            <span v-if="req.decided_at" class="text-base-content/70"> • {{ req.decided_at }}</span>
          </p>
	</div>

	<!-- Reason -->
	<div v-if="req.reason">
          <p class="uppercase text-xs tracking-widest text-base-content/60 font-medium mb-3">Reason</p>
          <p class="text-base-content/80 whitespace-pre-wrap">{{ req.reason }}</p>
	</div>

	<!-- Policy IDs -->
	<div v-if="req.policy_ids">
          <p class="uppercase text-xs tracking-widest text-base-content/60 font-medium mb-2">Policies</p>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="policy in (Array.isArray(req.policy_ids) ? req.policy_ids : [req.policy_ids])"
              :key="policy"
              class="badge badge-neutral badge-outline">
              {{ policy }}
            </span>
          </div>
	</div>

      </div>

      <!-- Action Buttons Footer -->
      <div class="px-8 py-6 bg-base-200/50 border-t border-base-200 flex flex-wrap gap-3">
	<!-- Cancel / Decline -->
	<button 
          v-if="canCancel()"
          @click="cancelRequest"
          class="btn btn-error btn-outline rounded-2xl px-6">
          Cancel Request
	</button>

	<!-- Appeal -->
	<button 
          v-if="canAppeal()"
          @click="appealRequest"
          class="btn btn-warning btn-outline rounded-2xl px-6">
          Appeal to Manager
	</button>

	<!-- Edit & Resubmit -->
	<button 
          v-if="canEdit()"
          @click="openEditModal"
          class="btn btn-primary rounded-2xl px-6">
          Edit & Resubmit
	</button>
      </div>
    
    </div>
  </div>

  <!-- Edit & Resubmit Modal -->
  <dialog v-if="!loading && showEditModal" class="modal modal-open">
    <div class="modal-box max-w-lg rounded-3xl">
      <h3 class="font-semibold text-lg mb-6">Edit & Resubmit Request</h3>
    
      <textarea 
	v-model="editForm.request"
	class="textarea textarea-bordered w-full h-32 rounded-2xl"
	placeholder="Update your request..."></textarea>

      <div class="modal-action mt-6">
	<button @click="closeEditModal" class="btn btn-ghost rounded-2xl">Cancel</button>
	<button @click="resubmitRequest" class="btn btn-primary rounded-2xl">Resubmit Request</button>
      </div>
    </div>
    <div @click="showEditModal = false" class="modal-backdrop"></div>
  </dialog>

  <!-- Records -->
  <div class="p-6 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-semibold tracking-tight">History</h1>
    </div>
    <div class="space-y-4">
      <div v-for="rc in rcrds" :key="rc.id"
	   class="group bg-base-100 hover:bg-base-120 border border-base-200
		  rounded-3xl px-6 py-6 transition-all duration-300
		  hover:shadow-xl grid grid-cols-12 gap-x-4 items-center">

	<div class="col-span-1 font-mono text-sm text-base-content/70 pt-1">
	  #{{ rc.id }}
	</div>

	<div class="col-span-3">
	  <p class="text-sm text-base-content/60 mt-1">{{ rc.action_at }}</p>
	  <p class="font-medium text-base">{{ rc.action }}</p>
	  <p class="text-sm text-base-content/70">{{ rc.user_name }}</p>
	</div>

	<div class="col-span-3">
	  <div class="flex flex-col gap-2 w-fit">
            <span class="badge badge-info px-4 py-2">{{ rc.status }}</span>
            <span 
              class="px-4 py-2 rounded-2xl text-sm font-medium"
              :class="{
		'bg-success/10 text-success': rc.decision === 'approved',
		'bg-error/10 text-error': rc.decision === 'denied'
              }">
              {{ rc.decision }}
            </span>
	  </div>
	</div>

	<div class="col-span-5 text-sm leading-relaxed text-base-content/80">
	  <p v-if="rc.request" class="mb-2">
            <span class="font-medium text-base-content/70">Request:</span> 
            {{ rc.request }}
	  </p>
	  <p v-if="rc.reason" class="mb-2">
            <span class="font-medium text-base-content/70">Reason:</span> 
            {{ rc.reason }}
	  </p>
	  <p v-if="rc.attach_path" class="text-primary hover:underline cursor-pointer">
            📎 {{ rc.attach_path }}
	  </p>
	</div>

      </div>
    </div>
  </div>
  
</template>

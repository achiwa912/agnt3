<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useLlmStore } from '../stores/user'

const users = ref([])
const llms = ref([])
const userStore = useUserStore()
const llmStore = useLlmStore()
const router = useRouter()

const selectedUser = ref(null)
const selectedLlm = ref('google-gla:gemini-3.1-flash-lite')
const loading = ref(false)

// Refs for dropdown triggers
const userDropdownTrigger = ref(null)
const llmDropdownTrigger = ref(null)

const login = async () => {
  if (!selectedUser.value) {
    alert('Please select a user')
    return
  }
  if (!selectedLlm.value) {
    alert('Please select an LLM model')
    return
  }

  loading.value = true
  userStore.setUser(selectedUser.value)
  llmStore.setLlm(selectedLlm.value)

  await new Promise(r => setTimeout(r, 300))
  router.push('/requests')
}

// Close dropdown after selection
const selectUser = (user) => {
  selectedUser.value = user
  userDropdownTrigger.value?.blur()   // This closes the DaisyUI dropdown
}

const selectLlm = (llm) => {
  selectedLlm.value = llm
  llmDropdownTrigger.value?.blur()    // This closes the DaisyUI dropdown
}

onMounted(async () => {
  try {
    const [modelsRes, usersRes] = await Promise.all([
      fetch('http://localhost:8001/models'),
      fetch('http://localhost:8001/users')
    ])

    llms.value = await modelsRes.json()
    users.value = await usersRes.json()
  } catch (err) {
    console.error('Failed to fetch data:', err)
  }
})
</script>

<template>
  <div class="min-h-screen bg-base-100 flex items-center justify-center p-6">
    <div class="max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center gap-3 mb-4">
          <span class="text-4xl font-bold tracking-tighter text-primary">agnt3</span>
        </div>
        <h1 class="text-3xl font-semibold tracking-tight">Welcome back</h1>
        <p class="text-base-content/60 mt-2">Sign in to continue</p>
      </div>

      <!-- Card -->
      <div class="bg-base-100 border border-base-200 rounded-3xl shadow-xl p-8 space-y-8">
        
        <!-- User Selection -->
        <div>
          <label class="block text-sm font-medium text-base-content/70 mb-2">User</label>
          <div class="dropdown w-full">
            <div ref="userDropdownTrigger"
                 tabindex="0" 
                 role="button"
                 class="btn btn-block justify-between h-14 text-left border-base-300 hover:border-primary/30 rounded-2xl">
              <span class="flex items-center gap-3">
                <div v-if="selectedUser" 
                     class="w-8 h-8 bg-primary/10 text-primary rounded-2xl flex items-center justify-center font-medium">
                  {{ selectedUser.fullname?.charAt(0) }}
                </div>
                {{ selectedUser?.fullname || selectedUser?.name || 'Select User' }}
              </span>
              <span class="opacity-50">▼</span>
            </div>
            <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-2xl shadow-xl w-full p-2 z-50 border border-base-200 max-h-80 overflow-auto">
              <li v-for="user in users" :key="user.id">
                <a @click="selectUser(user)" class="rounded-xl py-3 px-4 flex items-center gap-3">
                  <div class="w-9 h-9 bg-primary/10 text-primary rounded-2xl flex items-center justify-center font-medium">
                    {{ user.fullname?.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium">{{ user.fullname }}</p>
                    <p class="text-xs text-base-content/60">{{ user.role }}</p>
                  </div>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- LLM Selection -->
        <div>
          <label class="block text-sm font-medium text-base-content/70 mb-2">LLM Model</label>
          <div class="dropdown w-full">
            <div ref="llmDropdownTrigger"
                 tabindex="0" 
                 role="button"
                 class="btn btn-block justify-between h-14 text-left border-base-300 hover:border-primary/30 rounded-2xl">
              {{ selectedLlm || 'Select LLM Model' }}
              <span class="opacity-50">▼</span>
            </div>
            <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-2xl shadow-xl w-full p-2 z-50 border border-base-200">
              <li v-for="llm in llms" :key="llm">
                <a @click="selectLlm(llm)" class="rounded-xl py-3 px-4">{{ llm }}</a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Login Button -->
        <button 
          @click="login"
          :disabled="!selectedUser || !selectedLlm || loading"
          class="btn btn-primary btn-block h-14 text-base font-medium rounded-2xl mt-6 shadow-lg hover:shadow-xl transition-all active:scale-[0.985]">
          <span v-if="loading" class="loading loading-spinner"></span>
          Continue
        </button>
      </div>

      <p class="text-center text-xs text-base-content/50 mt-8">
        agnt3 • Internal Tool
      </p>
    </div>
  </div>
</template>

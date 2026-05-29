import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    function setUser(u) {
	user.value = u
	sessionStorage.setItem('user', JSON.stringify(u))
    }
    function loadUser() {
	const saved = sessionStorage.getItem('user')
	if (saved) user.value = JSON.parse(saved)
    }
    async function refreshUser() {
	const res = await fetch(`http://localhost:8001/users/${user.value.id}`)
	const u = await res.json()
	setUser(u)
	return u
    }
    return { user, setUser, loadUser, refreshUser }
})


export const useLlmStore = defineStore('llm', () => {
    const llm = ref(null)
    function setLlm(l) {
	llm.value = l
	sessionStorage.setItem('llm', l)
    }
    function loadLlm() {
	const saved = sessionStorage.getItem('llm')
	if (saved) llm.value = saved
    }
    return { llm, setLlm, loadLlm }
})

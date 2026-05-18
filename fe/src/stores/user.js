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
    return { user, setUser, loadUser }
})

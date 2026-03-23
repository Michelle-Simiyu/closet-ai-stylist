import { writable, derived } from 'svelte/store';
import { authApi, type User } from '$lib/api/client';

interface AuthState {
	user: User | null;
	token: string | null;
	loading: boolean;
	initialized: boolean;
}

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		token: null,
		loading: false,
		initialized: false,
	});

	return {
		subscribe,

		async init() {
			if (typeof window === 'undefined') return;
			const token = localStorage.getItem('token');
			if (!token) {
				update((s) => ({ ...s, initialized: true }));
				return;
			}
			update((s) => ({ ...s, token, loading: true }));
			try {
				const user = await authApi.me();
				update((s) => ({ ...s, user, loading: false, initialized: true }));
			} catch {
				localStorage.removeItem('token');
				update((s) => ({ ...s, token: null, loading: false, initialized: true }));
			}
		},

		async login(email: string, password: string) {
			update((s) => ({ ...s, loading: true }));
			const data = await authApi.login(email, password);
			localStorage.setItem('token', data.access_token);
			update((s) => ({
				...s,
				user: data.user,
				token: data.access_token,
				loading: false,
			}));
			return data;
		},

		async register(email: string, username: string, password: string) {
			update((s) => ({ ...s, loading: true }));
			const data = await authApi.register(email, username, password);
			localStorage.setItem('token', data.access_token);
			update((s) => ({
				...s,
				user: data.user,
				token: data.access_token,
				loading: false,
			}));
			return data;
		},

		logout() {
			localStorage.removeItem('token');
			set({ user: null, token: null, loading: false, initialized: true });
		},
	};
}

export const authStore = createAuthStore();
export const isAuthenticated = derived(authStore, ($s) => !!$s.user);
export const currentUser = derived(authStore, ($s) => $s.user);

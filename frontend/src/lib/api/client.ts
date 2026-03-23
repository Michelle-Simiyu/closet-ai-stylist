/**
 * API client for Closet AI backend.
 * All requests are authenticated via JWT stored in localStorage.
 */

const API_BASE = '/api/v1';

export interface ApiError {
	error: string;
	detail?: string;
	status_code: number;
}

class ApiClient {
	private getToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem('token');
	}

	private headers(extra: Record<string, string> = {}): Record<string, string> {
		const token = this.getToken();
		return {
			'Content-Type': 'application/json',
			...(token ? { Authorization: `Bearer ${token}` } : {}),
			...extra,
		};
	}

	private async handleResponse<T>(res: Response): Promise<T> {
		if (!res.ok) {
			let error: ApiError;
			try {
				error = await res.json();
			} catch {
				error = { error: res.statusText, status_code: res.status };
			}
			throw error;
		}
		if (res.status === 204) return undefined as T;
		return res.json();
	}

	async get<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
		const url = new URL(API_BASE + path, window.location.origin);
		if (params) {
			Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
		}
		const res = await fetch(url.toString(), { headers: this.headers() });
		return this.handleResponse<T>(res);
	}

	async post<T>(path: string, body?: unknown): Promise<T> {
		const res = await fetch(API_BASE + path, {
			method: 'POST',
			headers: this.headers(),
			body: body ? JSON.stringify(body) : undefined,
		});
		return this.handleResponse<T>(res);
	}

	async postForm<T>(path: string, formData: FormData): Promise<T> {
		const token = this.getToken();
		const res = await fetch(API_BASE + path, {
			method: 'POST',
			headers: token ? { Authorization: `Bearer ${token}` } : {},
			body: formData,
		});
		return this.handleResponse<T>(res);
	}

	async put<T>(path: string, body?: unknown): Promise<T> {
		const res = await fetch(API_BASE + path, {
			method: 'PUT',
			headers: this.headers(),
			body: body ? JSON.stringify(body) : undefined,
		});
		return this.handleResponse<T>(res);
	}

	async delete<T>(path: string): Promise<T> {
		const res = await fetch(API_BASE + path, {
			method: 'DELETE',
			headers: this.headers(),
		});
		return this.handleResponse<T>(res);
	}
}

export const api = new ApiClient();

// ---- Typed API Methods ----

export interface User {
	id: string;
	email: string;
	username: string;
	style_profile?: Record<string, unknown>;
	created_at: string;
}

export interface TokenResponse {
	access_token: string;
	token_type: string;
	user: User;
}

export interface ClothingItem {
	id: string;
	user_id: string;
	name: string;
	category: string;
	subcategory?: string;
	color: string;
	secondary_color?: string;
	style: string;
	pattern: string;
	formality: number;
	season: string;
	image_url?: string;
	brand?: string;
	notes?: string;
	times_worn: number;
	created_at: string;
	is_demo: boolean;
}

export interface ClothingItemCreate {
	name: string;
	category: string;
	color: string;
	secondary_color?: string;
	style: string;
	pattern: string;
	formality: number;
	season: string;
	image_url?: string;
	brand?: string;
	notes?: string;
}

export interface Outfit {
	id: string;
	user_id: string;
	name?: string;
	occasion: string;
	items: ClothingItem[];
	compatibility_score: number;
	liked: boolean;
	worn_count: number;
	created_at: string;
	is_saved: boolean;
	feedback: string[];
	description?: string;
}

export interface OutfitGenerationResponse {
	outfits: Outfit[];
	count: number;
	occasion: string;
	generation_time_ms: number;
}

export interface GenerateRequest {
	occasion: string;
	max_outfits?: number;
	weather?: string;
	temperature?: number;
}

export interface ClosetStats {
	total: number;
	categories: Record<string, number>;
	colors: Record<string, number>;
	styles: Record<string, number>;
	most_worn?: string;
}

export interface WeatherData {
	city: string;
	temperature_celsius: number;
	condition: string;
	season: string;
}

// Auth
export const authApi = {
	register: (email: string, username: string, password: string) =>
		api.post<TokenResponse>('/auth/register', { email, username, password }),

	login: async (email: string, password: string): Promise<TokenResponse> => {
		const form = new URLSearchParams();
		form.set('username', email);
		form.set('password', password);
		const res = await fetch('/api/v1/auth/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: form,
		});
		if (!res.ok) throw await res.json();
		return res.json();
	},

	me: () => api.get<User>('/auth/me'),

	saveQuiz: (quiz: Record<string, unknown>) => api.post('/auth/quiz', quiz),
};

// Closet
export const closetApi = {
	getAll: (params?: { category?: string; color?: string; include_demo?: boolean }) =>
		api.get<ClothingItem[]>('/closet', params as Record<string, string>),

	add: (item: ClothingItemCreate) => api.post<ClothingItem>('/closet', item),

	update: (id: string, item: Partial<ClothingItemCreate>) =>
		api.put<ClothingItem>(`/closet/${id}`, item),

	delete: (id: string) => api.delete<void>(`/closet/${id}`),

	loadDemo: () => api.post<ClothingItem[]>('/closet/demo'),

	stats: () => api.get<ClosetStats>('/closet/stats'),

	upload: async (file: File, removeBg = true): Promise<{ image_url: string; suggestions: Record<string, string> }> => {
		const form = new FormData();
		form.append('file', file);
		form.append('remove_bg', String(removeBg));
		return api.postForm(`/closet/upload?remove_bg=${removeBg}`, form);
	},
};

// Outfits
export const outfitsApi = {
	generate: (req: GenerateRequest) =>
		api.post<OutfitGenerationResponse>('/outfits/generate', req),

	saved: () => api.get<Outfit[]>('/outfits/saved'),

	save: (id: string) => api.post(`/outfits/${id}/save`),

	like: (id: string, liked: boolean) => api.post(`/outfits/${id}/like`, { liked }),
};

// Weather
export const weatherApi = {
	get: (city = 'New York') => api.get<WeatherData>('/weather', { city }),
};

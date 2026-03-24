/**
 * API client for Closet AI backend.
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
			try { error = await res.json(); }
			catch { error = { error: res.statusText, status_code: res.status }; }
			throw error;
		}
		if (res.status === 204) return undefined as T;
		return res.json();
	}

	async get<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
		const url = new URL(API_BASE + path, window.location.origin);
		if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
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

	async patch<T>(path: string, body?: unknown): Promise<T> {
		const res = await fetch(API_BASE + path, {
			method: 'PATCH',
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

// ---- Types ----

export interface User {
	id: string;
	email: string;
	username: string;
	style_profile?: Record<string, unknown>;
	gender?: string;
	country?: string;
	bio?: string;
	avatar_url?: string;
	closet_visibility: string;
	created_at: string;
}

export interface UserPublic {
	id: string;
	username: string;
	bio?: string;
	avatar_url?: string;
	closet_visibility: string;
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

export interface FriendshipRead {
	id: string;
	requester_id: string;
	addressee_id: string;
	status: string;
	created_at: string;
}

export interface ClosetRecommendationRead {
	id: string;
	from_user_id: string;
	to_user_id: string;
	item_id?: string;
	outfit_id?: string;
	message?: string;
	rec_type: string;
	created_at: string;
	is_read: boolean;
}

export interface FeedItem {
	id: string;
	name: string;
	category: string;
	color: string;
	style: string;
	image_url?: string;
	brand?: string;
}

export interface FeedEntry {
	user: {
		id: string;
		username: string;
		bio?: string;
		avatar_url?: string;
		country?: string;
		closet_visibility: string;
		created_at: string;
	};
	item_count: number;
	outfit_count: number;
	top_styles: string[];
	recent_items: FeedItem[];
	is_friend: boolean;
	has_pending_request: boolean;
}

export interface MarketplaceListing {
	id: string;
	user_id: string;
	item?: ClothingItem;
	price?: number;
	currency: string;
	description?: string;
	created_at: string;
}

export interface UserUpdate {
	username?: string;
	bio?: string;
	gender?: string;
	country?: string;
	avatar_url?: string;
	closet_visibility?: string;
}

// ---- Auth ----
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

// ---- Profile ----
export const profileApi = {
	update: (updates: UserUpdate) => api.patch<User>('/auth/profile', updates),
	changePassword: (current_password: string, new_password: string) =>
		api.post('/auth/change-password', { current_password, new_password }),
};

// ---- Closet ----
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
		return api.postForm(`/closet/upload?remove_bg=${removeBg}`, form);
	},
};

// ---- Outfits ----
export const outfitsApi = {
	generate: (req: GenerateRequest) =>
		api.post<OutfitGenerationResponse>('/outfits/generate', req),
	saved: () => api.get<Outfit[]>('/outfits/saved'),
	save: (id: string) => api.post(`/outfits/${id}/save`),
	like: (id: string, liked: boolean) => api.post(`/outfits/${id}/like`, { liked }),
};

// ---- Social ----
export const socialApi = {
	searchUsers: (q: string) => api.get<UserPublic[]>('/social/users/search', { q }),
	getUserProfile: (id: string) => api.get<UserPublic>(`/social/users/${id}`),
	getFriendCloset: (id: string) => api.get<ClothingItem[]>(`/social/users/${id}/closet`),
	getFriendOutfits: (id: string) => api.get<unknown[]>(`/social/users/${id}/outfits`),

	getFriends: () => api.get<UserPublic[]>('/social/friends'),
	getRequests: () => api.get<FriendshipRead[]>('/social/friends/requests'),
	getSentRequests: () => api.get<FriendshipRead[]>('/social/friends/sent'),
	sendFriendRequest: (userId: string) => api.post(`/social/friends/${userId}`),
	acceptRequest: (friendshipId: string) => api.post(`/social/friends/accept/${friendshipId}`),
	removeFriend: (userId: string) => api.delete(`/social/friends/${userId}`),

	getMarketplace: () => api.get<MarketplaceListing[]>('/social/marketplace'),
	listForSale: (data: { item_id: string; price?: number; currency?: string; description?: string }) =>
		api.post('/social/marketplace', data),
	markSold: (listingId: string) => api.patch(`/social/marketplace/${listingId}/sold`),
	removeListing: (listingId: string) => api.delete(`/social/marketplace/${listingId}`),

	getFeed: (params?: { style?: string; country?: string; limit?: number; offset?: number }) =>
		api.get<FeedEntry[]>('/social/feed', params as Record<string, string | number | boolean>),

	getRecommendations: () => api.get<ClosetRecommendationRead[]>('/social/recommendations'),
	sendRecommendation: (data: {
		to_user_id: string;
		item_id?: string;
		outfit_id?: string;
		message?: string;
		rec_type?: string;
	}) => api.post('/social/recommendations', data),
	markRecommendationRead: (id: string) => api.post(`/social/recommendations/${id}/read`),
};

// ---- Weather ----
export const weatherApi = {
	get: (city = 'New York') => api.get<WeatherData>('/weather', { city }),
};

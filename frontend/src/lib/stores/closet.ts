import { writable, derived } from 'svelte/store';
import { closetApi, type ClothingItem, type ClothingItemCreate, type ClosetStats } from '$lib/api/client';

interface ClosetState {
	items: ClothingItem[];
	loading: boolean;
	error: string | null;
	stats: ClosetStats | null;
}

function createClosetStore() {
	const { subscribe, set, update } = writable<ClosetState>({
		items: [],
		loading: false,
		error: null,
		stats: null,
	});

	return {
		subscribe,

		async load(params?: { category?: string; color?: string }) {
			update((s) => ({ ...s, loading: true, error: null }));
			try {
				const items = await closetApi.getAll({ ...params, include_demo: true });
				update((s) => ({ ...s, items, loading: false }));
			} catch (err: unknown) {
				const msg = (err as { detail?: string; error?: string })?.detail || 'Failed to load closet';
				update((s) => ({ ...s, loading: false, error: msg }));
			}
		},

		async add(item: ClothingItemCreate): Promise<ClothingItem> {
			const newItem = await closetApi.add(item);
			update((s) => ({ ...s, items: [...s.items, newItem] }));
			return newItem;
		},

		async update(id: string, data: Partial<ClothingItemCreate>): Promise<ClothingItem> {
			const updated = await closetApi.update(id, data);
			update((s) => ({
				...s,
				items: s.items.map((item) => (item.id === id ? updated : item)),
			}));
			return updated;
		},

		async remove(id: string) {
			await closetApi.delete(id);
			update((s) => ({ ...s, items: s.items.filter((i) => i.id !== id) }));
		},

		async loadDemo() {
			update((s) => ({ ...s, loading: true, error: null }));
			try {
				const demoItems = await closetApi.loadDemo();
				update((s) => ({
					...s,
					loading: false,
					items: [...s.items.filter((i) => !i.is_demo), ...demoItems],
				}));
				return demoItems;
			} catch (err: unknown) {
				const msg = (err as { detail?: string })?.detail || 'Failed to load demo';
				update((s) => ({ ...s, loading: false, error: msg }));
				throw err;
			}
		},

		async loadStats() {
			try {
				const stats = await closetApi.stats();
				update((s) => ({ ...s, stats }));
			} catch {
				// non-critical
			}
		},

		clear() {
			set({ items: [], loading: false, error: null, stats: null });
		},
	};
}

export const closetStore = createClosetStore();

// Derived: items by category
export const itemsByCategory = derived(closetStore, ($store) => {
	const grouped: Record<string, ClothingItem[]> = {};
	for (const item of $store.items) {
		if (!grouped[item.category]) grouped[item.category] = [];
		grouped[item.category].push(item);
	}
	return grouped;
});

// Derived: item count
export const itemCount = derived(closetStore, ($store) => $store.items.length);

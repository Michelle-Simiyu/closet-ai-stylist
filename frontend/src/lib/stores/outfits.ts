import { writable } from 'svelte/store';
import { outfitsApi, type Outfit, type GenerateRequest, weatherApi, type WeatherData } from '$lib/api/client';

interface OutfitsState {
	generated: Outfit[];
	saved: Outfit[];
	loading: boolean;
	error: string | null;
	lastGenerationMs: number | null;
	weather: WeatherData | null;
}

function createOutfitsStore() {
	const { subscribe, set, update } = writable<OutfitsState>({
		generated: [],
		saved: [],
		loading: false,
		error: null,
		lastGenerationMs: null,
		weather: null,
	});

	return {
		subscribe,

		async generate(req: GenerateRequest): Promise<Outfit[]> {
			update((s) => ({ ...s, loading: true, error: null }));
			try {
				const result = await outfitsApi.generate(req);
				update((s) => ({
					...s,
					generated: result.outfits,
					loading: false,
					lastGenerationMs: result.generation_time_ms,
				}));
				return result.outfits;
			} catch (err: unknown) {
				const msg = (err as { detail?: string; error?: string })?.detail || 'Generation failed';
				update((s) => ({ ...s, loading: false, error: msg }));
				throw err;
			}
		},

		async loadSaved() {
			try {
				const saved = await outfitsApi.saved();
				update((s) => ({ ...s, saved }));
			} catch {
				// non-critical
			}
		},

		async like(outfitId: string, liked: boolean) {
			await outfitsApi.like(outfitId, liked);
			update((s) => ({
				...s,
				generated: s.generated.map((o) => (o.id === outfitId ? { ...o, liked } : o)),
				saved: s.saved.map((o) => (o.id === outfitId ? { ...o, liked } : o)),
			}));
		},

		async save(outfitId: string) {
			await outfitsApi.save(outfitId);
			update((s) => ({
				...s,
				generated: s.generated.map((o) =>
					o.id === outfitId ? { ...o, is_saved: true } : o
				),
			}));
		},

		async loadWeather(city = 'New York') {
			try {
				const weather = await weatherApi.get(city);
				update((s) => ({ ...s, weather }));
			} catch {
				// non-critical
			}
		},

		clearGenerated() {
			update((s) => ({ ...s, generated: [] }));
		},
	};
}

export const outfitsStore = createOutfitsStore();

/**
 * PostHog analytics integration.
 * All tracking calls are no-ops if PostHog is not configured.
 */

let posthog: { capture: (event: string, props?: Record<string, unknown>) => void } | null = null;

export function initAnalytics(apiKey: string) {
	if (!apiKey || typeof window === 'undefined') return;
	import('posthog-js').then(({ default: ph }) => {
		ph.init(apiKey, { api_host: 'https://app.posthog.com' });
		posthog = ph;
	});
}

function track(event: string, properties?: Record<string, unknown>) {
	try {
		posthog?.capture(event, properties);
	} catch {
		// analytics must never break the app
	}
}

export const analytics = {
	userSignedUp: (method: 'email' | 'demo' = 'email') =>
		track('user_signed_up', { method }),

	itemAdded: (category: string) =>
		track('item_added', { category }),

	outfitGenerated: (count: number, occasion: string) =>
		track('outfit_generated', { count, occasion }),

	outfitLiked: (outfitId: string, score: number) =>
		track('outfit_liked', { outfit_id: outfitId, score }),

	outfitSaved: (outfitId: string) =>
		track('outfit_saved', { outfit_id: outfitId }),

	outfitShared: (outfitId: string) =>
		track('outfit_shared', { outfit_id: outfitId }),

	imageUploaded: () =>
		track('image_uploaded'),

	demoLoaded: () =>
		track('demo_loaded'),

	pageView: (page: string) =>
		track('page_view', { page }),
};

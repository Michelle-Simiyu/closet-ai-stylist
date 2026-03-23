<script lang="ts">
	import { goto } from '$app/navigation';
	import StyleQuiz from '$lib/components/StyleQuiz.svelte';
	import { closetStore } from '$lib/stores/closet';
	import { analytics } from '$lib/utils/analytics';

	let step: 'quiz' | 'demo' = 'quiz';

	async function handleQuizComplete() {
		step = 'demo';
	}

	async function loadDemoAndContinue() {
		await closetStore.loadDemo();
		analytics.demoLoaded();
		goto('/closet');
	}

	function skipDemo() {
		goto('/closet');
	}
</script>

<svelte:head><title>Setup — Closet AI</title></svelte:head>

<div class="max-w-lg mx-auto py-8 animate-fade-in">
	{#if step === 'quiz'}
		<div class="text-center mb-8">
			<h1 class="text-2xl font-bold text-gray-900">Tell us about your style</h1>
			<p class="text-gray-500 mt-1">Help us personalize your outfit recommendations</p>
		</div>
		<StyleQuiz on:complete={handleQuizComplete} />

	{:else}
		<div class="text-center">
			<div class="text-6xl mb-4">🎉</div>
			<h1 class="text-2xl font-bold text-gray-900 mb-2">You're all set!</h1>
			<p class="text-gray-500 mb-8">
				Want to see the magic? Load a demo wardrobe and generate your first outfits instantly.
			</p>

			<div class="card p-6 text-left mb-6">
				<h2 class="font-semibold text-gray-900 mb-3">🧺 Demo Wardrobe includes:</h2>
				<ul class="space-y-2 text-sm text-gray-600">
					<li>✓ 10 pre-styled clothing items</li>
					<li>✓ Mixed categories: tops, bottoms, outerwear, shoes</li>
					<li>✓ Range of styles: casual, formal, minimalist</li>
					<li>✓ Ready to generate outfits immediately</li>
				</ul>
			</div>

			<div class="flex flex-col sm:flex-row gap-3 justify-center">
				<button class="btn-primary px-6" on:click={loadDemoAndContinue}>
					Load Demo Wardrobe 🚀
				</button>
				<button class="btn-secondary px-6" on:click={skipDemo}>
					Start with my own items
				</button>
			</div>
		</div>
	{/if}
</div>

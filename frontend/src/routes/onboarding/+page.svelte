<script lang="ts">
	import { goto } from '$app/navigation';
	import StyleQuiz from '$lib/components/StyleQuiz.svelte';
	import { closetStore } from '$lib/stores/closet';
	import { analytics } from '$lib/utils/analytics';

	type Stage = 'welcome' | 'quiz' | 'demo';
	let stage: Stage = 'welcome';
	let demoLoading = false;

	function startQuiz() {
		stage = 'quiz';
	}

	function handleQuizComplete() {
		stage = 'demo';
	}

	async function loadDemoAndContinue() {
		demoLoading = true;
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

	<!-- ── Stage 1: Welcome ─────────────────────────────────────────── -->
	{#if stage === 'welcome'}
		<div class="text-center mb-10">
			<div class="text-5xl mb-4">✨</div>
			<h1 class="text-3xl font-bold text-gray-900">Welcome to Closet AI</h1>
			<p class="text-gray-500 mt-2 text-base max-w-sm mx-auto">
				Your personal AI stylist. Let's set up your style profile so every recommendation is made for <span class="font-semibold text-primary-600">you</span>.
			</p>
		</div>

		<!-- What we'll ask -->
		<div class="card p-5 mb-6">
			<h2 class="font-semibold text-gray-900 mb-4 text-sm uppercase tracking-wide text-gray-500">What we'll cover</h2>
			<div class="space-y-3">
				{#each [
					{ emoji: '🪪', title: 'Identity & location', desc: 'Gender and country for personalised, weather-aware suggestions' },
					{ emoji: '🎨', title: 'Style preferences', desc: 'Your aesthetic, colour palette, and formality level' },
					{ emoji: '💳', title: 'Budget & shopping habits', desc: 'Price range and how often you refresh your wardrobe' },
					{ emoji: '✂️', title: 'Fit & values', desc: 'How clothes should feel and your stance on sustainability' },
				] as item}
					<div class="flex items-start gap-3">
						<span class="text-xl mt-0.5">{item.emoji}</span>
						<div>
							<div class="text-sm font-medium text-gray-900">{item.title}</div>
							<div class="text-xs text-gray-500 mt-0.5">{item.desc}</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<div class="text-center space-y-3">
			<button class="btn-primary px-8 py-3 text-base w-full" on:click={startQuiz}>
				Get started →
			</button>
			<button class="text-sm text-gray-400 hover:text-gray-600 transition-colors" on:click={skipDemo}>
				Skip setup — I'll configure this later
			</button>
		</div>

	<!-- ── Stage 2: Style quiz ──────────────────────────────────────── -->
	{:else if stage === 'quiz'}
		<div class="text-center mb-6">
			<h1 class="text-xl font-bold text-gray-900">Your Style Profile</h1>
			<p class="text-gray-500 text-sm mt-1">10 quick questions · All answers can be updated later in Settings</p>
		</div>
		<StyleQuiz on:complete={handleQuizComplete} />

	<!-- ── Stage 3: Demo wardrobe ───────────────────────────────────── -->
	{:else}
		<div class="text-center">
			<div class="text-6xl mb-4">🎉</div>
			<h1 class="text-2xl font-bold text-gray-900 mb-1">Style profile saved!</h1>
			<p class="text-gray-500 mb-6 text-sm">
				Your AI stylist is ready. One last thing — would you like a demo wardrobe to see the magic right away?
			</p>

			<div class="card p-5 text-left mb-5">
				<div class="flex items-center gap-2 mb-3">
					<span class="text-lg">🧺</span>
					<h2 class="font-semibold text-gray-900">Demo wardrobe includes</h2>
				</div>
				<ul class="space-y-2.5 text-sm text-gray-600">
					<li class="flex items-start gap-2">
						<span class="text-green-500 mt-0.5 font-bold">✓</span>
						<span>15 pre-styled clothing items across all categories</span>
					</li>
					<li class="flex items-start gap-2">
						<span class="text-green-500 mt-0.5 font-bold">✓</span>
						<span>Tops, bottoms, outerwear, shoes, and accessories</span>
					</li>
					<li class="flex items-start gap-2">
						<span class="text-green-500 mt-0.5 font-bold">✓</span>
						<span>Mix of casual, formal, and minimalist pieces</span>
					</li>
					<li class="flex items-start gap-2">
						<span class="text-green-500 mt-0.5 font-bold">✓</span>
						<span>Ready to generate AI outfit recommendations instantly</span>
					</li>
				</ul>
				<p class="text-xs text-gray-400 mt-3">Demo items are clearly marked and can be removed at any time.</p>
			</div>

			<div class="flex flex-col sm:flex-row gap-3">
				<button
					class="btn-primary flex-1 py-3 text-base flex items-center justify-center gap-2"
					disabled={demoLoading}
					on:click={loadDemoAndContinue}
				>
					{#if demoLoading}
						<span class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
						Loading…
					{:else}
						🚀 Load demo wardrobe
					{/if}
				</button>
				<button class="btn-secondary flex-1 py-3 text-base" on:click={skipDemo}>
					Start with my own items
				</button>
			</div>
		</div>
	{/if}

</div>

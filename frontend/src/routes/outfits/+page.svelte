<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Sparkles, RefreshCw, CloudSun, ChevronDown } from 'lucide-svelte';
	import { closetStore } from '$lib/stores/closet';
	import { outfitsStore } from '$lib/stores/outfits';
	import { isAuthenticated } from '$lib/stores/auth';
	import OutfitCard from '$lib/components/OutfitCard.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import { analytics } from '$lib/utils/analytics';

	let occasion = 'casual';
	let maxOutfits = 5;
	let toast = '';

	const occasions = [
		{ value: 'casual', label: 'Casual', emoji: '😊' },
		{ value: 'work', label: 'Work', emoji: '💼' },
		{ value: 'formal', label: 'Formal', emoji: '🎩' },
		{ value: 'party', label: 'Party', emoji: '🎉' },
		{ value: 'date', label: 'Date Night', emoji: '❤️' },
	];

	$: weather = $outfitsStore.weather;
	$: hasItems = $closetStore.items.length >= 2;

	onMount(async () => {
		if (!$isAuthenticated) { goto('/'); return; }
		await closetStore.load();
		await outfitsStore.loadWeather();
		// Auto-generate if closet has items
		if ($closetStore.items.length >= 2 && $outfitsStore.generated.length === 0) {
			handleGenerate();
		}
	});

	async function handleGenerate() {
		if (!hasItems) return;
		await outfitsStore.generate({
			occasion,
			max_outfits: maxOutfits,
			temperature: weather?.temperature_celsius,
		});
		analytics.outfitGenerated($outfitsStore.generated.length, occasion);
	}

	async function handleLike(e: CustomEvent<{ id: string; liked: boolean }>) {
		await outfitsStore.like(e.detail.id, e.detail.liked);
		if (e.detail.liked) {
			analytics.outfitLiked(e.detail.id, $outfitsStore.generated.find((o) => o.id === e.detail.id)?.compatibility_score ?? 0);
		}
	}

	async function handleSave(e: CustomEvent<string>) {
		await outfitsStore.save(e.detail);
		analytics.outfitSaved(e.detail);
		showToast('Outfit saved! ✨');
	}

	function handleShare(e: CustomEvent<string>) {
		analytics.outfitShared(e.detail);
		// Simple share: copy URL
		const url = `${window.location.origin}/outfits/saved`;
		navigator.clipboard?.writeText(url);
		showToast('Link copied! 📋');
	}

	function showToast(msg: string) {
		toast = msg;
		setTimeout(() => (toast = ''), 3000);
	}
</script>

<svelte:head><title>Outfit Generator — Closet AI</title></svelte:head>

<!-- Toast -->
{#if toast}
	<div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-gray-900 text-white text-sm px-4 py-2.5 rounded-xl shadow-lg animate-slide-up">
		{toast}
	</div>
{/if}

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-start justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">AI Outfit Generator</h1>
			<p class="text-sm text-gray-500 mt-0.5">
				Smart combinations from your {$closetStore.items.length} item{$closetStore.items.length !== 1 ? 's' : ''}
			</p>
		</div>

		{#if weather}
			<div class="card px-3 py-2 flex items-center gap-2 text-sm">
				<CloudSun size={16} class="text-amber-500" />
				<span class="text-gray-600">{weather.city}</span>
				<span class="font-medium">{weather.temperature_celsius}°C</span>
			</div>
		{/if}
	</div>

	<!-- Controls -->
	<div class="card p-4 space-y-4">
		<!-- Occasion selector -->
		<div>
			<p class="text-sm font-medium text-gray-700 mb-2">Occasion</p>
			<div class="flex gap-2 flex-wrap">
				{#each occasions as occ}
					<button
						class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all"
						class:bg-primary-600={occasion === occ.value}
						class:text-white={occasion === occ.value}
						class:border-primary-600={occasion === occ.value}
						class:border-gray-200={occasion !== occ.value}
						class:text-gray-600={occasion !== occ.value}
						class:hover:border-gray-300={occasion !== occ.value}
						on:click={() => (occasion = occ.value)}
					>
						{occ.emoji} {occ.label}
					</button>
				{/each}
			</div>
		</div>

		<!-- Max outfits -->
		<div class="flex items-center justify-between">
			<label class="text-sm font-medium text-gray-700" for="maxOutfits">
				Max outfits: <span class="text-primary-600">{maxOutfits}</span>
			</label>
			<input
				type="range"
				id="maxOutfits"
				min="1"
				max="10"
				bind:value={maxOutfits}
				class="w-32 accent-primary-600"
			/>
		</div>

		<!-- Generate button -->
		{#if !hasItems}
			<div class="bg-amber-50 text-amber-700 rounded-xl px-4 py-3 text-sm">
				Add at least 2 items to your closet to generate outfits.
				<a href="/closet" class="font-medium underline ml-1">Go to Closet →</a>
			</div>
		{:else}
			<button
				class="btn-primary w-full text-base py-3"
				on:click={handleGenerate}
				disabled={$outfitsStore.loading}
			>
				{#if $outfitsStore.loading}
					<LoadingSpinner size="sm" />
					Generating outfits…
				{:else}
					<Sparkles size={18} />
					Generate Outfits
				{/if}
			</button>
		{/if}
	</div>

	<!-- Results -->
	{#if $outfitsStore.loading && $outfitsStore.generated.length === 0}
		<div class="flex items-center justify-center py-16">
			<div class="text-center">
				<div class="text-4xl mb-4 animate-pulse-slow">✨</div>
				<LoadingSpinner size="lg" label="Styling your outfits…" />
			</div>
		</div>

	{:else if $outfitsStore.error}
		<div class="card p-8 text-center">
			<p class="text-red-500 mb-3">{$outfitsStore.error}</p>
			<button class="btn-secondary" on:click={handleGenerate}>Try Again</button>
		</div>

	{:else if $outfitsStore.generated.length > 0}
		<div class="flex items-center justify-between">
			<p class="text-sm text-gray-500">
				{$outfitsStore.generated.length} outfit{$outfitsStore.generated.length !== 1 ? 's' : ''} generated
				{#if $outfitsStore.lastGenerationMs}
					in {Math.round($outfitsStore.lastGenerationMs)}ms
				{/if}
			</p>
			<button class="btn-ghost text-sm" on:click={handleGenerate}>
				<RefreshCw size={14} />
				Regenerate
			</button>
		</div>

		<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each $outfitsStore.generated as outfit, i (outfit.id)}
				<OutfitCard
					{outfit}
					index={i}
					on:like={handleLike}
					on:save={handleSave}
					on:share={handleShare}
				/>
			{/each}
		</div>
	{/if}
</div>

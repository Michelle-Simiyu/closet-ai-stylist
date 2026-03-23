<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Bookmark, Sparkles } from 'lucide-svelte';
	import { closetStore } from '$lib/stores/closet';
	import { outfitsStore } from '$lib/stores/outfits';
	import { isAuthenticated } from '$lib/stores/auth';
	import OutfitCard from '$lib/components/OutfitCard.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

	let loading = true;
	let toast = '';

	onMount(async () => {
		if (!$isAuthenticated) { goto('/'); return; }
		await closetStore.load();
		await outfitsStore.loadSaved();
		loading = false;
	});

	async function handleLike(e: CustomEvent<{ id: string; liked: boolean }>) {
		await outfitsStore.like(e.detail.id, e.detail.liked);
	}

	function showToast(msg: string) {
		toast = msg;
		setTimeout(() => (toast = ''), 3000);
	}
</script>

<svelte:head><title>Saved Outfits — Closet AI</title></svelte:head>

{#if toast}
	<div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-gray-900 text-white text-sm px-4 py-2.5 rounded-xl shadow-lg animate-slide-up">
		{toast}
	</div>
{/if}

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
			<Bookmark size={22} class="text-primary-600" />
			Saved Outfits
		</h1>
		<p class="text-sm text-gray-500 mt-0.5">Your favourite combinations</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-16">
			<LoadingSpinner size="lg" label="Loading saved outfits…" />
		</div>

	{:else if $outfitsStore.saved.length === 0}
		<div class="card p-12 text-center">
			<div class="text-5xl mb-4">🗂️</div>
			<h2 class="text-lg font-semibold text-gray-900 mb-2">No saved outfits yet</h2>
			<p class="text-gray-500 mb-6 text-sm">
				Generate outfits and save the ones you love here.
			</p>
			<a href="/outfits" class="btn-primary inline-flex items-center gap-2">
				<Sparkles size={14} />
				Generate Outfits
			</a>
		</div>

	{:else}
		<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each $outfitsStore.saved as outfit, i (outfit.id)}
				<OutfitCard
					{outfit}
					index={i}
					on:like={handleLike}
					on:save={() => {}}
					on:share={() => showToast('Link copied! 📋')}
				/>
			{/each}
		</div>
	{/if}
</div>

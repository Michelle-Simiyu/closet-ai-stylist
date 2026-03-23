<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Plus, Grid3X3, List, Filter, BarChart2, Sparkles, Download } from 'lucide-svelte';
	import { closetStore, itemsByCategory } from '$lib/stores/closet';
	import { authStore, isAuthenticated } from '$lib/stores/auth';
	import ClosetItem from '$lib/components/ClosetItem.svelte';
	import UploadModal from '$lib/components/UploadModal.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import { analytics } from '$lib/utils/analytics';
	import type { ClothingItem, ClothingItemCreate } from '$lib/api/client';

	let viewMode: 'grid' | 'list' = 'grid';
	let showUploadModal = false;
	let filterCategory = 'all';
	let loadingDemo = false;
	let toast = '';

	const categories = ['all', 'top', 'bottom', 'dress', 'shoes', 'outerwear', 'accessory'];

	$: filteredItems = filterCategory === 'all'
		? $closetStore.items
		: $closetStore.items.filter((i) => i.category === filterCategory);

	onMount(async () => {
		if (!$isAuthenticated) { goto('/'); return; }
		await closetStore.load();
		await closetStore.loadStats();
	});

	async function handleSaveItem(event: CustomEvent<ClothingItemCreate>) {
		const item = await closetStore.add(event.detail);
		analytics.itemAdded(item.category);
		showUploadModal = false;
		showToast('Item added to your closet! 🎉');
	}

	async function handleDelete(event: CustomEvent<string>) {
		if (!confirm('Delete this item?')) return;
		await closetStore.remove(event.detail);
		showToast('Item removed');
	}

	async function handleLoadDemo() {
		loadingDemo = true;
		await closetStore.loadDemo();
		loadingDemo = false;
		analytics.demoLoaded();
		showToast('Demo wardrobe loaded! 🛍️');
	}

	function showToast(msg: string) {
		toast = msg;
		setTimeout(() => (toast = ''), 3000);
	}

	function goToOutfits() {
		goto('/outfits');
	}
</script>

<svelte:head><title>My Closet — Closet AI</title></svelte:head>

<!-- Toast -->
{#if toast}
	<div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-gray-900 text-white text-sm px-4 py-2.5 rounded-xl shadow-lg animate-slide-up">
		{toast}
	</div>
{/if}

<UploadModal open={showUploadModal} on:close={() => (showUploadModal = false)} on:saved={handleSaveItem} />

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">My Closet</h1>
			<p class="text-sm text-gray-500 mt-0.5">
				{$closetStore.items.length} item{$closetStore.items.length !== 1 ? 's' : ''}
			</p>
		</div>

		<div class="flex items-center gap-2 flex-wrap">
			{#if $closetStore.items.length === 0}
				<button class="btn-secondary text-sm" on:click={handleLoadDemo} disabled={loadingDemo}>
					{#if loadingDemo}
						<LoadingSpinner size="sm" />
						Loading…
					{:else}
						<Download size={14} />
						Load Demo
					{/if}
				</button>
			{/if}

			{#if $closetStore.items.length >= 2}
				<button class="btn-primary text-sm" on:click={goToOutfits}>
					<Sparkles size={14} />
					Generate Outfits
				</button>
			{/if}

			<button class="btn-primary text-sm" on:click={() => (showUploadModal = true)}>
				<Plus size={14} />
				Add Item
			</button>
		</div>
	</div>

	<!-- Stats bar -->
	{#if $closetStore.stats && $closetStore.stats.total > 0}
		<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
			{#each Object.entries($closetStore.stats.categories).slice(0, 4) as [cat, count]}
				<div class="card p-3 text-center">
					<div class="text-2xl font-bold text-primary-600">{count}</div>
					<div class="text-xs text-gray-500 mt-0.5 capitalize">{cat}s</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Filters + view toggle -->
	<div class="flex items-center justify-between gap-3 flex-wrap">
		<div class="flex items-center gap-1.5 overflow-x-auto pb-1">
			{#each categories as cat}
				<button
					class="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all"
					class:bg-primary-600={filterCategory === cat}
					class:text-white={filterCategory === cat}
					class:bg-gray-100={filterCategory !== cat}
					class:text-gray-600={filterCategory !== cat}
					on:click={() => (filterCategory = cat)}
				>
					{cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1)}
					{#if cat !== 'all'}
						<span class="ml-1 opacity-70">
							({$closetStore.items.filter((i) => i.category === cat).length})
						</span>
					{/if}
				</button>
			{/each}
		</div>

		<div class="flex items-center gap-1">
			<button
				class="p-2 rounded-lg transition-colors"
				class:bg-primary-50={viewMode === 'grid'}
				class:text-primary-600={viewMode === 'grid'}
				class:text-gray-400={viewMode !== 'grid'}
				on:click={() => (viewMode = 'grid')}
			>
				<Grid3X3 size={16} />
			</button>
			<button
				class="p-2 rounded-lg transition-colors"
				class:bg-primary-50={viewMode === 'list'}
				class:text-primary-600={viewMode === 'list'}
				class:text-gray-400={viewMode !== 'list'}
				on:click={() => (viewMode = 'list')}
			>
				<List size={16} />
			</button>
		</div>
	</div>

	<!-- Items -->
	{#if $closetStore.loading}
		<div class="flex items-center justify-center py-16">
			<LoadingSpinner size="lg" label="Loading your closet…" />
		</div>

	{:else if $closetStore.error}
		<div class="card p-8 text-center">
			<p class="text-red-500 mb-3">{$closetStore.error}</p>
			<button class="btn-secondary" on:click={() => closetStore.load()}>Try Again</button>
		</div>

	{:else if filteredItems.length === 0}
		<div class="card p-12 text-center">
			<div class="text-5xl mb-4">👚</div>
			<h2 class="text-lg font-semibold text-gray-900 mb-2">
				{filterCategory !== 'all' ? `No ${filterCategory}s yet` : 'Your closet is empty'}
			</h2>
			<p class="text-gray-500 mb-6 text-sm">
				{filterCategory !== 'all'
					? `Add your first ${filterCategory} to get started`
					: 'Add clothing items or load the demo wardrobe to try the AI stylist'}
			</p>
			<div class="flex gap-3 justify-center flex-wrap">
				<button class="btn-primary" on:click={() => (showUploadModal = true)}>
					<Plus size={14} />
					Add Item
				</button>
				{#if filterCategory === 'all'}
					<button class="btn-secondary" on:click={handleLoadDemo}>
						<Download size={14} />
						Load Demo
					</button>
				{/if}
			</div>
		</div>

	{:else}
		<div
			class:grid={viewMode === 'grid'}
			class:grid-cols-2={viewMode === 'grid'}
			class:sm:grid-cols-3={viewMode === 'grid'}
			class:md:grid-cols-4={viewMode === 'grid'}
			class:lg:grid-cols-5={viewMode === 'grid'}
			class:gap-3={viewMode === 'grid'}
			class:space-y-2={viewMode === 'list'}
		>
			{#each filteredItems as item (item.id)}
				<ClosetItem
					{item}
					on:edit={(e) => { /* TODO: edit modal */ }}
					on:delete={handleDelete}
				/>
			{/each}
		</div>
	{/if}
</div>

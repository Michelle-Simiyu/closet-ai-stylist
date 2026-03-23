<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Pencil, Trash2, Star } from 'lucide-svelte';
	import type { ClothingItem } from '$lib/api/client';

	export let item: ClothingItem;
	export let selectable = false;
	export let selected = false;

	const dispatch = createEventDispatcher<{
		edit: ClothingItem;
		delete: string;
		select: ClothingItem;
	}>();

	const categoryColors: Record<string, string> = {
		top: 'bg-blue-100 text-blue-700',
		bottom: 'bg-green-100 text-green-700',
		dress: 'bg-pink-100 text-pink-700',
		shoes: 'bg-orange-100 text-orange-700',
		outerwear: 'bg-purple-100 text-purple-700',
		accessory: 'bg-yellow-100 text-yellow-700',
	};

	$: badgeClass = categoryColors[item.category] ?? 'bg-gray-100 text-gray-600';
	$: formalityStars = Array.from({ length: 5 }, (_, i) => i < item.formality);

	function handleClick() {
		if (selectable) dispatch('select', item);
	}
</script>

<div
	class="card overflow-hidden transition-all duration-200 hover:shadow-md group"
	class:ring-2={selected}
	class:ring-primary-500={selected}
	class:cursor-pointer={selectable}
	on:click={handleClick}
	on:keydown={(e) => e.key === 'Enter' && handleClick()}
	role={selectable ? 'button' : 'article'}
	tabindex={selectable ? 0 : undefined}
>
	<!-- Image -->
	<div class="relative aspect-square bg-gray-50 overflow-hidden">
		{#if item.image_url && !item.image_url.startsWith('data:')}
			<img
				src={item.image_url}
				alt={item.name}
				class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
				loading="lazy"
			/>
		{:else if item.image_url?.startsWith('data:')}
			<img
				src={item.image_url}
				alt={item.name}
				class="w-full h-full object-contain p-2"
			/>
		{:else}
			<div class="w-full h-full flex items-center justify-center">
				<span class="text-5xl select-none">
					{#if item.category === 'top'}👕{:else if item.category === 'bottom'}👖{:else if item.category === 'dress'}👗{:else if item.category === 'shoes'}👟{:else if item.category === 'outerwear'}🧥{:else}💍{/if}
				</span>
			</div>
		{/if}

		<!-- Selected overlay -->
		{#if selected}
			<div class="absolute inset-0 bg-primary-600/10 flex items-center justify-center">
				<div class="rounded-full bg-primary-600 text-white p-1">
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
				</div>
			</div>
		{/if}

		<!-- Actions overlay -->
		{#if !selectable}
			<div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-start justify-end p-2 gap-1 opacity-0 group-hover:opacity-100">
				<button
					class="p-1.5 bg-white rounded-lg shadow text-gray-600 hover:text-primary-600 transition-colors"
					on:click|stopPropagation={() => dispatch('edit', item)}
					title="Edit item"
				>
					<Pencil size={14} />
				</button>
				<button
					class="p-1.5 bg-white rounded-lg shadow text-gray-600 hover:text-red-600 transition-colors"
					on:click|stopPropagation={() => dispatch('delete', item.id)}
					title="Delete item"
				>
					<Trash2 size={14} />
				</button>
			</div>
		{/if}

		<!-- Demo badge -->
		{#if item.is_demo}
			<div class="absolute top-2 left-2">
				<span class="badge bg-amber-100 text-amber-700 text-[10px]">Demo</span>
			</div>
		{/if}
	</div>

	<!-- Info -->
	<div class="p-3">
		<div class="flex items-start justify-between gap-1">
			<p class="text-sm font-medium text-gray-900 truncate flex-1" title={item.name}>
				{item.name}
			</p>
		</div>

		<div class="mt-1.5 flex items-center gap-1.5 flex-wrap">
			<span class="badge text-[10px] {badgeClass}">{item.category}</span>

			<!-- Color dot -->
			<span class="inline-flex items-center gap-1 text-[10px] text-gray-500">
				<span class="w-2.5 h-2.5 rounded-full border border-gray-200 inline-block"
					style="background-color: {item.color}"
				/>
				{item.color}
			</span>
		</div>

		<!-- Formality stars -->
		<div class="mt-1.5 flex items-center gap-0.5" title="Formality: {item.formality}/5">
			{#each formalityStars as filled}
				<Star
					size={10}
					class={filled ? 'text-amber-400 fill-amber-400' : 'text-gray-200 fill-gray-200'}
				/>
			{/each}
		</div>
	</div>
</div>

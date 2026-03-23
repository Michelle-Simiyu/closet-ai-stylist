<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Heart, Bookmark, Share2, ChevronDown, ChevronUp } from 'lucide-svelte';
	import type { Outfit } from '$lib/api/client';

	export let outfit: Outfit;
	export let index = 0;

	const dispatch = createEventDispatcher<{
		like: { id: string; liked: boolean };
		save: string;
		share: string;
	}>();

	let expanded = false;

	$: scoreColor =
		outfit.compatibility_score >= 80
			? 'text-green-600'
			: outfit.compatibility_score >= 60
				? 'text-amber-600'
				: 'text-red-500';

	$: scoreRing =
		outfit.compatibility_score >= 80
			? 'stroke-green-500'
			: outfit.compatibility_score >= 60
				? 'stroke-amber-500'
				: 'stroke-red-400';

	$: circumference = 2 * Math.PI * 20;
	$: dashOffset = circumference - (outfit.compatibility_score / 100) * circumference;

	const occasionEmoji: Record<string, string> = {
		casual: '😊',
		work: '💼',
		formal: '🎩',
		party: '🎉',
		date: '❤️',
		sport: '🏃',
	};
</script>

<div class="card overflow-hidden animate-slide-up" style="animation-delay: {index * 80}ms">
	<!-- Header -->
	<div class="p-4 flex items-start justify-between gap-3 border-b border-gray-50">
		<div class="flex-1 min-w-0">
			<div class="flex items-center gap-2 flex-wrap">
				<span class="text-lg">{occasionEmoji[outfit.occasion] ?? '👗'}</span>
				<h3 class="font-semibold text-gray-900 text-sm">
					{outfit.description ?? `Outfit ${index + 1}`}
				</h3>
			</div>
			<div class="mt-1 flex items-center gap-2">
				<span class="badge-gray">{outfit.occasion}</span>
				{#if outfit.is_saved}
					<span class="badge-purple">Saved</span>
				{/if}
			</div>
		</div>

		<!-- Score ring -->
		<div class="flex-shrink-0 relative w-14 h-14">
			<svg class="w-14 h-14 -rotate-90" viewBox="0 0 48 48">
				<circle cx="24" cy="24" r="20" fill="none" stroke="#e5e7eb" stroke-width="4" />
				<circle
					cx="24"
					cy="24"
					r="20"
					fill="none"
					class={scoreRing}
					stroke-width="4"
					stroke-linecap="round"
					stroke-dasharray={circumference}
					stroke-dashoffset={dashOffset}
					style="transition: stroke-dashoffset 0.6s ease"
				/>
			</svg>
			<div class="absolute inset-0 flex flex-col items-center justify-center">
				<span class="text-xs font-bold {scoreColor}">{Math.round(outfit.compatibility_score)}</span>
				<span class="text-[9px] text-gray-400">score</span>
			</div>
		</div>
	</div>

	<!-- Items grid -->
	<div class="p-4">
		<div class="grid grid-cols-3 sm:grid-cols-4 gap-2">
			{#each outfit.items.slice(0, 4) as item}
				<div class="aspect-square rounded-xl overflow-hidden bg-gray-50 border border-gray-100">
					{#if item.image_url && !item.image_url.startsWith('data:')}
						<img
							src={item.image_url}
							alt={item.name}
							class="w-full h-full object-cover"
							loading="lazy"
						/>
					{:else if item.image_url?.startsWith('data:')}
						<img src={item.image_url} alt={item.name} class="w-full h-full object-contain p-1" />
					{:else}
						<div class="w-full h-full flex items-center justify-center text-2xl">
							{#if item.category === 'top'}👕{:else if item.category === 'bottom'}👖{:else if item.category === 'dress'}👗{:else if item.category === 'shoes'}👟{:else if item.category === 'outerwear'}🧥{:else}💍{/if}
						</div>
					{/if}
				</div>
			{/each}
			{#if outfit.items.length > 4}
				<div class="aspect-square rounded-xl bg-gray-100 flex items-center justify-center text-xs text-gray-500 font-medium">
					+{outfit.items.length - 4}
				</div>
			{/if}
		</div>

		<!-- Item names -->
		<div class="mt-3 flex flex-wrap gap-1">
			{#each outfit.items as item}
				<span class="badge-gray text-[10px]">{item.name}</span>
			{/each}
		</div>
	</div>

	<!-- Feedback -->
	{#if outfit.feedback && outfit.feedback.length > 0}
		<div class="px-4 pb-3">
			<button
				class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
				on:click={() => (expanded = !expanded)}
			>
				{#if expanded}
					<ChevronUp size={12} />
					Hide tips
				{:else}
					<ChevronDown size={12} />
					{outfit.feedback.length} styling tip{outfit.feedback.length !== 1 ? 's' : ''}
				{/if}
			</button>

			{#if expanded}
				<ul class="mt-2 space-y-1">
					{#each outfit.feedback as tip}
						<li class="flex items-start gap-1.5 text-xs text-gray-600">
							<span class="text-primary-500 mt-0.5 flex-shrink-0">✦</span>
							{tip}
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}

	<!-- Actions -->
	<div class="px-4 pb-4 flex items-center gap-2">
		<button
			class="btn-ghost text-xs flex-1 gap-1.5"
			class:text-red-500={outfit.liked}
			class:bg-red-50={outfit.liked}
			on:click={() => dispatch('like', { id: outfit.id, liked: !outfit.liked })}
		>
			<Heart size={14} class={outfit.liked ? 'fill-current' : ''} />
			{outfit.liked ? 'Liked' : 'Like'}
		</button>

		<button
			class="btn-ghost text-xs flex-1 gap-1.5"
			class:text-primary-600={outfit.is_saved}
			class:bg-primary-50={outfit.is_saved}
			on:click={() => dispatch('save', outfit.id)}
		>
			<Bookmark size={14} class={outfit.is_saved ? 'fill-current' : ''} />
			{outfit.is_saved ? 'Saved' : 'Save'}
		</button>

		<button
			class="btn-ghost text-xs flex-1 gap-1.5"
			on:click={() => dispatch('share', outfit.id)}
		>
			<Share2 size={14} />
			Share
		</button>
	</div>
</div>

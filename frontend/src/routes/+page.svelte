<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore, isAuthenticated } from '$lib/stores/auth';
	import { Sparkles, Shirt, Zap, Heart } from 'lucide-svelte';

	let checkingAuth = true;

	onMount(async () => {
		await authStore.init();
		if ($isAuthenticated) {
			goto('/closet');
		}
		checkingAuth = false;
	});

	const features = [
		{ icon: Shirt, title: 'Your Wardrobe', desc: 'Upload photos or add items manually. Your closet, organized.' },
		{ icon: Zap, title: 'AI Styling', desc: 'Smart outfit combinations using color harmony and style rules.' },
		{ icon: Heart, title: 'Learn Your Style', desc: 'Like outfits, take the style quiz — AI learns your preferences.' },
	];
</script>

<svelte:head>
	<title>Closet AI — Your AI Personal Stylist</title>
</svelte:head>

{#if checkingAuth}
	<div class="flex items-center justify-center min-h-[60vh]">
		<div class="text-center">
			<div class="text-4xl mb-4 animate-pulse-slow">👗</div>
			<p class="text-gray-500">Loading…</p>
		</div>
	</div>
{:else}
	<div class="min-h-[80vh] flex flex-col items-center justify-center text-center py-16 px-4">
		<!-- Hero -->
		<div class="max-w-2xl animate-fade-in">
			<div class="inline-flex items-center gap-2 bg-primary-50 text-primary-700 rounded-full px-4 py-1.5 text-sm font-medium mb-6">
				<Sparkles size={14} />
				AI-Powered Personal Stylist
			</div>

			<h1 class="text-5xl sm:text-6xl font-bold text-gray-900 leading-tight mb-4">
				Your wardrobe,
				<span class="gradient-text"> reimagined</span>
			</h1>

			<p class="text-lg text-gray-500 mb-8 max-w-lg mx-auto">
				Upload your clothing and get personalized outfit combinations powered by AI. Turn your existing wardrobe into endless possibilities.
			</p>

			<div class="flex flex-col sm:flex-row gap-3 justify-center mb-16">
				<a href="/register" class="btn-primary text-base px-6 py-3">
					Get Started Free
				</a>
				<a href="/login" class="btn-secondary text-base px-6 py-3">
					Sign In
				</a>
			</div>

			<!-- Features -->
			<div class="grid sm:grid-cols-3 gap-6 text-left">
				{#each features as feature, i}
					<div class="card p-5 animate-slide-up" style="animation-delay: {i * 100}ms">
						<div class="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center mb-3">
							<svelte:component this={feature.icon} size={20} class="text-primary-600" />
						</div>
						<h3 class="font-semibold text-gray-900 mb-1">{feature.title}</h3>
						<p class="text-sm text-gray-500">{feature.desc}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}

<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore, isAuthenticated } from '$lib/stores/auth';
	import { Shirt, Sparkles, Bookmark, BarChart2, Menu, X, LogOut } from 'lucide-svelte';
	import { initAnalytics, analytics } from '$lib/utils/analytics';

	const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY ?? '';

	let mobileMenuOpen = false;

	onMount(async () => {
		if (POSTHOG_KEY) initAnalytics(POSTHOG_KEY);
		await authStore.init();
		analytics.pageView($page.url.pathname);
	});

	$: navItems = [
		{ href: '/closet', label: 'My Closet', icon: Shirt },
		{ href: '/outfits', label: 'Outfits', icon: Sparkles },
		{ href: '/outfits/saved', label: 'Saved', icon: Bookmark },
	];

	$: isAuthRoute = $page.url.pathname === '/' || $page.url.pathname === '/login' || $page.url.pathname === '/register';
</script>

<div class="min-h-screen bg-gray-50">
	{#if !isAuthRoute && $isAuthenticated}
		<!-- Topbar -->
		<header class="sticky top-0 z-40 bg-white border-b border-gray-100 shadow-sm">
			<div class="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
				<!-- Logo -->
				<a href="/closet" class="flex items-center gap-2 font-bold text-gray-900">
					<span class="text-xl">👗</span>
					<span class="gradient-text">Closet AI</span>
				</a>

				<!-- Desktop nav -->
				<nav class="hidden md:flex items-center gap-1">
					{#each navItems as item}
						<a
							href={item.href}
							class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
							class:text-primary-600={$page.url.pathname.startsWith(item.href)}
							class:bg-primary-50={$page.url.pathname.startsWith(item.href)}
							class:text-gray-600={!$page.url.pathname.startsWith(item.href)}
							class:hover:bg-gray-100={!$page.url.pathname.startsWith(item.href)}
						>
							<svelte:component this={item.icon} size={16} />
							{item.label}
						</a>
					{/each}
				</nav>

				<!-- Right actions -->
				<div class="flex items-center gap-2">
					<span class="hidden sm:block text-sm text-gray-500">
						{$authStore.user?.username}
					</span>
					<button
						class="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500"
						on:click={() => { authStore.logout(); goto('/'); }}
						title="Logout"
					>
						<LogOut size={16} />
					</button>
					<!-- Mobile menu btn -->
					<button
						class="md:hidden p-2 hover:bg-gray-100 rounded-lg"
						on:click={() => (mobileMenuOpen = !mobileMenuOpen)}
					>
						{#if mobileMenuOpen}<X size={18} />{:else}<Menu size={18} />{/if}
					</button>
				</div>
			</div>

			<!-- Mobile nav -->
			{#if mobileMenuOpen}
				<nav class="md:hidden border-t border-gray-100 bg-white px-4 py-2 flex flex-col gap-1">
					{#each navItems as item}
						<a
							href={item.href}
							class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium"
							class:text-primary-600={$page.url.pathname.startsWith(item.href)}
							class:bg-primary-50={$page.url.pathname.startsWith(item.href)}
							class:text-gray-600={!$page.url.pathname.startsWith(item.href)}
							on:click={() => (mobileMenuOpen = false)}
						>
							<svelte:component this={item.icon} size={16} />
							{item.label}
						</a>
					{/each}
				</nav>
			{/if}
		</header>
	{/if}

	<main class="max-w-6xl mx-auto px-4 py-6">
		<slot />
	</main>
</div>

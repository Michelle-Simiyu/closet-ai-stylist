<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { analytics } from '$lib/utils/analytics';

	let email = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleLogin() {
		error = '';
		loading = true;
		try {
			await authStore.login(email, password);
			goto('/closet');
		} catch (err: unknown) {
			error = (err as { detail?: string })?.detail ?? 'Login failed. Check your credentials.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Sign In — Closet AI</title></svelte:head>

<div class="max-w-sm mx-auto pt-8 animate-fade-in">
	<div class="text-center mb-8">
		<div class="text-4xl mb-3">👗</div>
		<h1 class="text-2xl font-bold text-gray-900">Welcome back</h1>
		<p class="text-gray-500 mt-1">Sign in to your wardrobe</p>
	</div>

	<div class="card p-6">
		<form on:submit|preventDefault={handleLogin} class="space-y-4">
			<div>
				<label class="label" for="email">Email</label>
				<input class="input" id="email" type="email" bind:value={email} placeholder="you@example.com" required autocomplete="email" />
			</div>
			<div>
				<label class="label" for="password">Password</label>
				<input class="input" id="password" type="password" bind:value={password} placeholder="••••••••" required autocomplete="current-password" />
			</div>

			{#if error}
				<p class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{error}</p>
			{/if}

			<button type="submit" class="btn-primary w-full" disabled={loading}>
				{loading ? 'Signing in…' : 'Sign In'}
			</button>
		</form>

		<p class="text-center text-sm text-gray-500 mt-4">
			No account?
			<a href="/register" class="text-primary-600 font-medium hover:underline">Create one</a>
		</p>
	</div>
</div>

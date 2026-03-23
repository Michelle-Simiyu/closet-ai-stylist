<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { analytics } from '$lib/utils/analytics';

	let email = '';
	let username = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleRegister() {
		error = '';
		if (password.length < 8) { error = 'Password must be at least 8 characters'; return; }
		loading = true;
		try {
			await authStore.register(email, username, password);
			analytics.userSignedUp();
			goto('/onboarding');
		} catch (err: unknown) {
			error = (err as { detail?: string })?.detail ?? 'Registration failed';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Create Account — Closet AI</title></svelte:head>

<div class="max-w-sm mx-auto pt-8 animate-fade-in">
	<div class="text-center mb-8">
		<div class="text-4xl mb-3">✨</div>
		<h1 class="text-2xl font-bold text-gray-900">Create your account</h1>
		<p class="text-gray-500 mt-1">Start building your smart wardrobe</p>
	</div>

	<div class="card p-6">
		<form on:submit|preventDefault={handleRegister} class="space-y-4">
			<div>
				<label class="label" for="email">Email</label>
				<input class="input" id="email" type="email" bind:value={email} placeholder="you@example.com" required autocomplete="email" />
			</div>
			<div>
				<label class="label" for="username">Username</label>
				<input class="input" id="username" bind:value={username} placeholder="stylist123" required autocomplete="username" />
			</div>
			<div>
				<label class="label" for="password">Password</label>
				<input class="input" id="password" type="password" bind:value={password} placeholder="Min 8 characters" required autocomplete="new-password" />
			</div>

			{#if error}
				<p class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{error}</p>
			{/if}

			<button type="submit" class="btn-primary w-full" disabled={loading}>
				{loading ? 'Creating account…' : 'Create Account'}
			</button>
		</form>

		<p class="text-center text-sm text-gray-500 mt-4">
			Already have an account?
			<a href="/login" class="text-primary-600 font-medium hover:underline">Sign in</a>
		</p>
	</div>
</div>

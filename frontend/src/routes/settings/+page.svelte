<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore, isAuthenticated, currentUser } from '$lib/stores/auth';
	import { profileApi } from '$lib/api/client';
	import { Camera, User, Lock, Eye, Palette } from 'lucide-svelte';

	let activeTab: 'profile' | 'privacy' | 'style' | 'account' = 'profile';
	let saving = false;
	let saved = false;
	let error = '';

	// Profile fields
	let username = '';
	let bio = '';
	let gender = '';
	let country = '';
	let countrySearch = '';

	// Privacy
	let closetVisibility: 'private' | 'friends' | 'public' = 'private';

	// Change password
	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let passwordError = '';

	const COUNTRIES = [
		'Afghanistan','Albania','Algeria','Argentina','Australia','Austria','Bangladesh',
		'Belgium','Bolivia','Brazil','Cambodia','Cameroon','Canada','Chile','China',
		'Colombia','Congo','Costa Rica','Croatia','Cuba','Czech Republic','Denmark',
		'Dominican Republic','Ecuador','Egypt','El Salvador','Ethiopia','Finland',
		'France','Germany','Ghana','Greece','Guatemala','Haiti','Honduras','Hungary',
		'India','Indonesia','Iran','Iraq','Ireland','Israel','Italy','Jamaica','Japan',
		'Jordan','Kazakhstan','Kenya','Kuwait','Lebanon','Libya','Malaysia','Mexico',
		'Morocco','Mozambique','Myanmar','Nepal','Netherlands','New Zealand','Nicaragua',
		'Nigeria','Norway','Pakistan','Panama','Paraguay','Peru','Philippines','Poland',
		'Portugal','Qatar','Romania','Russia','Saudi Arabia','Senegal','Serbia',
		'Sierra Leone','Singapore','Somalia','South Africa','South Korea','Spain',
		'Sri Lanka','Sudan','Sweden','Switzerland','Syria','Tanzania','Thailand',
		'Tunisia','Turkey','Uganda','Ukraine','United Arab Emirates','United Kingdom',
		'United States','Uruguay','Venezuela','Vietnam','Yemen','Zambia','Zimbabwe',
	];

	$: filteredCountries = countrySearch.length > 0
		? COUNTRIES.filter(c => c.toLowerCase().includes(countrySearch.toLowerCase())).slice(0, 6)
		: [];

	onMount(async () => {
		await authStore.init();
		if (!$isAuthenticated) { goto('/'); return; }
		username = $currentUser?.username ?? '';
		bio = ($currentUser as any)?.bio ?? '';
		gender = ($currentUser as any)?.gender ?? '';
		country = ($currentUser as any)?.country ?? '';
		closetVisibility = (($currentUser as any)?.closet_visibility ?? 'private') as typeof closetVisibility;
	});

	async function saveProfile() {
		saving = true; error = ''; saved = false;
		try {
			const updated = await profileApi.update({ username, bio, gender, country });
			authStore.setUser(updated);
			saved = true;
			setTimeout(() => (saved = false), 2500);
		} catch (e: any) {
			error = e?.detail ?? 'Failed to save profile';
		} finally {
			saving = false;
		}
	}

	async function savePrivacy() {
		saving = true; error = ''; saved = false;
		try {
			const updated = await profileApi.update({ closet_visibility: closetVisibility });
			authStore.setUser(updated);
			saved = true;
			setTimeout(() => (saved = false), 2500);
		} catch (e: any) {
			error = e?.detail ?? 'Failed to save privacy settings';
		} finally {
			saving = false;
		}
	}

	async function changePassword() {
		passwordError = '';
		if (newPassword !== confirmPassword) {
			passwordError = 'Passwords do not match';
			return;
		}
		if (newPassword.length < 8) {
			passwordError = 'Password must be at least 8 characters';
			return;
		}
		saving = true;
		try {
			await profileApi.changePassword(currentPassword, newPassword);
			currentPassword = ''; newPassword = ''; confirmPassword = '';
			saved = true;
			setTimeout(() => (saved = false), 2500);
		} catch (e: any) {
			passwordError = e?.detail ?? 'Failed to change password';
		} finally {
			saving = false;
		}
	}

	const genderOptions = [
		{ value: 'female', label: 'Female', emoji: '👩' },
		{ value: 'male', label: 'Male', emoji: '👨' },
		{ value: 'nonbinary', label: 'Non-binary', emoji: '🧑' },
		{ value: 'prefer_not_to_say', label: 'Prefer not to say', emoji: '🤍' },
	];

	const visibilityOptions = [
		{ value: 'private', label: 'Private', desc: 'Only you can see your closet', emoji: '🔒' },
		{ value: 'friends', label: 'Friends only', desc: 'Only friends can see your closet & outfits', emoji: '👥' },
		{ value: 'public', label: 'Public', desc: 'Anyone can view your closet & saved outfits', emoji: '🌍' },
	];
</script>

<svelte:head><title>Settings — Closet AI</title></svelte:head>

<div class="max-w-2xl mx-auto">
	<h1 class="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

	<!-- Tabs -->
	<div class="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl">
		{#each [
			{ id: 'profile', label: 'Profile', icon: User },
			{ id: 'privacy', label: 'Privacy', icon: Eye },
			{ id: 'account', label: 'Account', icon: Lock },
		] as tab}
			<button
				class="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-sm font-medium transition-all"
				class:bg-white={activeTab === tab.id}
				class:shadow-sm={activeTab === tab.id}
				class:text-gray-900={activeTab === tab.id}
				class:text-gray-500={activeTab !== tab.id}
				on:click={() => { activeTab = tab.id as typeof activeTab; error = ''; saved = false; }}
			>
				<svelte:component this={tab.icon} size={14} />
				{tab.label}
			</button>
		{/each}
	</div>

	{#if saved}
		<div class="mb-4 px-4 py-3 bg-green-50 border border-green-200 text-green-700 rounded-xl text-sm">
			✓ Changes saved
		</div>
	{/if}
	{#if error}
		<div class="mb-4 px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
			{error}
		</div>
	{/if}

	<!-- Profile tab -->
	{#if activeTab === 'profile'}
		<div class="card p-6 space-y-5">
			<h2 class="font-semibold text-gray-900">Profile information</h2>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
				<input
					type="text" bind:value={username}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
					placeholder="Your username"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Bio</label>
				<textarea
					bind:value={bio} rows="3"
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 resize-none"
					placeholder="Tell people a little about your style…"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Gender identity</label>
				<div class="grid grid-cols-2 gap-2">
					{#each genderOptions as opt}
						<button
							type="button"
							class="p-3 rounded-xl border-2 text-sm font-medium transition-all flex items-center gap-2"
							class:border-primary-500={gender === opt.value}
							class:bg-primary-50={gender === opt.value}
							class:text-primary-700={gender === opt.value}
							class:border-gray-200={gender !== opt.value}
							class:text-gray-600={gender !== opt.value}
							on:click={() => (gender = opt.value)}
						>
							<span>{opt.emoji}</span>{opt.label}
						</button>
					{/each}
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Country</label>
				{#if country}
					<div class="flex items-center gap-2 px-3 py-2.5 bg-primary-50 rounded-xl border border-primary-200 mb-2">
						<span>📍</span>
						<span class="text-sm font-medium text-primary-700">{country}</span>
						<button class="ml-auto text-primary-400 hover:text-primary-600 text-xs" on:click={() => { country = ''; countrySearch = ''; }}>Change</button>
					</div>
				{/if}
				<input
					type="text" bind:value={countrySearch}
					placeholder="Search country…"
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
				/>
				{#if filteredCountries.length > 0}
					<div class="mt-1 border border-gray-100 rounded-xl overflow-hidden bg-white shadow-sm">
						{#each filteredCountries as c}
							<button
								type="button"
								class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
								on:click={() => { country = c; countrySearch = ''; }}
							>{c}</button>
						{/each}
					</div>
				{/if}
			</div>

			<button class="btn-primary w-full" on:click={saveProfile} disabled={saving}>
				{saving ? 'Saving…' : 'Save Profile'}
			</button>
		</div>

	<!-- Privacy tab -->
	{:else if activeTab === 'privacy'}
		<div class="card p-6 space-y-5">
			<div>
				<h2 class="font-semibold text-gray-900">Closet visibility</h2>
				<p class="text-sm text-gray-500 mt-1">Control who can see your wardrobe and outfit saves</p>
			</div>

			<div class="space-y-2">
				{#each visibilityOptions as opt}
					<button
						type="button"
						class="w-full p-4 rounded-xl border-2 text-left transition-all"
						class:border-primary-500={closetVisibility === opt.value}
						class:bg-primary-50={closetVisibility === opt.value}
						class:border-gray-200={closetVisibility !== opt.value}
						on:click={() => (closetVisibility = opt.value as typeof closetVisibility)}
					>
						<div class="flex items-center gap-3">
							<span class="text-xl">{opt.emoji}</span>
							<div>
								<div class="text-sm font-medium text-gray-900">{opt.label}</div>
								<div class="text-xs text-gray-500 mt-0.5">{opt.desc}</div>
							</div>
							{#if closetVisibility === opt.value}
								<span class="ml-auto text-primary-500 text-lg">✓</span>
							{/if}
						</div>
					</button>
				{/each}
			</div>

			<div class="rounded-xl bg-amber-50 border border-amber-200 p-3 text-xs text-amber-700">
				<strong>Friends</strong> can recommend closet items to each other and share outfit suggestions when visibility is set to Friends or Public.
			</div>

			<button class="btn-primary w-full" on:click={savePrivacy} disabled={saving}>
				{saving ? 'Saving…' : 'Save Privacy Settings'}
			</button>
		</div>

	<!-- Account tab -->
	{:else if activeTab === 'account'}
		<div class="card p-6 space-y-5">
			<h2 class="font-semibold text-gray-900">Change password</h2>

			{#if passwordError}
				<div class="px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
					{passwordError}
				</div>
			{/if}

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Current password</label>
				<input
					type="password" bind:value={currentPassword}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
				/>
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">New password</label>
				<input
					type="password" bind:value={newPassword}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
					placeholder="Minimum 8 characters"
				/>
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Confirm new password</label>
				<input
					type="password" bind:value={confirmPassword}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
				/>
			</div>

			<button
				class="btn-primary w-full"
				on:click={changePassword}
				disabled={saving || !currentPassword || !newPassword}
			>
				{saving ? 'Updating…' : 'Update Password'}
			</button>

			<div class="border-t border-gray-100 pt-5">
				<h2 class="font-semibold text-gray-900 mb-1">Email address</h2>
				<p class="text-sm text-gray-500 mb-2">Signed in as</p>
				<div class="px-3 py-2.5 bg-gray-50 rounded-xl text-sm text-gray-700 font-mono">
					{$currentUser?.email ?? '—'}
				</div>
			</div>
		</div>
	{/if}
</div>

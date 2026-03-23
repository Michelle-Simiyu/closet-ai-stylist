<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore, isAuthenticated } from '$lib/stores/auth';
	import { socialApi, type UserPublic, type FriendshipRead, type ClosetRecommendationRead, type MarketplaceListing } from '$lib/api/client';
	import { Search, UserPlus, UserCheck, ShoppingBag, Bell, Users } from 'lucide-svelte';

	type Tab = 'friends' | 'discover' | 'requests' | 'marketplace' | 'recommendations';
	let activeTab: Tab = 'friends';

	let friends: UserPublic[] = [];
	let pendingRequests: FriendshipRead[] = [];
	let sentRequests: FriendshipRead[] = [];
	let searchResults: UserPublic[] = [];
	let recommendations: ClosetRecommendationRead[] = [];
	let marketplace: MarketplaceListing[] = [];

	let searchQuery = '';
	let searching = false;
	let loading = false;
	let actionMsg = '';

	// For viewing a friend's closet inline
	let viewingUser: UserPublic | null = null;
	let friendCloset: unknown[] = [];
	let friendOutfits: unknown[] = [];
	let viewTab: 'closet' | 'outfits' = 'closet';
	let loadingView = false;

	onMount(async () => {
		await authStore.init();
		if (!$isAuthenticated) { goto('/'); return; }
		await loadAll();
	});

	async function loadAll() {
		loading = true;
		try {
			[friends, pendingRequests, recommendations, marketplace] = await Promise.all([
				socialApi.getFriends(),
				socialApi.getRequests(),
				socialApi.getRecommendations(),
				socialApi.getMarketplace(),
			]);
		} catch {}
		loading = false;
	}

	async function searchUsers() {
		if (!searchQuery.trim()) return;
		searching = true;
		try {
			searchResults = await socialApi.searchUsers(searchQuery);
		} catch {}
		searching = false;
	}

	async function sendRequest(userId: string) {
		try {
			await socialApi.sendFriendRequest(userId);
			actionMsg = 'Friend request sent!';
			sentRequests = await socialApi.getSentRequests();
		} catch (e: any) {
			actionMsg = e?.detail ?? 'Could not send request';
		}
		setTimeout(() => (actionMsg = ''), 3000);
	}

	async function acceptRequest(friendshipId: string) {
		await socialApi.acceptRequest(friendshipId);
		await loadAll();
	}

	async function declineRequest(userId: string) {
		await socialApi.removeFriend(userId);
		pendingRequests = await socialApi.getRequests();
	}

	async function removeFriend(userId: string) {
		await socialApi.removeFriend(userId);
		friends = friends.filter(f => f.id !== userId);
		if (viewingUser?.id === userId) viewingUser = null;
	}

	async function viewFriendProfile(user: UserPublic) {
		viewingUser = user;
		loadingView = true;
		try {
			[friendCloset, friendOutfits] = await Promise.all([
				socialApi.getFriendCloset(user.id),
				socialApi.getFriendOutfits(user.id),
			]);
		} catch {}
		loadingView = false;
	}

	async function markSold(listingId: string) {
		await socialApi.markSold(listingId);
		marketplace = await socialApi.getMarketplace();
	}

	async function markRecRead(recId: string) {
		await socialApi.markRecommendationRead(recId);
		recommendations = recommendations.map(r => r.id === recId ? { ...r, is_read: true } : r);
	}

	function isFriend(userId: string) {
		return friends.some(f => f.id === userId);
	}

	function hasSentRequest(userId: string) {
		return sentRequests.some(r => r.addressee_id === userId);
	}

	$: unreadRecs = recommendations.filter(r => !r.is_read).length;
	$: pendingCount = pendingRequests.length;
</script>

<svelte:head><title>Social — Closet AI</title></svelte:head>

<div class="max-w-4xl mx-auto">
	<h1 class="text-2xl font-bold text-gray-900 mb-6">Social</h1>

	<!-- Tabs -->
	<div class="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl overflow-x-auto">
		{#each [
			{ id: 'friends', label: 'Friends', icon: Users, badge: 0 },
			{ id: 'discover', label: 'Discover', icon: Search, badge: 0 },
			{ id: 'requests', label: 'Requests', icon: UserPlus, badge: pendingCount },
			{ id: 'marketplace', label: 'Marketplace', icon: ShoppingBag, badge: 0 },
			{ id: 'recommendations', label: 'Tips', icon: Bell, badge: unreadRecs },
		] as tab}
			<button
				class="flex-shrink-0 flex items-center gap-1.5 py-2 px-3 rounded-lg text-sm font-medium transition-all relative"
				class:bg-white={activeTab === tab.id}
				class:shadow-sm={activeTab === tab.id}
				class:text-gray-900={activeTab === tab.id}
				class:text-gray-500={activeTab !== tab.id}
				on:click={() => { activeTab = tab.id as Tab; viewingUser = null; }}
			>
				<svelte:component this={tab.icon} size={14} />
				{tab.label}
				{#if tab.badge > 0}
					<span class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[9px] flex items-center justify-center font-bold">
						{tab.badge}
					</span>
				{/if}
			</button>
		{/each}
	</div>

	{#if actionMsg}
		<div class="mb-4 px-4 py-3 bg-primary-50 border border-primary-200 text-primary-700 rounded-xl text-sm animate-fade-in">
			{actionMsg}
		</div>
	{/if}

	<!-- FRIENDS tab -->
	{#if activeTab === 'friends'}
		{#if viewingUser}
			<!-- Friend profile view -->
			<div class="mb-4 flex items-center gap-3">
				<button class="btn-ghost text-sm" on:click={() => viewingUser = null}>← Back</button>
				<div class="flex items-center gap-2">
					<div class="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-sm">
						{viewingUser.username[0].toUpperCase()}
					</div>
					<div>
						<div class="font-semibold text-gray-900 text-sm">{viewingUser.username}</div>
						{#if viewingUser.bio}<div class="text-xs text-gray-500">{viewingUser.bio}</div>{/if}
					</div>
				</div>
				<button class="ml-auto btn-ghost text-xs text-red-500 hover:bg-red-50" on:click={() => removeFriend(viewingUser!.id)}>
					Remove friend
				</button>
			</div>

			<!-- Closet / Outfits sub-tabs -->
			<div class="flex gap-2 mb-4">
				<button
					class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
					class:bg-primary-600={viewTab === 'closet'}
					class:text-white={viewTab === 'closet'}
					class:bg-gray-100={viewTab !== 'closet'}
					class:text-gray-600={viewTab !== 'closet'}
					on:click={() => (viewTab = 'closet')}
				>Closet ({friendCloset.length})</button>
				<button
					class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
					class:bg-primary-600={viewTab === 'outfits'}
					class:text-white={viewTab === 'outfits'}
					class:bg-gray-100={viewTab !== 'outfits'}
					class:text-gray-600={viewTab !== 'outfits'}
					on:click={() => (viewTab = 'outfits')}
				>Saved Outfits ({friendOutfits.length})</button>
			</div>

			{#if loadingView}
				<div class="text-center py-12 text-gray-400">Loading…</div>
			{:else if viewTab === 'closet'}
				{#if friendCloset.length === 0}
					<div class="text-center py-12 text-gray-400">
						{#if viewingUser.closet_visibility === 'private'}
							🔒 This closet is private
						{:else}
							No items yet
						{/if}
					</div>
				{:else}
					<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
						{#each friendCloset as item}
							{@const i = item as any}
							<div class="card overflow-hidden">
								<div class="aspect-square bg-gray-50">
									{#if i.image_url}
										<img src={i.image_url} alt={i.name} class="w-full h-full object-cover" loading="lazy" />
									{:else}
										<div class="w-full h-full flex items-center justify-center text-3xl">
											{#if i.category === 'top'}👕{:else if i.category === 'bottom'}👖{:else if i.category === 'dress'}👗{:else if i.category === 'shoes'}👟{:else if i.category === 'outerwear'}🧥{:else}💍{/if}
										</div>
									{/if}
								</div>
								<div class="p-2">
									<div class="text-xs font-medium text-gray-900 truncate">{i.name}</div>
									<div class="text-xs text-gray-500 capitalize">{i.category}</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			{:else}
				{#if friendOutfits.length === 0}
					<div class="text-center py-12 text-gray-400">No saved outfits yet</div>
				{:else}
					<div class="space-y-3">
						{#each friendOutfits as outfit}
							{@const o = outfit as any}
							<div class="card p-4">
								<div class="flex items-center justify-between mb-3">
									<span class="text-sm font-medium text-gray-900">{o.description ?? o.occasion}</span>
									<span class="badge-gray">{Math.round(o.compatibility_score)}% match</span>
								</div>
								<div class="flex gap-2 overflow-x-auto">
									{#each o.items ?? [] as item}
										{@const it = item as any}
										<div class="flex-shrink-0 w-14 h-14 rounded-lg bg-gray-50 overflow-hidden">
											{#if it.image_url}
												<img src={it.image_url} alt={it.name} class="w-full h-full object-cover" />
											{:else}
												<div class="w-full h-full flex items-center justify-center">
													{#if it.category === 'top'}👕{:else if it.category === 'bottom'}👖{:else}👗{/if}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			{/if}

		{:else}
			<!-- Friends list -->
			{#if loading}
				<div class="text-center py-12 text-gray-400">Loading…</div>
			{:else if friends.length === 0}
				<div class="text-center py-16">
					<div class="text-5xl mb-3">👥</div>
					<p class="text-gray-500 mb-4">No friends yet. Search for people to connect with!</p>
					<button class="btn-primary" on:click={() => (activeTab = 'discover')}>Find friends</button>
				</div>
			{:else}
				<div class="grid sm:grid-cols-2 gap-3">
					{#each friends as friend}
						<div class="card p-4 flex items-center gap-3">
							<div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
								{friend.username[0].toUpperCase()}
							</div>
							<div class="flex-1 min-w-0">
								<div class="font-medium text-gray-900 text-sm">{friend.username}</div>
								{#if friend.bio}<div class="text-xs text-gray-500 truncate">{friend.bio}</div>{/if}
								<div class="text-xs text-gray-400 mt-0.5">
									{friend.closet_visibility === 'public' ? '🌍 Public' : friend.closet_visibility === 'friends' ? '👥 Shared with friends' : '🔒 Private'}
								</div>
							</div>
							<button
								class="btn-ghost text-xs"
								on:click={() => viewFriendProfile(friend)}
							>View →</button>
						</div>
					{/each}
				</div>
			{/if}
		{/if}

	<!-- DISCOVER tab -->
	{:else if activeTab === 'discover'}
		<div class="space-y-4">
			<div class="flex gap-2">
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search by username…"
					class="flex-1 px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
					on:keydown={e => e.key === 'Enter' && searchUsers()}
				/>
				<button class="btn-primary px-4" on:click={searchUsers} disabled={searching}>
					{searching ? '…' : 'Search'}
				</button>
			</div>

			{#if searchResults.length > 0}
				<div class="space-y-2">
					{#each searchResults as user}
						<div class="card p-4 flex items-center gap-3">
							<div class="w-10 h-10 rounded-full bg-accent-100 flex items-center justify-center text-accent-600 font-bold">
								{user.username[0].toUpperCase()}
							</div>
							<div class="flex-1 min-w-0">
								<div class="font-medium text-gray-900 text-sm">{user.username}</div>
								{#if user.bio}<div class="text-xs text-gray-500 truncate">{user.bio}</div>{/if}
							</div>
							{#if isFriend(user.id)}
								<span class="flex items-center gap-1 text-xs text-green-600 font-medium">
									<UserCheck size={12} /> Friends
								</span>
							{:else if hasSentRequest(user.id)}
								<span class="text-xs text-gray-400">Pending…</span>
							{:else}
								<button class="btn-primary text-xs px-3 py-1.5 flex items-center gap-1" on:click={() => sendRequest(user.id)}>
									<UserPlus size={12} /> Add
								</button>
							{/if}
						</div>
					{/each}
				</div>
			{:else if searchQuery && !searching}
				<div class="text-center py-8 text-gray-400 text-sm">No users found for "{searchQuery}"</div>
			{/if}
		</div>

	<!-- REQUESTS tab -->
	{:else if activeTab === 'requests'}
		<div class="space-y-6">
			<div>
				<h2 class="text-sm font-semibold text-gray-700 mb-3">Incoming requests ({pendingRequests.length})</h2>
				{#if pendingRequests.length === 0}
					<p class="text-sm text-gray-400">No pending requests</p>
				{:else}
					<div class="space-y-2">
						{#each pendingRequests as req}
							<div class="card p-4 flex items-center gap-3">
								<div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-sm">
									{req.requester_id.slice(0, 2).toUpperCase()}
								</div>
								<div class="flex-1 min-w-0">
									<div class="text-sm font-medium text-gray-900">User {req.requester_id.slice(0, 8)}…</div>
									<div class="text-xs text-gray-400">wants to be friends</div>
								</div>
								<button class="btn-primary text-xs px-3 py-1.5" on:click={() => acceptRequest(req.id)}>Accept</button>
								<button class="btn-ghost text-xs px-3 py-1.5" on:click={() => declineRequest(req.requester_id)}>Decline</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

	<!-- MARKETPLACE tab -->
	{:else if activeTab === 'marketplace'}
		<div class="space-y-4">
			<div class="flex items-center justify-between">
				<div>
					<h2 class="font-semibold text-gray-900">Friends' listings</h2>
					<p class="text-xs text-gray-500 mt-0.5">Items your friends have listed for sale</p>
				</div>
				<a href="/closet" class="btn-ghost text-xs">List from my closet →</a>
			</div>

			{#if marketplace.length === 0}
				<div class="text-center py-16">
					<div class="text-5xl mb-3">🛍️</div>
					<p class="text-gray-500 text-sm">No listings yet from your friends.</p>
					<p class="text-gray-400 text-xs mt-1">When friends list items for sale, they'll appear here.</p>
				</div>
			{:else}
				<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each marketplace as listing}
						{@const l = listing as any}
						<div class="card overflow-hidden">
							<div class="aspect-square bg-gray-50">
								{#if l.item?.image_url}
									<img src={l.item.image_url} alt={l.item?.name} class="w-full h-full object-cover" />
								{:else}
									<div class="w-full h-full flex items-center justify-center text-4xl">
										{#if l.item?.category === 'top'}👕{:else if l.item?.category === 'bottom'}👖{:else if l.item?.category === 'dress'}👗{:else if l.item?.category === 'shoes'}👟{:else}🧥{/if}
									</div>
								{/if}
							</div>
							<div class="p-3">
								<div class="font-medium text-sm text-gray-900 truncate">{l.item?.name ?? 'Item'}</div>
								<div class="text-xs text-gray-500 capitalize mb-2">{l.item?.category} · {l.item?.color}</div>
								{#if l.description}
									<div class="text-xs text-gray-600 mb-2">{l.description}</div>
								{/if}
								<div class="flex items-center justify-between">
									<span class="font-bold text-primary-600">
										{l.price ? `${l.currency} ${l.price}` : 'Free / negotiable'}
									</span>
									{#if l.user_id === 'self'}
										<button class="text-xs text-gray-400 hover:text-gray-600" on:click={() => markSold(l.id)}>Mark sold</button>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

	<!-- RECOMMENDATIONS tab -->
	{:else if activeTab === 'recommendations'}
		<div class="space-y-4">
			<div>
				<h2 class="font-semibold text-gray-900">Closet tips from friends</h2>
				<p class="text-xs text-gray-500 mt-0.5">Outfit & item suggestions your friends sent you</p>
			</div>

			{#if recommendations.length === 0}
				<div class="text-center py-16">
					<div class="text-5xl mb-3">💌</div>
					<p class="text-gray-500 text-sm">No recommendations yet.</p>
					<p class="text-gray-400 text-xs mt-1">Friends can suggest items to add, remove, or outfits to try.</p>
				</div>
			{:else}
				<div class="space-y-2">
					{#each recommendations as rec}
						<div
							class="card p-4 transition-all"
							class:opacity-60={rec.is_read}
						>
							<div class="flex items-start gap-3">
								<div class="w-8 h-8 rounded-full bg-accent-100 flex items-center justify-center text-accent-600 font-bold text-xs flex-shrink-0">
									{rec.from_user_id.slice(0, 2).toUpperCase()}
								</div>
								<div class="flex-1 min-w-0">
									<div class="flex items-center gap-2 flex-wrap mb-1">
										<span class="text-xs font-medium text-gray-900">User {rec.from_user_id.slice(0, 8)}…</span>
										<span class="badge-gray text-[10px]">
											{rec.rec_type === 'add' ? '➕ Add to closet' : rec.rec_type === 'remove' ? '🗑️ Remove' : rec.rec_type === 'replace' ? '🔄 Replace' : '👗 Try outfit'}
										</span>
										{#if !rec.is_read}
											<span class="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0"></span>
										{/if}
									</div>
									{#if rec.message}
										<p class="text-sm text-gray-600">"{rec.message}"</p>
									{/if}
									<div class="text-xs text-gray-400 mt-1">
										{new Date(rec.created_at).toLocaleDateString()}
									</div>
								</div>
								{#if !rec.is_read}
									<button class="text-xs text-gray-400 hover:text-gray-600 flex-shrink-0" on:click={() => markRecRead(rec.id)}>
										Mark read
									</button>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

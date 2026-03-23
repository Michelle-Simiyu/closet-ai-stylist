<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { X, Upload, Camera, Loader2 } from 'lucide-svelte';
	import { closetApi, type ClothingItemCreate } from '$lib/api/client';

	export let open = false;

	const dispatch = createEventDispatcher<{ close: void; saved: ClothingItemCreate }>();

	type Step = 'form' | 'uploading';
	let step: Step = 'form';
	let error = '';

	// Form state
	let name = '';
	let category = 'top';
	let color = 'white';
	let secondary_color = '';
	let style = 'casual';
	let pattern = 'solid';
	let formality = 2;
	let season = 'all';
	let imageFile: File | null = null;
	let imagePreview = '';
	let imageUrl = '';

	const categories = ['top', 'bottom', 'dress', 'shoes', 'outerwear', 'accessory'];
	const styles = ['casual', 'formal', 'sporty', 'bohemian', 'minimalist'];
	const patterns = ['solid', 'striped', 'checkered', 'floral', 'geometric', 'abstract'];
	const seasons = ['all', 'spring', 'summer', 'fall', 'winter'];

	function handleFile(e: Event) {
		const target = e.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;
		imageFile = file;
		imagePreview = URL.createObjectURL(file);
		// Suggest color from filename as fallback
		if (!color) {
			const colors = ['white', 'black', 'blue', 'red', 'green', 'gray', 'brown', 'navy'];
			const nameLower = file.name.toLowerCase();
			color = colors.find((c) => nameLower.includes(c)) ?? 'white';
		}
	}

	async function handleSubmit() {
		if (!name.trim()) { error = 'Name is required'; return; }
		error = '';
		step = 'uploading';

		try {
			// Upload image if provided
			if (imageFile) {
				const result = await closetApi.upload(imageFile, true);
				imageUrl = result.image_url;
				// Apply color suggestion if color not manually set
				if (result.suggestions?.color && color === 'white') {
					color = result.suggestions.color;
				}
			}

			const itemData: ClothingItemCreate = {
				name: name.trim(),
				category,
				color,
				secondary_color: secondary_color || undefined,
				style,
				pattern,
				formality,
				season,
				image_url: imageUrl || undefined,
			};

			dispatch('saved', itemData);
			resetForm();
		} catch (err: unknown) {
			error = (err as { detail?: string })?.detail ?? 'Failed to save item';
			step = 'form';
		}
	}

	function resetForm() {
		name = ''; category = 'top'; color = 'white'; secondary_color = '';
		style = 'casual'; pattern = 'solid'; formality = 2; season = 'all';
		imageFile = null; imagePreview = ''; imageUrl = '';
		step = 'form'; error = '';
	}

	function close() {
		resetForm();
		dispatch('close');
	}
</script>

{#if open}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4"
		on:click|self={close}
		on:keydown={(e) => e.key === 'Escape' && close()}
		role="dialog"
		aria-modal="true"
		aria-label="Add clothing item"
		tabindex="-1"
	>
		<div class="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto shadow-xl animate-slide-up">
			<!-- Header -->
			<div class="sticky top-0 bg-white z-10 px-5 py-4 border-b border-gray-100 flex items-center justify-between">
				<h2 class="text-lg font-semibold text-gray-900">Add to Closet</h2>
				<button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" on:click={close}>
					<X size={18} />
				</button>
			</div>

			<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
				<!-- Image upload -->
				<div>
					<label class="label">Photo (optional)</label>
					<div class="relative">
						{#if imagePreview}
							<div class="relative w-full aspect-square rounded-xl overflow-hidden bg-gray-50 mb-2">
								<img src={imagePreview} alt="Preview" class="w-full h-full object-contain" />
								<button
									type="button"
									class="absolute top-2 right-2 p-1 bg-white rounded-full shadow"
									on:click={() => { imageFile = null; imagePreview = ''; }}
								>
									<X size={12} />
								</button>
							</div>
						{:else}
							<label class="flex flex-col items-center justify-center w-full h-32 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors">
								<Upload size={20} class="text-gray-400 mb-1.5" />
								<span class="text-sm text-gray-500">Upload photo</span>
								<span class="text-xs text-gray-400 mt-0.5">PNG, JPG up to 10MB</span>
								<input type="file" accept="image/*" class="sr-only" on:change={handleFile} />
							</label>
						{/if}
					</div>
				</div>

				<!-- Name -->
				<div>
					<label class="label" for="name">Name *</label>
					<input class="input" id="name" bind:value={name} placeholder="e.g. White Button-Down" required />
				</div>

				<!-- Category + Style -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="label" for="category">Category</label>
						<select class="select" id="category" bind:value={category}>
							{#each categories as c}
								<option value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="label" for="style">Style</label>
						<select class="select" id="style" bind:value={style}>
							{#each styles as s}
								<option value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Color -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="label" for="color">Color</label>
						<input class="input" id="color" bind:value={color} placeholder="e.g. navy" />
					</div>
					<div>
						<label class="label" for="secondary_color">Secondary (optional)</label>
						<input class="input" id="secondary_color" bind:value={secondary_color} placeholder="e.g. white" />
					</div>
				</div>

				<!-- Pattern + Season -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="label" for="pattern">Pattern</label>
						<select class="select" id="pattern" bind:value={pattern}>
							{#each patterns as p}
								<option value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="label" for="season">Season</label>
						<select class="select" id="season" bind:value={season}>
							{#each seasons as s}
								<option value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Formality slider -->
				<div>
					<label class="label" for="formality">
						Formality — {['Very Casual', 'Casual', 'Smart Casual', 'Formal', 'Very Formal'][formality - 1]}
					</label>
					<input
						type="range"
						id="formality"
						min="1"
						max="5"
						bind:value={formality}
						class="w-full h-2 bg-gray-200 rounded-full accent-primary-600 cursor-pointer"
					/>
					<div class="flex justify-between text-[10px] text-gray-400 mt-1">
						<span>Casual</span>
						<span>Formal</span>
					</div>
				</div>

				{#if error}
					<p class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{error}</p>
				{/if}

				<!-- Submit -->
				<div class="flex gap-3 pt-2">
					<button type="button" class="btn-secondary flex-1" on:click={close}>Cancel</button>
					<button type="submit" class="btn-primary flex-1" disabled={step === 'uploading'}>
						{#if step === 'uploading'}
							<Loader2 size={16} class="animate-spin" />
							Saving…
						{:else}
							Add Item
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

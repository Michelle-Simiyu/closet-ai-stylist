<script lang="ts">
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { authApi } from '$lib/api/client';

	const dispatch = createEventDispatcher<{ complete: Record<string, unknown> }>();

	interface QuizOption {
		value: string;
		label: string;
		emoji: string;
		desc?: string;
	}

	interface QuizQuestion {
		id: string;
		question: string;
		subtitle?: string;
		type: string;
		skippable: boolean;
		stepName: string;
		options?: QuizOption[];
		labels?: string[];
	}

	let step = 0;
	let saving = false;
	let autoAdvanceTimer: ReturnType<typeof setTimeout> | null = null;

	let quiz = {
		gender: '',
		country: '',
		preferred_styles: [] as string[],
		formality_preference: 3,
		color_preference: '',
		occasion_priority: '',
		budget_sensitivity: '',
		fit_preference: '',
		sustainability_preference: '',
		shopping_frequency: '',
	};

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

	const questions: QuizQuestion[] = [
		{
			id: 'gender',
			question: 'How do you identify?',
			subtitle: 'Helps us tailor clothing and fit recommendations for you',
			type: 'gender',
			skippable: false,
			stepName: 'Identity',
			options: [
				{ value: 'female', label: 'Female', emoji: '👩' },
				{ value: 'male', label: 'Male', emoji: '👨' },
				{ value: 'nonbinary', label: 'Non-binary', emoji: '🧑' },
				{ value: 'prefer_not_to_say', label: 'Prefer not to say', emoji: '🤍' },
			],
		},
		{
			id: 'country',
			question: 'Where are you based?',
			subtitle: 'Enables weather-aware and locally relevant outfit recommendations',
			type: 'country',
			skippable: true,
			stepName: 'Location',
		},
		{
			id: 'preferred_styles',
			question: 'What styles do you gravitate toward?',
			subtitle: 'Pick all that apply — we\'ll blend them together',
			type: 'multi',
			skippable: false,
			stepName: 'Style',
			options: [
				{ value: 'casual', label: 'Casual', emoji: '👕', desc: 'Relaxed everyday wear' },
				{ value: 'minimalist', label: 'Minimalist', emoji: '⬜', desc: 'Clean lines, neutral tones' },
				{ value: 'formal', label: 'Formal', emoji: '👔', desc: 'Polished and professional' },
				{ value: 'bohemian', label: 'Bohemian', emoji: '🌸', desc: 'Free-spirited, earthy' },
				{ value: 'sporty', label: 'Sporty', emoji: '🏃', desc: 'Athletic and active' },
			],
		},
		{
			id: 'formality_preference',
			question: "What's your day-to-day formality level?",
			subtitle: 'Drag to your sweet spot — we\'ll calibrate every recommendation',
			type: 'range',
			skippable: true,
			stepName: 'Formality',
			labels: ['Very Casual', 'Casual', 'Smart Casual', 'Business', 'Formal'],
		},
		{
			id: 'color_preference',
			question: 'How do you approach color?',
			subtitle: 'Your palette shapes every outfit we suggest',
			type: 'single',
			skippable: true,
			stepName: 'Color',
			options: [
				{ value: 'neutral', label: 'Mostly neutrals', desc: 'Black, white, gray, beige, tan', emoji: '🩶' },
				{ value: 'bold', label: 'Bold & vibrant', desc: 'Rich color, statement pieces', emoji: '🌈' },
				{ value: 'mixed', label: 'Balanced mix', desc: 'Neutrals with pops of color', emoji: '🎨' },
			],
		},
		{
			id: 'occasion_priority',
			question: 'What do you mainly dress for?',
			subtitle: "We'll weight suggestions toward your primary context",
			type: 'single',
			skippable: true,
			stepName: 'Occasion',
			options: [
				{ value: 'casual', label: 'Everyday casual', desc: 'Errands, weekends, going out', emoji: '☀️' },
				{ value: 'work', label: 'Office & work', desc: 'Professional and smart environments', emoji: '💼' },
				{ value: 'formal', label: 'Events & nights out', desc: 'Dinners, parties, occasions', emoji: '🎉' },
				{ value: 'date', label: 'Date nights', desc: 'Stylish and put-together', emoji: '❤️' },
			],
		},
		{
			id: 'budget_sensitivity',
			question: 'What\'s your typical budget per clothing item?',
			subtitle: 'Helps us tailor shopping and styling suggestions to your price range',
			type: 'single',
			skippable: true,
			stepName: 'Budget',
			options: [
				{ value: 'low', label: 'Budget-friendly', desc: 'Under $30 — affordable finds', emoji: '💰' },
				{ value: 'medium', label: 'Mid-range', desc: '$30–$100 — quality basics', emoji: '💳' },
				{ value: 'high', label: 'Premium', desc: '$100+ — investment pieces', emoji: '✨' },
			],
		},
		{
			id: 'fit_preference',
			question: 'How do you like your clothes to fit?',
			subtitle: 'Fit affects everything — from comfort to silhouette',
			type: 'single',
			skippable: true,
			stepName: 'Fit',
			options: [
				{ value: 'oversized', label: 'Relaxed & oversized', desc: 'Roomy, comfortable, slouchy', emoji: '🧸' },
				{ value: 'regular', label: 'Regular / true to size', desc: 'Classic fit, not too tight or loose', emoji: '👌' },
				{ value: 'slim', label: 'Slim & tailored', desc: 'Close fit, streamlined silhouette', emoji: '✂️' },
			],
		},
		{
			id: 'sustainability_preference',
			question: 'How important is sustainable fashion to you?',
			subtitle: "We'll highlight eco-conscious brands and second-hand options",
			type: 'single',
			skippable: true,
			stepName: 'Values',
			options: [
				{ value: 'high', label: 'Very important', desc: 'I actively seek sustainable brands', emoji: '🌿' },
				{ value: 'medium', label: 'Somewhat important', desc: 'I consider it when accessible', emoji: '♻️' },
				{ value: 'low', label: 'Not a priority', desc: 'Style and price come first', emoji: '🛍️' },
			],
		},
		{
			id: 'shopping_frequency',
			question: 'How often do you add to your wardrobe?',
			subtitle: 'Helps us understand how to keep your closet fresh',
			type: 'single',
			skippable: true,
			stepName: 'Habits',
			options: [
				{ value: 'rarely', label: 'Rarely', desc: 'Only for special occasions or when needed', emoji: '🎯' },
				{ value: 'seasonally', label: 'Seasonally', desc: 'A few pieces each season', emoji: '🍂' },
				{ value: 'monthly', label: 'Monthly', desc: 'Regular hauls throughout the year', emoji: '📦' },
				{ value: 'weekly', label: 'Frequently', desc: 'Always on the lookout for new pieces', emoji: '🛒' },
			],
		},
	];

	$: currentQ = questions[step];
	$: progress = ((step + 1) / questions.length) * 100;
	$: progressLabel = `${step + 1} of ${questions.length}`;
	$: currentValue = (quiz as Record<string, unknown>)[currentQ.id];

	// Country search
	let countrySearch = '';
	$: filteredCountries = countrySearch.length > 0
		? COUNTRIES.filter(c => c.toLowerCase().includes(countrySearch.toLowerCase())).slice(0, 10)
		: COUNTRIES.slice(0, 10);

	function selectOption(id: string, value: string) {
		quiz = { ...quiz, [id]: value } as typeof quiz;
	}

	function toggleStyle(value: string) {
		if (quiz.preferred_styles.includes(value)) {
			quiz.preferred_styles = quiz.preferred_styles.filter(s => s !== value);
		} else {
			quiz.preferred_styles = [...quiz.preferred_styles, value];
		}
	}

	/** Select a single option then auto-advance after a short delay */
	function selectAndAdvance(id: string, value: string) {
		selectOption(id, value);
		if (autoAdvanceTimer) clearTimeout(autoAdvanceTimer);
		autoAdvanceTimer = setTimeout(() => { next(); }, 380);
	}

	$: canProceed = currentQ.id === 'gender'
		? quiz.gender !== ''
		: currentQ.id === 'preferred_styles'
			? quiz.preferred_styles.length > 0
			: true;

	$: lockedReason = currentQ.id === 'gender'
		? 'Select how you identify to continue'
		: currentQ.id === 'preferred_styles'
			? 'Pick at least one style to continue'
			: '';

	async function finish() {
		saving = true;
		// Convert empty optional strings to null so the backend leaves existing values intact.
		// Fill required string fields with sensible defaults if user skipped them.
		const payload = {
			...quiz,
			gender: quiz.gender || null,
			country: quiz.country || null,
			color_preference: quiz.color_preference || 'mixed',
			occasion_priority: quiz.occasion_priority || 'casual',
			budget_sensitivity: quiz.budget_sensitivity || 'medium',
			fit_preference: quiz.fit_preference || null,
			sustainability_preference: quiz.sustainability_preference || null,
			shopping_frequency: quiz.shopping_frequency || null,
		};
		try {
			await authApi.saveQuiz(payload);
			dispatch('complete', payload);
		} catch {
			dispatch('complete', payload);
		} finally {
			saving = false;
		}
	}

	onDestroy(() => {
		if (autoAdvanceTimer) clearTimeout(autoAdvanceTimer);
	});

	function next() {
		if (autoAdvanceTimer) { clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; }
		if (step < questions.length - 1) {
			step++;
		} else {
			finish();
		}
	}

	function skip() {
		if (autoAdvanceTimer) { clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; }
		if (step < questions.length - 1) {
			step++;
		} else {
			finish();
		}
	}

	function back() {
		if (autoAdvanceTimer) { clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; }
		if (step > 0) step--;
	}
</script>

<div class="max-w-lg mx-auto">
	<!-- Progress -->
	<div class="mb-6">
		<div class="flex justify-between items-center mb-2">
			<span class="text-xs font-semibold text-primary-600 uppercase tracking-wide">{currentQ.stepName}</span>
			<span class="text-xs text-gray-400">{progressLabel}</span>
		</div>
		<div class="h-2 bg-gray-100 rounded-full overflow-hidden">
			<div
				class="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500 ease-out"
				style="width: {progress}%"
			/>
		</div>
		<!-- Step dots -->
		<div class="flex justify-between mt-2 px-0.5">
			{#each questions as q, i}
				<div
					class="w-1.5 h-1.5 rounded-full transition-all duration-300"
					class:bg-primary-500={i < step}
					class:bg-primary-600={i === step}
					class:scale-125={i === step}
					class:bg-gray-200={i > step}
				/>
			{/each}
		</div>
	</div>

	{#key step}
	<div class="card p-6 animate-fade-in">
		<h2 class="text-xl font-semibold text-gray-900 leading-snug">{currentQ.question}</h2>
		{#if currentQ.subtitle}
			<p class="text-sm text-gray-400 mt-1.5 mb-5">{currentQ.subtitle}</p>
		{:else}
			<div class="mb-5" />
		{/if}

		<!-- Gender -->
		{#if currentQ.type === 'gender'}
			<div class="grid grid-cols-2 gap-3">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="p-4 rounded-xl border-2 text-sm font-medium transition-all flex flex-col items-center gap-2 relative"
						class:border-primary-500={quiz.gender === option.value}
						class:bg-primary-50={quiz.gender === option.value}
						class:text-primary-700={quiz.gender === option.value}
						class:shadow-sm={quiz.gender === option.value}
						class:border-gray-200={quiz.gender !== option.value}
						class:text-gray-600={quiz.gender !== option.value}
						class:hover:border-gray-300={quiz.gender !== option.value}
						on:click={() => selectAndAdvance('gender', option.value)}
					>
						{#if quiz.gender === option.value}
							<span class="absolute top-2 right-2 w-4 h-4 bg-primary-500 rounded-full flex items-center justify-center text-white text-[10px]">✓</span>
						{/if}
						<span class="text-3xl">{option.emoji}</span>
						{option.label}
					</button>
				{/each}
			</div>

		<!-- Country -->
		{:else if currentQ.type === 'country'}
			<div class="space-y-2">
				<input
					type="text"
					placeholder="Search your country…"
					bind:value={countrySearch}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
					autofocus
				/>
				{#if quiz.country}
					<div class="flex items-center gap-2 px-3 py-2.5 bg-primary-50 rounded-xl border border-primary-200">
						<span class="text-base">📍</span>
						<span class="text-sm font-medium text-primary-700 flex-1">{quiz.country}</span>
						<button
							class="text-primary-400 hover:text-primary-600 transition-colors text-sm"
							on:click={() => { quiz.country = ''; countrySearch = ''; }}
						>✕</button>
					</div>
				{/if}
				<div class="space-y-0.5 max-h-52 overflow-y-auto rounded-xl border border-gray-100 bg-gray-50 p-1">
					{#each filteredCountries as country}
						<button
							type="button"
							class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors"
							class:bg-primary-100={quiz.country === country}
							class:text-primary-700={quiz.country === country}
							class:font-medium={quiz.country === country}
							class:hover:bg-white={quiz.country !== country}
							class:text-gray-700={quiz.country !== country}
							on:click={() => { selectOption('country', country); countrySearch = ''; }}
						>
							{country}
							{#if quiz.country === country}<span class="float-right text-primary-500">✓</span>{/if}
						</button>
					{/each}
					{#if filteredCountries.length === 0}
						<p class="text-center text-sm text-gray-400 py-4">No countries found</p>
					{/if}
				</div>
			</div>

		<!-- Multi-select styles -->
		{:else if currentQ.type === 'multi'}
			<div class="space-y-2">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="w-full p-3.5 rounded-xl border-2 text-sm font-medium transition-all flex items-center gap-3 text-left relative"
						class:border-primary-500={quiz.preferred_styles.includes(option.value)}
						class:bg-primary-50={quiz.preferred_styles.includes(option.value)}
						class:text-primary-700={quiz.preferred_styles.includes(option.value)}
						class:shadow-sm={quiz.preferred_styles.includes(option.value)}
						class:border-gray-200={!quiz.preferred_styles.includes(option.value)}
						class:text-gray-600={!quiz.preferred_styles.includes(option.value)}
						class:hover:border-gray-300={!quiz.preferred_styles.includes(option.value)}
						on:click={() => toggleStyle(option.value)}
					>
						<span class="text-2xl flex-shrink-0">{option.emoji}</span>
						<div class="flex-1 min-w-0">
							<div>{option.label}</div>
							{#if option.desc}<div class="text-xs text-gray-400 font-normal mt-0.5">{option.desc}</div>{/if}
						</div>
						<div class="w-5 h-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-all"
							class:bg-primary-500={quiz.preferred_styles.includes(option.value)}
							class:border-primary-500={quiz.preferred_styles.includes(option.value)}
							class:border-gray-300={!quiz.preferred_styles.includes(option.value)}
						>
							{#if quiz.preferred_styles.includes(option.value)}
								<span class="text-white text-[10px] font-bold">✓</span>
							{/if}
						</div>
					</button>
				{/each}
			</div>

		<!-- Single select -->
		{:else if currentQ.type === 'single'}
			<div class="space-y-2">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="w-full p-3.5 rounded-xl border-2 text-sm font-medium text-left flex items-center gap-3 transition-all"
						class:border-primary-500={currentValue === option.value}
						class:bg-primary-50={currentValue === option.value}
						class:text-primary-700={currentValue === option.value}
						class:shadow-sm={currentValue === option.value}
						class:border-gray-200={currentValue !== option.value}
						class:text-gray-600={currentValue !== option.value}
						class:hover:border-gray-300={currentValue !== option.value}
						on:click={() => selectAndAdvance(currentQ.id, option.value)}
					>
						<span class="text-xl flex-shrink-0">{option.emoji}</span>
						<div class="flex-1 min-w-0">
							<div>{option.label}</div>
							{#if option.desc}<div class="text-xs text-gray-400 font-normal mt-0.5">{option.desc}</div>{/if}
						</div>
						{#if currentValue === option.value}
							<span class="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">✓</span>
						{/if}
					</button>
				{/each}
			</div>

		<!-- Range -->
		{:else if currentQ.type === 'range'}
			<div class="py-4 space-y-4">
				<div class="px-1">
					<input
						type="range"
						min="1"
						max="5"
						step="1"
						bind:value={quiz.formality_preference}
						class="w-full h-2 rounded-full cursor-pointer accent-primary-600"
					/>
					<div class="flex justify-between text-xs text-gray-400 mt-2">
						{#each currentQ.labels ?? [] as label}
							<span class="text-center leading-tight" style="width: 20%">{label}</span>
						{/each}
					</div>
				</div>
				<div class="text-center py-3 bg-primary-50 rounded-xl">
					<span class="text-base font-semibold text-primary-700">
						{currentQ.labels?.[quiz.formality_preference - 1]}
					</span>
					<p class="text-xs text-primary-500 mt-0.5">
						{quiz.formality_preference === 1 ? 'Think hoodies, sweats, trainers' :
						 quiz.formality_preference === 2 ? 'Jeans, tees, casual sneakers' :
						 quiz.formality_preference === 3 ? 'Chinos, blouses, clean shoes' :
						 quiz.formality_preference === 4 ? 'Blazers, dress shirts, trousers' :
						 'Suits, gowns, formal footwear'}
					</p>
				</div>
			</div>
		{/if}

		<!-- Navigation -->
		<div class="mt-6 space-y-3">
			<!-- Locked hint -->
			{#if !canProceed && lockedReason}
				<p class="text-center text-xs text-gray-400">{lockedReason}</p>
			{/if}

			<div class="flex items-center gap-2">
				<!-- Back -->
				{#if step > 0}
					<button class="btn-ghost px-4" on:click={back}>← Back</button>
				{:else}
					<div class="flex-1" />
				{/if}

				<div class="flex items-center gap-2 ml-auto">
					<!-- Skip (optional steps) -->
					{#if currentQ.skippable && !(currentQ.type === 'range')}
						<button
							class="text-sm text-gray-400 hover:text-gray-600 transition-colors px-2 py-1"
							on:click={skip}
						>Skip</button>
					{/if}

					<!-- Next / Done -->
					<button
						class="btn-primary min-w-[100px]"
						on:click={next}
						disabled={saving || !canProceed}
					>
						{#if saving}
							<span class="flex items-center gap-2">
								<span class="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
								Saving…
							</span>
						{:else if step < questions.length - 1}
							Next →
						{:else}
							Finish ✓
						{/if}
					</button>
				</div>
			</div>
		</div>
	</div>
	{/key}
</div>

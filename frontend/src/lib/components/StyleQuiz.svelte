<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authApi } from '$lib/api/client';

	const dispatch = createEventDispatcher<{ complete: Record<string, unknown> }>();

	let step = 0;
	let saving = false;

	let quiz = {
		gender: '',
		country: '',
		preferred_styles: [] as string[],
		formality_preference: 3,
		color_preference: 'mixed',
		occasion_priority: 'casual',
		budget_sensitivity: 'medium',
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

	const questions = [
		{
			id: 'gender',
			question: 'How do you identify?',
			subtitle: 'This helps us tailor style recommendations for you',
			type: 'gender',
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
			subtitle: 'Used to make weather-aware outfit recommendations',
			type: 'country',
		},
		{
			id: 'preferred_styles',
			question: 'What styles do you gravitate toward?',
			subtitle: 'Pick all that apply',
			type: 'multi',
			options: [
				{ value: 'casual', label: 'Casual', emoji: '👕' },
				{ value: 'minimalist', label: 'Minimalist', emoji: '⬜' },
				{ value: 'formal', label: 'Formal', emoji: '👔' },
				{ value: 'bohemian', label: 'Bohemian', emoji: '🌸' },
				{ value: 'sporty', label: 'Sporty', emoji: '🏃' },
			],
		},
		{
			id: 'formality_preference',
			question: "What's your typical formality level?",
			subtitle: 'Slide to your sweet spot',
			type: 'range',
			labels: ['Very Casual', 'Casual', 'Smart Casual', 'Business', 'Formal'],
		},
		{
			id: 'color_preference',
			question: 'How do you approach color?',
			subtitle: 'Your palette, your rules',
			type: 'single',
			options: [
				{ value: 'neutral', label: 'Mostly neutrals — black, white, gray, beige', emoji: '🩶' },
				{ value: 'bold', label: 'Bold & vibrant colors', emoji: '🌈' },
				{ value: 'mixed', label: 'Mix of neutrals and pops of color', emoji: '🎨' },
			],
		},
		{
			id: 'occasion_priority',
			question: 'What do you dress for most?',
			subtitle: 'We\'ll prioritize these outfit suggestions',
			type: 'single',
			options: [
				{ value: 'casual', label: 'Everyday casual', emoji: '☀️' },
				{ value: 'work', label: 'Office & professional', emoji: '💼' },
				{ value: 'formal', label: 'Events & going out', emoji: '🎉' },
				{ value: 'date', label: 'Date nights', emoji: '❤️' },
			],
		},
	];

	$: currentQ = questions[step];
	$: progress = ((step + 1) / questions.length) * 100;
	$: currentValue = (quiz as Record<string, unknown>)[currentQ.id];

	// Country search
	let countrySearch = '';
	$: filteredCountries = countrySearch.length > 0
		? COUNTRIES.filter(c => c.toLowerCase().includes(countrySearch.toLowerCase())).slice(0, 8)
		: COUNTRIES.slice(0, 8);

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

	function canProceed(): boolean {
		if (currentQ.id === 'gender') return quiz.gender !== '';
		if (currentQ.id === 'country') return quiz.country !== '';
		if (currentQ.id === 'preferred_styles') return quiz.preferred_styles.length > 0;
		return true;
	}

	async function finish() {
		saving = true;
		try {
			await authApi.saveQuiz(quiz);
			dispatch('complete', quiz);
		} catch {
			dispatch('complete', quiz);
		}
	}

	function next() {
		if (step < questions.length - 1) {
			step++;
		} else {
			finish();
		}
	}
</script>

<div class="max-w-md mx-auto">
	<!-- Progress bar -->
	<div class="mb-6">
		<div class="flex justify-between text-xs text-gray-500 mb-2">
			<span>Style Setup</span>
			<span>{step + 1} of {questions.length}</span>
		</div>
		<div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
			<div
				class="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500"
				style="width: {progress}%"
			/>
		</div>
	</div>

	{#key step}
	<div class="card p-6 animate-fade-in">
		<h2 class="text-xl font-semibold text-gray-900">{currentQ.question}</h2>
		{#if currentQ.subtitle}
			<p class="text-sm text-gray-500 mt-1 mb-5">{currentQ.subtitle}</p>
		{:else}
			<div class="mb-5" />
		{/if}

		<!-- Gender selection -->
		{#if currentQ.type === 'gender'}
			<div class="grid grid-cols-2 gap-3">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="p-4 rounded-xl border-2 text-sm font-medium transition-all flex flex-col items-center gap-2"
						class:border-primary-500={quiz.gender === option.value}
						class:bg-primary-50={quiz.gender === option.value}
						class:text-primary-700={quiz.gender === option.value}
						class:border-gray-200={quiz.gender !== option.value}
						class:text-gray-700={quiz.gender !== option.value}
						on:click={() => selectOption('gender', option.value)}
					>
						<span class="text-3xl">{option.emoji}</span>
						{option.label}
					</button>
				{/each}
			</div>

		<!-- Country selection -->
		{:else if currentQ.type === 'country'}
			<div class="space-y-3">
				<input
					type="text"
					placeholder="Search your country…"
					bind:value={countrySearch}
					class="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400"
				/>
				{#if quiz.country}
					<div class="flex items-center gap-2 px-3 py-2 bg-primary-50 rounded-xl border border-primary-200">
						<span class="text-lg">📍</span>
						<span class="text-sm font-medium text-primary-700">{quiz.country}</span>
						<button class="ml-auto text-primary-400 hover:text-primary-600" on:click={() => { quiz.country = ''; countrySearch = ''; }}>✕</button>
					</div>
				{/if}
				<div class="space-y-1 max-h-48 overflow-y-auto">
					{#each filteredCountries as country}
						<button
							type="button"
							class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors"
							class:bg-primary-50={quiz.country === country}
							class:text-primary-700={quiz.country === country}
							class:font-medium={quiz.country === country}
							class:hover:bg-gray-50={quiz.country !== country}
							class:text-gray-700={quiz.country !== country}
							on:click={() => { selectOption('country', country); countrySearch = ''; }}
						>
							{country}
						</button>
					{/each}
					{#if filteredCountries.length === 0}
						<p class="text-center text-sm text-gray-400 py-4">No countries found</p>
					{/if}
				</div>
			</div>

		<!-- Multi-select styles -->
		{:else if currentQ.type === 'multi'}
			<div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="p-3 rounded-xl border-2 text-sm font-medium transition-all"
						class:border-primary-500={quiz.preferred_styles.includes(option.value)}
						class:bg-primary-50={quiz.preferred_styles.includes(option.value)}
						class:text-primary-700={quiz.preferred_styles.includes(option.value)}
						class:border-gray-200={!quiz.preferred_styles.includes(option.value)}
						class:text-gray-700={!quiz.preferred_styles.includes(option.value)}
						on:click={() => toggleStyle(option.value)}
					>
						<div class="text-2xl mb-1">{option.emoji}</div>
						{option.label}
					</button>
				{/each}
			</div>

		<!-- Single select -->
		{:else if currentQ.type === 'single'}
			<div class="space-y-2">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="w-full p-3 rounded-xl border-2 text-sm font-medium text-left flex items-center gap-3 transition-all"
						class:border-primary-500={currentValue === option.value}
						class:bg-primary-50={currentValue === option.value}
						class:text-primary-700={currentValue === option.value}
						class:border-gray-200={currentValue !== option.value}
						class:text-gray-700={currentValue !== option.value}
						on:click={() => selectOption(currentQ.id, option.value)}
					>
						<span class="text-xl">{option.emoji}</span>
						{option.label}
					</button>
				{/each}
			</div>

		<!-- Range -->
		{:else if currentQ.type === 'range'}
			<div class="py-4">
				<input
					type="range"
					min="1"
					max="5"
					bind:value={quiz.formality_preference}
					class="w-full h-3 bg-gray-200 rounded-full accent-primary-600 cursor-pointer"
				/>
				<div class="flex justify-between text-xs text-gray-500 mt-2">
					{#each currentQ.labels ?? [] as label}
						<span>{label}</span>
					{/each}
				</div>
				<p class="text-center mt-4 text-sm font-medium text-primary-600">
					{currentQ.labels?.[quiz.formality_preference - 1]}
				</p>
			</div>
		{/if}

		<div class="mt-6 flex justify-between items-center">
			{#if step > 0}
				<button class="btn-ghost" on:click={() => step--}>← Back</button>
			{:else}
				<div />
			{/if}

			<button
				class="btn-primary"
				on:click={next}
				disabled={saving || !canProceed()}
			>
				{#if saving}
					Saving…
				{:else if step < questions.length - 1}
					Next →
				{:else}
					Done! 🎉
				{/if}
			</button>
		</div>
	</div>
	{/key}
</div>

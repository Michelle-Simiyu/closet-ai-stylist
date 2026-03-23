<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authApi } from '$lib/api/client';

	const dispatch = createEventDispatcher<{ complete: Record<string, unknown> }>();

	let step = 0;
	let saving = false;

	const quiz = {
		preferred_styles: [] as string[],
		formality_preference: 2,
		color_preference: 'mixed',
		occasion_priority: 'casual',
		budget_sensitivity: 'medium',
	};

	const questions = [
		{
			id: 'preferred_styles',
			question: 'What styles do you gravitate toward?',
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
			question: 'What's your typical formality level?',
			type: 'range',
			labels: ['Very Casual', 'Casual', 'Smart Casual', 'Business', 'Formal'],
		},
		{
			id: 'color_preference',
			question: 'How do you approach color?',
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

	function toggleStyle(value: string) {
		if (quiz.preferred_styles.includes(value)) {
			quiz.preferred_styles = quiz.preferred_styles.filter((s) => s !== value);
		} else {
			quiz.preferred_styles = [...quiz.preferred_styles, value];
		}
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
			<span>Style Quiz</span>
			<span>{step + 1} of {questions.length}</span>
		</div>
		<div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
			<div
				class="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500"
				style="width: {progress}%"
			/>
		</div>
	</div>

	<div class="card p-6 animate-fade-in" key={step}>
		<h2 class="text-xl font-semibold text-gray-900 mb-5">{currentQ.question}</h2>

		{#if currentQ.type === 'multi'}
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

		{:else if currentQ.type === 'single'}
			<div class="space-y-2">
				{#each currentQ.options ?? [] as option}
					<button
						type="button"
						class="w-full p-3 rounded-xl border-2 text-sm font-medium text-left flex items-center gap-3 transition-all"
						class:border-primary-500={quiz[currentQ.id as keyof typeof quiz] === option.value}
						class:bg-primary-50={quiz[currentQ.id as keyof typeof quiz] === option.value}
						class:text-primary-700={quiz[currentQ.id as keyof typeof quiz] === option.value}
						class:border-gray-200={quiz[currentQ.id as keyof typeof quiz] !== option.value}
						class:text-gray-700={quiz[currentQ.id as keyof typeof quiz] !== option.value}
						on:click={() => { (quiz as Record<string, unknown>)[currentQ.id] = option.value; }}
					>
						<span class="text-xl">{option.emoji}</span>
						{option.label}
					</button>
				{/each}
			</div>

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
				<button class="btn-ghost" on:click={() => step--}>Back</button>
			{:else}
				<div />
			{/if}

			<button class="btn-primary" on:click={next} disabled={saving}>
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
</div>

<script lang="ts">
  import AnalysisForm from "$lib/components/AnalysisForm.svelte";
  import ExportView from "$lib/components/ExportView.svelte";
  import RecommendationCard from "$lib/components/RecommendationCard.svelte";
  import SkillSection from "$lib/components/SkillSection.svelte";
  import type { AnalysisResult, View } from "$lib/types";

  let view: View = $state("form");
  let result: AnalysisResult | null = $state(null);
  let error: string | null = $state(null);

  function handleResult(json: string) {
    result = JSON.parse(json);
    view = "results";
  }

  function handleError(msg: string) {
    error = msg;
    if (view === "loading") view = "form";
  }

  function newAnalysis() {
    view = "form";
    result = null;
    error = null;
  }
</script>

<main class="min-h-screen bg-gray-50 text-gray-900">
  <header class="bg-white border-b border-gray-200 px-8 py-6">
    <div class="max-w-4xl mx-auto flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">ProjectBridge</h1>
        <p class="text-gray-500 mt-1">AI-powered skill-gap analysis for developers</p>
      </div>
      <div class="flex gap-4">
        {#if view === "results"}
          <button
            onclick={() => { view = "export"; }}
            class="text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 px-3 py-1.5 rounded-lg font-medium transition-colors"
          >
            Export
          </button>
          <button
            onclick={newAnalysis}
            class="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            New Analysis
          </button>
        {/if}
        {#if view === "export"}
          <button
            onclick={() => { view = "results"; }}
            class="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Back to Results
          </button>
        {/if}
      </div>
    </div>
  </header>

  <div class="max-w-4xl mx-auto px-8 py-8">

    {#if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-red-700 font-medium">Error</p>
            <p class="text-red-600 text-sm mt-1">{error}</p>
          </div>
          <button
            onclick={() => { error = null; }}
            class="text-red-400 hover:text-red-600 text-lg leading-none ml-4"
            aria-label="Dismiss error"
          >&times;</button>
        </div>
      </div>
    {/if}

    {#if view === "form"}
      <AnalysisForm
        onresult={handleResult}
        onerror={handleError}
        onloading={() => { view = "loading"; error = null; result = null; }}
      />
    {/if}

    {#if view === "loading"}
      <div class="text-center py-16">
        <div class="inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        <p class="text-gray-500 mt-4">Running analysis...</p>
      </div>
    {/if}

    {#if view === "results" && result}
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-green-600">{result.strengths.length}</p>
          <p class="text-sm text-gray-500">Strengths</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-amber-600">{result.gaps.length}</p>
          <p class="text-sm text-gray-500">Skill Gaps</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-blue-600">{result.recommendations.length}</p>
          <p class="text-sm text-gray-500">Recommendations</p>
        </div>
      </div>

      <div class="space-y-8">
        <SkillSection title="Strengths" skills={result.strengths} colorClass="bg-green-100 text-green-800" />
        <SkillSection title="Skill Gaps" skills={result.gaps} colorClass="bg-amber-100 text-amber-800" />

        {#if result.portfolio_insights && result.portfolio_insights.length > 0}
          <section>
            <h2 class="text-lg font-semibold mb-4">Portfolio Insights</h2>
            <div class="space-y-3">
              {#each result.portfolio_insights as insight}
                <div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <div class="flex items-start gap-3">
                    <span class="text-xs font-medium text-amber-600 uppercase tracking-wide bg-amber-100 px-2 py-0.5 rounded shrink-0 mt-0.5">{insight.category}</span>
                    <p class="text-sm text-amber-900">{insight.message}</p>
                  </div>
                </div>
              {/each}
            </div>
          </section>
        {/if}

        <section>
          <h2 class="text-lg font-semibold mb-4">Recommendations</h2>
          {#if result.recommendations.length === 0}
            <p class="text-gray-400 text-sm">No recommendations generated.</p>
          {:else}
            <div class="space-y-6">
              {#each result.recommendations as rec, i}
                <RecommendationCard {rec} index={i} {result} onerror={handleError} />
              {/each}
            </div>
          {/if}
        </section>

        <div class="flex justify-center gap-6 pt-4 pb-8">
          <button
            onclick={() => { view = "export"; }}
            class="bg-gray-100 text-gray-700 hover:bg-gray-200 px-5 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Export Results
          </button>
          <button
            onclick={newAnalysis}
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            New Analysis
          </button>
        </div>
      </div>
    {/if}

    {#if view === "export" && result}
      <ExportView {result} onerror={handleError} />
    {/if}
  </div>
</main>

<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";

  interface Skill {
    name: string;
    category: string;
  }

  interface Recommendation {
    title: string;
    description: string;
    skills_addressed: string[];
    estimated_scope: string;
  }

  interface AnalysisResult {
    schema_version: string;
    strengths: Skill[];
    gaps: Skill[];
    recommendations: Recommendation[];
  }

  let result: AnalysisResult | null = $state(null);
  let error: string | null = $state(null);
  let loading = $state(false);

  async function runExample() {
    loading = true;
    error = null;
    result = null;

    try {
      const json = await invoke<string>("run_analysis", {
        args: ["analyze", "--example", "--no-ai"],
      });
      result = JSON.parse(json);
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }
</script>

<main class="min-h-screen bg-gray-50 text-gray-900">
  <header class="bg-white border-b border-gray-200 px-8 py-6">
    <h1 class="text-2xl font-bold">ProjectBridge</h1>
    <p class="text-gray-500 mt-1">AI-powered skill-gap analysis for developers</p>
  </header>

  <div class="max-w-4xl mx-auto px-8 py-8">
    {#if !result && !loading}
      <div class="text-center py-16">
        <h2 class="text-xl font-semibold mb-4">Ready to analyze</h2>
        <p class="text-gray-500 mb-8">
          Run an example analysis to see ProjectBridge in action.
        </p>
        <button
          onclick={runExample}
          class="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Run Example Analysis
        </button>
      </div>
    {/if}

    {#if loading}
      <div class="text-center py-16">
        <div class="inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        <p class="text-gray-500 mt-4">Running analysis...</p>
      </div>
    {/if}

    {#if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-700 font-medium">Error</p>
        <p class="text-red-600 text-sm mt-1">{error}</p>
      </div>
    {/if}

    {#if result}
      <div class="space-y-8">
        <!-- Strengths -->
        <section>
          <h2 class="text-lg font-semibold mb-3">Strengths</h2>
          <div class="flex flex-wrap gap-2">
            {#each result.strengths as skill}
              <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                {skill.name}
              </span>
            {/each}
            {#if result.strengths.length === 0}
              <p class="text-gray-400 text-sm">No strengths detected.</p>
            {/if}
          </div>
        </section>

        <!-- Gaps -->
        <section>
          <h2 class="text-lg font-semibold mb-3">Skill Gaps</h2>
          <div class="flex flex-wrap gap-2">
            {#each result.gaps as skill}
              <span class="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium">
                {skill.name}
              </span>
            {/each}
            {#if result.gaps.length === 0}
              <p class="text-gray-400 text-sm">No gaps detected.</p>
            {/if}
          </div>
        </section>

        <!-- Recommendations -->
        <section>
          <h2 class="text-lg font-semibold mb-3">Recommendations</h2>
          <div class="space-y-4">
            {#each result.recommendations as rec}
              <div class="bg-white border border-gray-200 rounded-lg p-5">
                <div class="flex items-start justify-between">
                  <h3 class="font-medium">{rec.title}</h3>
                  <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded ml-3 shrink-0">
                    {rec.estimated_scope}
                  </span>
                </div>
                <p class="text-gray-600 text-sm mt-2">{rec.description}</p>
                <div class="flex gap-2 mt-3">
                  {#each rec.skills_addressed as skill}
                    <span class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                      {skill}
                    </span>
                  {/each}
                </div>
              </div>
            {/each}
            {#if result.recommendations.length === 0}
              <p class="text-gray-400 text-sm">No recommendations generated.</p>
            {/if}
          </div>
        </section>

        <!-- Run again -->
        <div class="text-center pt-4">
          <button
            onclick={runExample}
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Run again
          </button>
        </div>
      </div>
    {/if}
  </div>
</main>

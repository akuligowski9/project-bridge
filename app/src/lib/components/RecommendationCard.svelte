<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { save } from "@tauri-apps/plugin-dialog";
  import { writeText } from "@tauri-apps/plugin-clipboard-manager";
  import { writeTextFile } from "@tauri-apps/plugin-fs";
  import {
    scopeStyles,
    tierTabs,
    type AnalysisResult,
    type ProjectSpec,
  } from "$lib/types";

  interface Props {
    rec: { title: string; description: string; skills_addressed: string[]; estimated_scope: string; skill_context?: string | null };
    index: number;
    result: AnalysisResult;
    onerror: (msg: string) => void;
  }

  let { rec, index, result, onerror }: Props = $props();

  let selectedTier = $state("");
  let specCache: Record<string, ProjectSpec> = $state({});
  let specLoadingKey = $state<string | null>(null);
  let specExportCopied = $state(false);

  let cacheKey = $derived(`${index}-${selectedTier}`);
  let spec = $derived(selectedTier ? specCache[cacheKey] : null);
  let isLoading = $derived(specLoadingKey === cacheKey);

  async function selectTier(difficulty: string) {
    if (selectedTier === difficulty) {
      selectedTier = "";
      return;
    }
    selectedTier = difficulty;

    const cacheKey = `${index}-${difficulty}`;
    if (specCache[cacheKey]) return;

    specLoadingKey = cacheKey;
    try {
      const analysisJson = JSON.stringify(result);
      const jsonStr = await invoke<string>("export_project_spec", {
        analysisJson,
        recommendationIndex: index + 1,
        difficulty,
        format: "json",
        noAi: true,
      });
      specCache[cacheKey] = JSON.parse(jsonStr);
    } catch (e) {
      onerror(String(e));
    } finally {
      specLoadingKey = null;
    }
  }

  async function fetchSpecMarkdown(): Promise<string | null> {
    if (!selectedTier) return null;
    try {
      const analysisJson = JSON.stringify(result);
      return await invoke<string>("export_project_spec", {
        analysisJson,
        recommendationIndex: index + 1,
        difficulty: selectedTier,
        format: "markdown",
        noAi: true,
      });
    } catch (e) {
      onerror(String(e));
      return null;
    }
  }

  async function exportSpecMarkdown() {
    const markdown = await fetchSpecMarkdown();
    if (!markdown) return;
    const path = await save({
      defaultPath: "project-spec.md",
      filters: [{ name: "Markdown", extensions: ["md"] }],
    });
    if (path) {
      try {
        await writeTextFile(path, markdown);
      } catch (e) {
        onerror(String(e));
      }
    }
  }

  async function copySpecMarkdown() {
    const markdown = await fetchSpecMarkdown();
    if (!markdown) return;
    await writeText(markdown);
    specExportCopied = true;
    setTimeout(() => { specExportCopied = false; }, 2000);
  }
</script>

<div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
  <div class="p-5">
    <div class="flex items-start justify-between gap-3">
      <h3 class="font-semibold text-base">{rec.title}</h3>
      <span class="text-xs px-2 py-1 rounded shrink-0 {scopeStyles[rec.estimated_scope] || 'bg-gray-100 text-gray-600'}">
        {rec.estimated_scope}
      </span>
    </div>

    <div class="flex flex-wrap gap-2 mt-2">
      {#each rec.skills_addressed as skill}
        <span class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">{skill}</span>
      {/each}
    </div>

    <p class="text-sm text-gray-700 leading-relaxed mt-4">{rec.description}</p>

    {#if rec.skill_context}
      <div class="bg-blue-50 border-l-4 border-blue-300 p-3 mt-4 rounded-r">
        <p class="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-1">Why These Skills Matter</p>
        <p class="text-sm text-blue-900 italic">{rec.skill_context}</p>
      </div>
    {/if}
  </div>

  <!-- Tier tabs -->
  <div class="border-t border-gray-200 bg-gray-50 px-5 py-3">
    <div class="flex gap-2">
      {#each tierTabs as tab}
        <button
          onclick={() => selectTier(tab.key)}
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-all {selectedTier === tab.key ? tab.active : tab.inactive}"
        >
          {tab.label}
          <span class="text-xs font-normal ml-1">({tab.count})</span>
        </button>
      {/each}
    </div>
  </div>

  <!-- Expanded tier content -->
  {#if selectedTier}
    <div class="p-5 border-t border-gray-200">
      {#if isLoading}
        <div class="text-center py-6">
          <div class="inline-block w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
          <p class="text-gray-400 text-xs mt-2">Loading {selectedTier} spec...</p>
        </div>
      {:else if spec}
        {@const specParagraphs = spec.description.split("\n\n")}
        {#if specParagraphs.length > 1}
          <div class="space-y-3 mb-5">
            {#each specParagraphs.slice(1) as paragraph}
              <p class="text-sm text-gray-700 leading-relaxed">{paragraph}</p>
            {/each}
          </div>
        {/if}

        <div class="mb-5">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Key Features</h4>
          <ol class="space-y-2">
            {#each spec.features as feature, fi}
              <li class="text-sm text-gray-700 flex gap-2.5">
                <span class="text-gray-400 font-mono text-xs mt-0.5 shrink-0">{fi + 1}.</span>
                {feature}
              </li>
            {/each}
          </ol>
        </div>

        {#if spec.doc_links && spec.doc_links.length > 0}
          <div class="mb-5">
            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Documentation & Resources</h4>
            <div class="space-y-1">
              {#each spec.doc_links as link}
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-gray-500 font-medium">{link.skill}</span>
                  <span class="text-gray-300">&mdash;</span>
                  <a href={link.url} target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 hover:underline">{link.label}</a>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <div class="flex gap-2 pt-3 border-t border-gray-100">
          <button
            onclick={exportSpecMarkdown}
            class="text-xs bg-blue-600 text-white px-4 py-1.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Save Project Spec
          </button>
          <button
            onclick={copySpecMarkdown}
            class="text-xs bg-gray-100 text-gray-700 px-4 py-1.5 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            {specExportCopied ? "Copied!" : "Copy to Clipboard"}
          </button>
        </div>
      {/if}
    </div>
  {/if}
</div>

<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { open } from "@tauri-apps/plugin-dialog";
  import { readTextFile } from "@tauri-apps/plugin-fs";

  interface Props {
    onresult: (json: string) => void;
    onerror: (msg: string) => void;
    onloading: () => void;
  }

  let { onresult, onerror, onloading }: Props = $props();

  let githubUser = $state("");
  let jobText = $state("");
  let resumeText = $state("");
  let provider = $state("none");
  let apiKey = $state("");
  let ollamaModels: string[] = $state([]);
  let ollamaModel = $state("");
  let ollamaChecking = $state(false);
  let ollamaError: string | null = $state(null);

  let submitted = $state(false);
  let githubUserError = $derived(
    submitted && githubUser.trim() === "" ? "GitHub username is required." : null
  );
  let jobTextError = $derived(
    submitted && jobText.trim() === "" ? "Job description is required." : null
  );

  async function loadResumeFile() {
    const path = await open({
      filters: [{ name: "Text Files", extensions: ["txt", "md", "text"] }],
    });
    if (path) {
      resumeText = await readTextFile(path);
    }
  }

  async function checkOllamaModels() {
    ollamaChecking = true;
    ollamaError = null;
    ollamaModels = [];
    ollamaModel = "";
    try {
      const models = await invoke<string[]>("list_ollama_models");
      ollamaModels = models;
      if (models.length > 0) {
        ollamaModel = models[0];
      }
    } catch (e) {
      ollamaError = String(e);
    } finally {
      ollamaChecking = false;
    }
  }

  function handleProviderChange(e: Event) {
    const target = e.target as HTMLSelectElement;
    provider = target.value;
    apiKey = "";
    ollamaError = null;
    if (provider === "ollama") {
      checkOllamaModels();
    }
  }

  async function handleSubmit() {
    submitted = true;
    if (githubUser.trim() === "" || jobText.trim() === "") return;

    onloading();

    try {
      const json = await invoke<string>("run_analysis_form", {
        githubUser: githubUser.trim(),
        jobText: jobText.trim(),
        resumeText: resumeText.trim() || null,
        provider,
        apiKey: apiKey.trim() || null,
        ollamaModel: ollamaModel.trim() || null,
      });
      onresult(json);
    } catch (e) {
      onerror(String(e));
    }
  }

  async function runExample() {
    onloading();
    try {
      const json = await invoke<string>("run_analysis", {
        args: ["analyze", "--example", "--no-ai"],
      });
      onresult(json);
    } catch (e) {
      onerror(String(e));
    }
  }
</script>

<div class="bg-white border border-gray-200 rounded-lg p-6">
  <h2 class="text-lg font-semibold mb-6">Run Analysis</h2>

  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
    <div>
      <label for="github-user" class="block text-sm font-medium text-gray-700 mb-1">
        GitHub Username <span class="text-red-500">*</span>
      </label>
      <input
        id="github-user"
        type="text"
        bind:value={githubUser}
        placeholder="e.g. octocat or https://github.com/octocat"
        class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {githubUserError ? 'border-red-300' : 'border-gray-300'}"
      />
      {#if githubUserError}
        <p class="text-red-500 text-xs mt-1">{githubUserError}</p>
      {/if}
    </div>

    <div>
      <label for="job-text" class="block text-sm font-medium text-gray-700 mb-1">
        Job Description <span class="text-red-500">*</span>
      </label>
      <textarea
        id="job-text"
        bind:value={jobText}
        rows={6}
        placeholder="Paste job description text or a URL to the posting..."
        class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y {jobTextError ? 'border-red-300' : 'border-gray-300'}"
      ></textarea>
      {#if jobTextError}
        <p class="text-red-500 text-xs mt-1">{jobTextError}</p>
      {/if}
    </div>

    <div>
      <div class="flex items-center justify-between mb-1">
        <label for="resume-text" class="text-sm font-medium text-gray-700">
          Resume Text <span class="text-gray-400 font-normal">(optional)</span>
        </label>
        <button
          type="button"
          onclick={loadResumeFile}
          class="text-xs text-blue-600 hover:text-blue-800 font-medium"
        >
          Load from file...
        </button>
      </div>
      <textarea
        id="resume-text"
        bind:value={resumeText}
        rows={4}
        placeholder="Paste your resume text for enriched analysis..."
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
      ></textarea>
    </div>

    <div>
      <label for="provider" class="block text-sm font-medium text-gray-700 mb-1">
        AI Provider
      </label>
      <select
        id="provider"
        value={provider}
        onchange={handleProviderChange}
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
      >
        <option value="none">None (heuristic only)</option>
        <option value="openai">OpenAI</option>
        <option value="anthropic">Anthropic</option>
        <option value="ollama">Ollama (local)</option>
      </select>
    </div>

    {#if provider === "openai" || provider === "anthropic"}
      <div>
        <label for="api-key" class="block text-sm font-medium text-gray-700 mb-1">
          API Key
        </label>
        <input
          id="api-key"
          type="password"
          bind:value={apiKey}
          placeholder={provider === "openai" ? "sk-..." : "sk-ant-..."}
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <p class="text-xs text-gray-400 mt-1">Not stored. Falls back to env var if empty.</p>
      </div>
    {/if}

    {#if provider === "ollama"}
      <div>
        <div class="flex items-center gap-2 mb-1">
          <label for="ollama-model" class="text-sm font-medium text-gray-700">Model</label>
          {#if ollamaChecking}
            <div class="inline-block w-3 h-3 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
          {:else if ollamaModels.length > 0}
            <span class="inline-block w-2 h-2 rounded-full bg-green-500" title="Connected"></span>
          {:else if ollamaError}
            <span class="inline-block w-2 h-2 rounded-full bg-red-500" title="Unreachable"></span>
          {/if}
        </div>
        {#if ollamaModels.length > 0}
          <select
            id="ollama-model"
            bind:value={ollamaModel}
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
          >
            {#each ollamaModels as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        {:else if ollamaError}
          <p class="text-red-500 text-xs">{ollamaError}</p>
        {:else if !ollamaChecking}
          <p class="text-gray-400 text-xs">Checking Ollama server...</p>
        {/if}
        <button
          type="button"
          onclick={checkOllamaModels}
          class="text-xs text-blue-600 hover:text-blue-800 font-medium mt-1"
        >
          Refresh models
        </button>
      </div>
    {/if}

    <div class="flex items-center gap-4 pt-2">
      <button
        type="submit"
        class="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm"
      >
        Analyze
      </button>
      <button
        type="button"
        onclick={runExample}
        class="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        Run Example Instead
      </button>
    </div>
  </form>
</div>

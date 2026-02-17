<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { save } from "@tauri-apps/plugin-dialog";
  import { writeText } from "@tauri-apps/plugin-clipboard-manager";
  import { writeTextFile } from "@tauri-apps/plugin-fs";
  import type { AnalysisResult } from "$lib/types";

  interface Props {
    result: AnalysisResult;
    onerror: (msg: string) => void;
  }

  let { result, onerror }: Props = $props();

  let exportFormat = $state<"json" | "markdown">("markdown");
  let exportPreview = $state("");
  let exportLoading = $state(false);
  let copied = $state(false);

  async function generatePreview() {
    exportLoading = true;
    copied = false;
    try {
      const analysisJson = JSON.stringify(result);
      exportPreview = await invoke<string>("export_analysis", {
        analysisJson,
        format: exportFormat,
      });
    } catch (e) {
      onerror(String(e));
    } finally {
      exportLoading = false;
    }
  }

  async function handleFormatChange(fmt: "json" | "markdown") {
    exportFormat = fmt;
    await generatePreview();
  }

  async function saveToFile() {
    const ext = exportFormat === "markdown" ? "md" : "json";
    const path = await save({
      defaultPath: `projectbridge-analysis.${ext}`,
      filters: [
        {
          name: exportFormat === "markdown" ? "Markdown" : "JSON",
          extensions: [ext],
        },
      ],
    });
    if (path) {
      try {
        await writeTextFile(path, exportPreview);
      } catch (e) {
        onerror(String(e));
      }
    }
  }

  async function copyToClipboard() {
    try {
      await writeText(exportPreview);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    } catch (e) {
      onerror(String(e));
    }
  }

  // Generate preview on mount.
  $effect(() => {
    generatePreview();
  });
</script>

<div class="space-y-6">
  <div class="bg-white border border-gray-200 rounded-lg p-6">
    <h2 class="text-lg font-semibold mb-4">Export Analysis</h2>
    <div class="flex gap-3 mb-4">
      <button
        onclick={() => handleFormatChange("markdown")}
        class="px-4 py-2 rounded-lg text-sm font-medium transition-colors {exportFormat === 'markdown' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
      >
        Markdown
      </button>
      <button
        onclick={() => handleFormatChange("json")}
        class="px-4 py-2 rounded-lg text-sm font-medium transition-colors {exportFormat === 'json' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
      >
        JSON
      </button>
    </div>
    <div class="flex gap-3">
      <button
        onclick={saveToFile}
        disabled={exportLoading}
        class="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
      >
        Save to File
      </button>
      <button
        onclick={copyToClipboard}
        disabled={exportLoading}
        class="bg-gray-100 text-gray-700 px-5 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
      >
        {copied ? "Copied!" : "Copy to Clipboard"}
      </button>
    </div>
  </div>

  <div class="bg-white border border-gray-200 rounded-lg p-6">
    <h3 class="text-sm font-medium text-gray-500 mb-3">Preview</h3>
    {#if exportLoading}
      <div class="text-center py-8">
        <div class="inline-block w-6 h-6 border-3 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
    {:else}
      <pre class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs text-gray-700 overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">{exportPreview}</pre>
    {/if}
  </div>
</div>

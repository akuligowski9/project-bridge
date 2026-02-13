<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { save } from "@tauri-apps/plugin-dialog";
  import { writeText } from "@tauri-apps/plugin-clipboard-manager";
  import { writeTextFile } from "@tauri-apps/plugin-fs";

  interface Skill {
    name: string;
    category: string;
  }

  interface Recommendation {
    title: string;
    description: string;
    skills_addressed: string[];
    estimated_scope: string;
    skill_context?: string | null;
  }

  interface AnalysisResult {
    schema_version: string;
    strengths: Skill[];
    gaps: Skill[];
    recommendations: Recommendation[];
  }

  type View = "form" | "loading" | "results" | "export";

  let view: View = $state("results");
  let result: AnalysisResult | null = $state({
    schema_version: "1.1",
    strengths: [
      { name: "Python", category: "language" },
      { name: "JavaScript", category: "language" },
      { name: "React", category: "framework" },
      { name: "Flask", category: "framework" },
      { name: "Docker", category: "infrastructure" },
      { name: "GitHub Actions", category: "infrastructure" },
    ],
    gaps: [
      { name: "TypeScript", category: "language" },
      { name: "Django", category: "framework" },
      { name: "FastAPI", category: "framework" },
      { name: "PostgreSQL", category: "tool" },
      { name: "Redis", category: "tool" },
      { name: "Kubernetes", category: "infrastructure" },
      { name: "AWS", category: "infrastructure" },
    ],
    recommendations: [
      {
        title: "Build a REST API with Django",
        description: "Create a RESTful API using Django REST Framework. Implement CRUD endpoints for a resource (e.g., a task manager), add authentication, and write API documentation with Swagger/OpenAPI.",
        skills_addressed: ["Django", "REST API"],
        estimated_scope: "medium",
        skill_context: "Django powers a huge portion of production web applications, from startups to enterprises like Instagram and Mozilla. Teams value developers who can ship complete backend features — models, views, serializers, auth — without hand-holding. Understanding Django's conventions makes you productive on day one in most Python web shops.",
      },
      {
        title: "Deploy a containerized app with Kubernetes",
        description: "Dockerize a simple web application, create Kubernetes manifests, and deploy to a local cluster (minikube or kind). Practice pod management, services, and basic scaling.",
        skills_addressed: ["Docker", "Kubernetes"],
        estimated_scope: "medium",
        skill_context: "Containerization is how modern engineering teams ship software reliably. Understanding Docker and Kubernetes means you can participate in deployment conversations, debug production issues, and work effectively with DevOps and platform teams. These skills transfer across every company and tech stack.",
      },
      {
        title: "Build a microservice with FastAPI and Redis",
        description: "Create a FastAPI microservice with Redis for caching and rate limiting. Implement async endpoints, background tasks, and health checks. Containerize with Docker.",
        skills_addressed: ["FastAPI", "Redis", "Docker"],
        estimated_scope: "medium",
        skill_context: "Production backend systems rely on caching and async processing to handle real-world traffic. FastAPI's async-first design reflects where the Python ecosystem is heading, and Redis is the de facto standard for caching and message brokering. Understanding these tools shows you can build services that perform under load.",
      },
      {
        title: "Build a full-stack app with Next.js and PostgreSQL",
        description: "Create a full-stack application using Next.js with server-side rendering, API routes, and PostgreSQL for persistence. Implement user authentication and deploy to Vercel.",
        skills_addressed: ["Next.js", "PostgreSQL", "TypeScript"],
        estimated_scope: "large",
        skill_context: "Full-stack TypeScript with a relational database is the bread and butter of modern product engineering. Teams need developers who can own features end-to-end — from the database schema through the API to the rendered page. This combination is the most in-demand skill set across startups and mid-size companies.",
      },
      {
        title: "Deploy a serverless API on AWS Lambda",
        description: "Build a serverless REST API using AWS Lambda and API Gateway. Implement DynamoDB for storage, configure IAM roles, and automate deployment with SAM or CDK.",
        skills_addressed: ["AWS", "Serverless"],
        estimated_scope: "medium",
        skill_context: "Cloud infrastructure is a fundamental part of modern software delivery, and AWS dominates the market. Understanding serverless architecture shows you can think about cost, scalability, and operational concerns — not just application code. These skills make you more valuable in any engineering team that deploys to the cloud.",
      },
    ],
  });
  let error: string | null = $state(null);

  // Form fields
  let githubUser = $state("");
  let jobText = $state("");
  let resumeText = $state("");
  let noAi = $state(false);

  // Validation
  let submitted = $state(false);
  let githubUserError = $derived(
    submitted && githubUser.trim() === "" ? "GitHub username is required." : null
  );
  let jobTextError = $derived(
    submitted && jobText.trim() === "" ? "Job description is required." : null
  );

  // Export state
  let exportFormat = $state<"json" | "markdown">("markdown");
  let exportPreview = $state("");
  let exportLoading = $state(false);
  let copied = $state(false);

  const categoryLabels: Record<string, string> = {
    language: "Languages",
    framework: "Frameworks",
    infrastructure: "Infrastructure",
    tool: "Tools",
    concept: "Concepts",
  };

  const scopeStyles: Record<string, string> = {
    small: "bg-green-100 text-green-700",
    medium: "bg-amber-100 text-amber-700",
    large: "bg-red-100 text-red-700",
  };

  function groupByCategory(skills: Skill[]): Record<string, Skill[]> {
    const groups: Record<string, Skill[]> = {};
    for (const skill of skills) {
      const cat = skill.category || "concept";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(skill);
    }
    return groups;
  }

  async function handleSubmit() {
    submitted = true;
    if (githubUser.trim() === "" || jobText.trim() === "") return;

    view = "loading";
    error = null;
    result = null;

    try {
      const json = await invoke<string>("run_analysis_form", {
        githubUser: githubUser.trim(),
        jobText: jobText.trim(),
        resumeText: resumeText.trim() || null,
        noAi,
      });
      result = JSON.parse(json);
      view = "results";
    } catch (e) {
      error = String(e);
      view = "form";
    }
  }

  async function runExample() {
    view = "loading";
    error = null;
    result = null;

    try {
      const json = await invoke<string>("run_analysis", {
        args: ["analyze", "--example", "--no-ai"],
      });
      result = JSON.parse(json);
      view = "results";
    } catch (e) {
      error = String(e);
      view = "form";
    }
  }

  function newAnalysis() {
    view = "form";
    result = null;
    error = null;
    submitted = false;
  }

  async function openExport() {
    view = "export";
    await generatePreview();
  }

  async function generatePreview() {
    if (!result) return;
    exportLoading = true;
    copied = false;
    try {
      const analysisJson = JSON.stringify(result);
      exportPreview = await invoke<string>("export_analysis", {
        analysisJson,
        format: exportFormat,
      });
    } catch (e) {
      error = String(e);
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
        error = String(e);
      }
    }
  }

  async function copyToClipboard() {
    try {
      await writeText(exportPreview);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    } catch (e) {
      error = String(e);
    }
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
            onclick={openExport}
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

    <!-- INPUT FORM -->
    {#if view === "form"}
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-lg font-semibold mb-6">Run Analysis</h2>

        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
          <!-- GitHub Username -->
          <div>
            <label for="github-user" class="block text-sm font-medium text-gray-700 mb-1">
              GitHub Username <span class="text-red-500">*</span>
            </label>
            <input
              id="github-user"
              type="text"
              bind:value={githubUser}
              placeholder="e.g. octocat"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {githubUserError ? 'border-red-300' : 'border-gray-300'}"
            />
            {#if githubUserError}
              <p class="text-red-500 text-xs mt-1">{githubUserError}</p>
            {/if}
          </div>

          <!-- Job Description -->
          <div>
            <label for="job-text" class="block text-sm font-medium text-gray-700 mb-1">
              Job Description <span class="text-red-500">*</span>
            </label>
            <textarea
              id="job-text"
              bind:value={jobText}
              rows={6}
              placeholder="Paste the job description here..."
              class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y {jobTextError ? 'border-red-300' : 'border-gray-300'}"
            ></textarea>
            {#if jobTextError}
              <p class="text-red-500 text-xs mt-1">{jobTextError}</p>
            {/if}
          </div>

          <!-- Resume (optional) -->
          <div>
            <label for="resume-text" class="block text-sm font-medium text-gray-700 mb-1">
              Resume Text <span class="text-gray-400 font-normal">(optional)</span>
            </label>
            <textarea
              id="resume-text"
              bind:value={resumeText}
              rows={4}
              placeholder="Paste your resume text for enriched analysis..."
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
            ></textarea>
          </div>

          <!-- No AI toggle -->
          <div class="flex items-center gap-2">
            <input
              id="no-ai"
              type="checkbox"
              bind:checked={noAi}
              class="rounded border-gray-300"
            />
            <label for="no-ai" class="text-sm text-gray-700">
              Heuristic only (no AI provider)
            </label>
          </div>

          <!-- Actions -->
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
    {/if}

    <!-- LOADING -->
    {#if view === "loading"}
      <div class="text-center py-16">
        <div class="inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        <p class="text-gray-500 mt-4">Running analysis...</p>
      </div>
    {/if}

    <!-- RESULTS DASHBOARD -->
    {#if view === "results" && result}
      <!-- Summary bar -->
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
        <!-- Strengths -->
        <section class="bg-white border border-gray-200 rounded-lg p-6">
          <h2 class="text-lg font-semibold mb-4">Strengths</h2>
          {#if result.strengths.length === 0}
            <p class="text-gray-400 text-sm">No strengths detected.</p>
          {:else}
            {@const groups = groupByCategory(result.strengths)}
            <div class="space-y-3">
              {#each Object.entries(groups) as [cat, skills]}
                <div>
                  <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1.5">
                    {categoryLabels[cat] || cat}
                  </p>
                  <div class="flex flex-wrap gap-2">
                    {#each skills as skill}
                      <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                        {skill.name}
                      </span>
                    {/each}
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </section>

        <!-- Gaps -->
        <section class="bg-white border border-gray-200 rounded-lg p-6">
          <h2 class="text-lg font-semibold mb-4">Skill Gaps</h2>
          {#if result.gaps.length === 0}
            <p class="text-gray-400 text-sm">No gaps detected.</p>
          {:else}
            {@const groups = groupByCategory(result.gaps)}
            <div class="space-y-3">
              {#each Object.entries(groups) as [cat, skills]}
                <div>
                  <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1.5">
                    {categoryLabels[cat] || cat}
                  </p>
                  <div class="flex flex-wrap gap-2">
                    {#each skills as skill}
                      <span class="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium">
                        {skill.name}
                      </span>
                    {/each}
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </section>

        <!-- Recommendations -->
        <section>
          <h2 class="text-lg font-semibold mb-4">Recommendations</h2>
          {#if result.recommendations.length === 0}
            <p class="text-gray-400 text-sm">No recommendations generated.</p>
          {:else}
            <div class="space-y-4">
              {#each result.recommendations as rec}
                <div class="bg-white border border-gray-200 rounded-lg p-5">
                  <div class="flex items-start justify-between gap-3">
                    <h3 class="font-medium">{rec.title}</h3>
                    <span class="text-xs px-2 py-1 rounded shrink-0 {scopeStyles[rec.estimated_scope] || 'bg-gray-100 text-gray-600'}">
                      {rec.estimated_scope}
                    </span>
                  </div>
                  <p class="text-gray-600 text-sm mt-2">{rec.description}</p>
                  {#if rec.skill_context}
                    <div class="bg-blue-50 border-l-4 border-blue-300 p-3 mt-3 rounded-r">
                      <p class="text-sm text-blue-900 italic">{rec.skill_context}</p>
                    </div>
                  {/if}
                  <div class="flex flex-wrap gap-2 mt-3">
                    {#each rec.skills_addressed as skill}
                      <span class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                        {skill}
                      </span>
                    {/each}
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </section>

        <!-- Actions -->
        <div class="flex justify-center gap-6 pt-4 pb-8">
          <button
            onclick={openExport}
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

    <!-- EXPORT VIEW -->
    {#if view === "export" && result}
      <div class="space-y-6">
        <!-- Format selector -->
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

          <!-- Action buttons -->
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

        <!-- Preview -->
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
    {/if}
  </div>
</main>

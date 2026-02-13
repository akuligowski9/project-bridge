# AI Setup Guide

ProjectBridge works out of the box with **no AI** — the heuristic engine analyzes your GitHub repos, detects skill gaps, and generates recommendations using curated templates. AI enhances the results with richer descriptions and more personalized suggestions, but it's entirely optional.

The recommended AI provider is **Ollama** — it's free, runs locally, and keeps all your data on your machine.

---

## Option 1: Ollama (Free, Local, Recommended)

[Ollama](https://ollama.com) runs open-source AI models on your computer. No API keys, no accounts, no cost.

### Step 1: Install Ollama

**macOS:**

```bash
brew install ollama
```

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**

Download the installer from [ollama.com/download](https://ollama.com/download).

### Step 2: Start Ollama and pull a model

```bash
# Start the Ollama server (runs in the background)
ollama serve
```

In a new terminal, pull the default model:

```bash
ollama pull llama3.2
```

This downloads ~2GB. You only need to do this once. The `llama3.2` model works well for ProjectBridge's recommendation generation and context analysis.

> **Smaller machine?** Try `ollama pull llama3.2:1b` for a lighter 1B parameter model. Larger machine? `ollama pull llama3.1:8b` gives better results.

### Step 3: Configure ProjectBridge

Create a `projectbridge.config.yaml` in your working directory (or wherever you run ProjectBridge from):

```yaml
ai:
  provider: ollama
```

That's it. Run an analysis:

```bash
projectbridge analyze --example
```

You should see the AI spinner while Ollama processes. Results will include AI-enhanced recommendation descriptions and richer skill context.

### Step 4 (Optional): Use a different model

If you pulled a different model, specify it in the config:

```yaml
ai:
  provider: ollama
  ollama_model: llama3.1:8b
```

### Troubleshooting

**"Cannot reach Ollama at http://localhost:11434"**

Ollama isn't running. Start it with `ollama serve` (or open the Ollama desktop app on macOS/Windows).

**Slow responses**

Ollama runs on your CPU by default. First-time inference is slower as the model loads into memory. Subsequent calls are faster. If you have a GPU, Ollama will use it automatically on supported hardware.

**Model not found**

Make sure you pulled the model: `ollama list` shows installed models. Pull one with `ollama pull llama3.2`.

---

## Option 2: No AI (Default)

If you don't configure any provider, ProjectBridge uses its built-in heuristic engine. This is what runs when you use `--no-ai` or have no config file.

What you get without AI:
- Full skill gap detection (strengths, gaps, adjacent skills)
- Template-based project recommendations (31 curated templates)
- Experience level inference and difficulty calibration
- Portfolio insights and interview topics

What AI adds:
- Richer, more contextual recommendation descriptions
- Personalized suggestions that reference your specific skill combinations
- Enhanced context analysis of your developer profile

The heuristic engine is deterministic, fast, and produces solid results. Many users find it sufficient.

---

## Option 3: Paid Providers (OpenAI, Anthropic)

If you already have an API key for OpenAI or Anthropic, you can use it with ProjectBridge. These are not required and are not free.

### OpenAI

```bash
pip install projectbridge[openai]
export OPENAI_API_KEY="sk-..."
```

```yaml
ai:
  provider: openai
```

### Anthropic

```bash
pip install projectbridge[anthropic]
export ANTHROPIC_API_KEY="sk-ant-..."
```

```yaml
ai:
  provider: anthropic
```

Both use their respective chat APIs and cost a few cents per analysis run. See their pricing pages for details.

---

## Using AI in the Desktop App

The Tauri desktop app reads the same `projectbridge.config.yaml` file. Place it in the directory where you launch the app, and toggle the "Heuristic only" checkbox off in the input form to use your configured AI provider.

---

## Prompts Are Transparent

All prompts sent to AI providers are stored as plain text files you can read and edit:

```
engine/projectbridge/ai/prompts/
├── analyze_context.txt
└── generate_recommendations.txt
```

No hidden instructions. No data sent anywhere you can't inspect.

<script lang="ts">
  import { categoryLabels, groupByCategory, type Skill } from "$lib/types";

  interface Props {
    title: string;
    skills: Skill[];
    colorClass: string;
  }

  let { title, skills, colorClass }: Props = $props();
</script>

<section class="bg-white border border-gray-200 rounded-lg p-6">
  <h2 class="text-lg font-semibold mb-4">{title}</h2>
  {#if skills.length === 0}
    <p class="text-gray-400 text-sm">No {title.toLowerCase()} detected.</p>
  {:else}
    {@const groups = groupByCategory(skills)}
    <div class="space-y-3">
      {#each Object.entries(groups) as [cat, catSkills]}
        <div>
          <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1.5">{categoryLabels[cat] || cat}</p>
          <div class="flex flex-wrap gap-2">
            {#each catSkills as skill}
              <span class="{colorClass} px-3 py-1 rounded-full text-sm font-medium">{skill.name}</span>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

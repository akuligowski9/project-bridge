export interface Skill {
  name: string;
  category: string;
}

export interface Recommendation {
  title: string;
  description: string;
  skills_addressed: string[];
  estimated_scope: string;
  skill_context?: string | null;
}

export interface PortfolioInsight {
  category: string;
  message: string;
}

export interface AnalysisResult {
  schema_version: string;
  strengths: Skill[];
  gaps: Skill[];
  recommendations: Recommendation[];
  portfolio_insights?: PortfolioInsight[];
}

export interface DocLink {
  label: string;
  url: string;
  skill: string;
}

export interface ProjectSpec {
  title: string;
  difficulty: string;
  description: string;
  features: string[];
  skills_addressed: string[];
  why_skills_matter: string;
  doc_links: DocLink[];
  strengths_referenced: string[];
}

export type View = "form" | "loading" | "results" | "export";

export const categoryLabels: Record<string, string> = {
  language: "Languages",
  framework: "Frameworks",
  infrastructure: "Infrastructure",
  tool: "Tools",
  concept: "Concepts",
};

export const scopeStyles: Record<string, string> = {
  small: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  large: "bg-red-100 text-red-700",
};

export const tierTabs = [
  {
    key: "beginner",
    label: "Beginner",
    count: 3,
    active: "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-300",
    inactive:
      "bg-emerald-50 text-emerald-600 ring-1 ring-emerald-200 hover:bg-emerald-100 hover:ring-emerald-300",
  },
  {
    key: "intermediate",
    label: "Intermediate",
    count: 5,
    active: "bg-amber-100 text-amber-800 ring-1 ring-amber-300",
    inactive:
      "bg-amber-50 text-amber-600 ring-1 ring-amber-200 hover:bg-amber-100 hover:ring-amber-300",
  },
  {
    key: "advanced",
    label: "Advanced",
    count: 8,
    active: "bg-slate-200 text-slate-800 ring-1 ring-slate-400",
    inactive:
      "bg-slate-100 text-slate-600 ring-1 ring-slate-300 hover:bg-slate-200 hover:ring-slate-400",
  },
] as const;

export function groupByCategory(skills: Skill[]): Record<string, Skill[]> {
  const groups: Record<string, Skill[]> = {};
  for (const skill of skills) {
    const cat = skill.category || "concept";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(skill);
  }
  return groups;
}

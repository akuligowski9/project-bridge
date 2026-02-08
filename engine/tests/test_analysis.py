"""Tests for projectbridge.analysis.engine and taxonomy."""

from projectbridge.analysis.engine import analyze
from projectbridge.analysis.taxonomy import TAXONOMY, get_adjacent, get_category, is_known
from projectbridge.schema import SkillCategory


class TestTaxonomy:
    def test_at_least_50_skills(self):
        assert len(TAXONOMY) >= 50

    def test_react_adjacents(self):
        adj = get_adjacent("React")
        assert "Next.js" in adj
        assert "TypeScript" in adj
        assert "Redux" in adj

    def test_unknown_skill(self):
        assert not is_known("MadeUpFramework")
        assert get_category("MadeUpFramework") is None
        assert get_adjacent("MadeUpFramework") == []

    def test_covers_multiple_categories(self):
        cats = {entry[0] for entry in TAXONOMY.values()}
        assert SkillCategory.LANGUAGE in cats
        assert SkillCategory.FRAMEWORK in cats
        assert SkillCategory.INFRASTRUCTURE in cats
        assert SkillCategory.TOOL in cats


class TestAnalyze:
    def test_returns_three_lists(self, sample_dev_context, sample_job_text):
        from projectbridge.input.job_description import parse_job_description

        job_reqs = parse_job_description(sample_job_text).model_dump()
        result = analyze(sample_dev_context, job_reqs)

        assert "detected_skills" in result
        assert "adjacent_skills" in result
        assert "missing_skills" in result

    def test_detected_skills_are_intersection(self, sample_dev_context):
        job_reqs = {"required_technologies": ["Python", "React", "Docker", "Kafka"]}
        result = analyze(sample_dev_context, job_reqs)

        detected = {s.name for s in result["detected_skills"]}
        assert "Python" in detected
        assert "React" in detected
        assert "Docker" in detected
        assert "Kafka" not in detected

    def test_deterministic(self, sample_dev_context):
        job_reqs = {"required_technologies": ["Python", "TypeScript", "Kubernetes"]}
        r1 = analyze(sample_dev_context, job_reqs)
        r2 = analyze(sample_dev_context, job_reqs)
        assert r1 == r2

    def test_adjacent_from_taxonomy(self, sample_dev_context):
        job_reqs = {"required_technologies": ["TypeScript", "Kubernetes"]}
        result = analyze(sample_dev_context, job_reqs)

        adjacent = {s.name for s in result["adjacent_skills"]}
        # TypeScript is adjacent to JavaScript (which dev has)
        assert "TypeScript" in adjacent
        # Kubernetes is adjacent to Docker (which dev has)
        assert "Kubernetes" in adjacent

    def test_resume_skills_enrichment(self, sample_dev_context):
        enriched = dict(sample_dev_context)
        enriched["resume_skills"] = ["Kubernetes", "Terraform"]
        job_reqs = {"required_technologies": ["Kubernetes", "Terraform"]}
        result = analyze(enriched, job_reqs)

        detected = {s.name for s in result["detected_skills"]}
        assert "Kubernetes" in detected
        assert "Terraform" in detected

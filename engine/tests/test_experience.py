"""Tests for projectbridge.analysis.experience."""

from projectbridge.analysis.experience import ExperienceLevel, infer_experience_level


class TestInferExperienceLevel:
    def test_junior_few_skills(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 80.0}],
            "frameworks": [],
            "infrastructure_signals": [],
        }
        assert infer_experience_level(ctx) == ExperienceLevel.JUNIOR

    def test_senior_many_skills(self):
        ctx = {
            "languages": [
                {"name": "Python", "percentage": 30.0},
                {"name": "JavaScript", "percentage": 25.0},
                {"name": "TypeScript", "percentage": 15.0},
                {"name": "Go", "percentage": 10.0},
                {"name": "Java", "percentage": 10.0},
                {"name": "Rust", "percentage": 5.0},
                {"name": "Ruby", "percentage": 5.0},
            ],
            "frameworks": [
                {"name": "Django"},
                {"name": "React"},
                {"name": "FastAPI"},
            ],
            "infrastructure_signals": [
                {"name": "Docker"},
                {"name": "Kubernetes"},
                {"name": "AWS"},
            ],
        }
        assert infer_experience_level(ctx) == ExperienceLevel.SENIOR

    def test_mid_moderate_skills(self):
        ctx = {
            "languages": [
                {"name": "Python", "percentage": 50.0},
                {"name": "JavaScript", "percentage": 30.0},
                {"name": "HTML", "percentage": 10.0},
                {"name": "CSS", "percentage": 10.0},
            ],
            "frameworks": [{"name": "Flask"}],
            "infrastructure_signals": [{"name": "Docker"}],
        }
        assert infer_experience_level(ctx) == ExperienceLevel.MID

    def test_years_override_senior(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 100.0}],
            "frameworks": [],
            "infrastructure_signals": [],
            "resume_years": 10,
        }
        assert infer_experience_level(ctx) == ExperienceLevel.SENIOR

    def test_years_override_junior(self):
        ctx = {
            "languages": [
                {"name": "Python", "percentage": 30.0},
                {"name": "JavaScript", "percentage": 25.0},
                {"name": "Go", "percentage": 15.0},
                {"name": "Java", "percentage": 10.0},
                {"name": "Ruby", "percentage": 10.0},
                {"name": "TypeScript", "percentage": 10.0},
            ],
            "frameworks": [],
            "infrastructure_signals": [],
            "resume_years": 1,
        }
        assert infer_experience_level(ctx) == ExperienceLevel.JUNIOR

    def test_empty_context_is_junior(self):
        ctx = {}
        assert infer_experience_level(ctx) == ExperienceLevel.JUNIOR

    def test_resume_skills_counted(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 100.0}],
            "frameworks": [],
            "infrastructure_signals": [],
            "resume_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"],
        }
        assert infer_experience_level(ctx) == ExperienceLevel.MID

    def test_enum_values(self):
        assert ExperienceLevel.JUNIOR.value == "junior"
        assert ExperienceLevel.MID.value == "mid"
        assert ExperienceLevel.SENIOR.value == "senior"

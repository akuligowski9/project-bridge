"""Tests for projectbridge.analysis.portfolio."""

from projectbridge.analysis.portfolio import derive_portfolio_insights


class TestDerivePortfolioInsights:
    def test_balanced_portfolio_no_balance_insight(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 50.0}],
            "frameworks": [{"name": "Flask"}],
            "infrastructure_signals": [{"name": "Docker"}],
        }
        job = {"required_technologies": ["Python", "Flask", "Docker"]}
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        categories = [i["category"] for i in insights]
        assert "balance" not in categories

    def test_language_only_flags_balance(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 100.0}],
            "frameworks": [],
            "infrastructure_signals": [],
        }
        job = {"required_technologies": ["Python"]}
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        balance = [i for i in insights if i["category"] == "balance"]
        assert len(balance) == 1
        assert "frameworks" in balance[0]["message"]
        assert "infrastructure" in balance[0]["message"]

    def test_infra_gap_detected(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 50.0}],
            "frameworks": [{"name": "Django"}],
            "infrastructure_signals": [],
        }
        job = {"required_technologies": ["Python", "Docker", "AWS"]}
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        infra = [i for i in insights if i["category"] == "infrastructure"]
        assert len(infra) == 1
        assert "Docker" in infra[0]["message"]

    def test_missing_domains(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 50.0}],
            "frameworks": [{"name": "Flask"}],
            "infrastructure_signals": [{"name": "Docker"}],
        }
        job = {
            "required_technologies": ["Python"],
            "experience_domains": ["fintech", "security"],
        }
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        domain = [i for i in insights if i["category"] == "domain"]
        assert len(domain) == 1

    def test_max_three_insights(self):
        ctx = {
            "languages": [
                {"name": "Python", "percentage": 10.0},
                {"name": "JavaScript", "percentage": 10.0},
                {"name": "Go", "percentage": 10.0},
                {"name": "Rust", "percentage": 10.0},
                {"name": "Ruby", "percentage": 10.0},
            ],
            "frameworks": [],
            "infrastructure_signals": [],
        }
        job = {
            "required_technologies": ["Docker", "AWS"],
            "experience_domains": ["fintech", "cloud"],
        }
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        assert len(insights) <= 3

    def test_no_infra_gap_when_dev_has_infra(self):
        ctx = {
            "languages": [{"name": "Python", "percentage": 50.0}],
            "frameworks": [],
            "infrastructure_signals": [{"name": "Docker"}],
        }
        job = {"required_technologies": ["Python", "Docker"]}
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        infra = [i for i in insights if i["category"] == "infrastructure"]
        assert len(infra) == 0

    def test_empty_context(self):
        ctx = {}
        job = {"required_technologies": []}
        analysis = {"detected_skills": [], "missing_skills": [], "adjacent_skills": []}
        insights = derive_portfolio_insights(ctx, job, analysis)
        assert isinstance(insights, list)

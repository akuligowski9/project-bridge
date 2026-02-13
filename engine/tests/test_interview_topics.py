"""Tests for projectbridge.analysis.interview_topics."""

from projectbridge.analysis.interview_topics import (
    INTERVIEW_TOPICS,
    get_interview_topics,
)


class TestInterviewTopics:
    def test_known_skill_returns_topics(self):
        topics = get_interview_topics("Docker")
        assert len(topics) >= 2
        assert any("Dockerfile" in t for t in topics)

    def test_case_insensitive(self):
        assert get_interview_topics("docker") == get_interview_topics("Docker")
        assert get_interview_topics("REACT") == get_interview_topics("React")

    def test_unknown_skill_returns_empty(self):
        assert get_interview_topics("ObscureTech99") == []

    def test_all_entries_have_at_least_two_topics(self):
        for skill, topics in INTERVIEW_TOPICS.items():
            assert len(topics) >= 2, f"{skill} has fewer than 2 topics"

    def test_all_entries_have_at_most_three_topics(self):
        for skill, topics in INTERVIEW_TOPICS.items():
            assert len(topics) <= 3, f"{skill} has more than 3 topics"

    def test_topics_are_strings(self):
        for skill, topics in INTERVIEW_TOPICS.items():
            for t in topics:
                assert isinstance(t, str), f"{skill} has non-string topic"
                assert len(t) >= 10, f"{skill} has a too-short topic: {t}"

    def test_python_topics(self):
        topics = get_interview_topics("Python")
        assert len(topics) == 3
        assert any("decorator" in t.lower() for t in topics)

    def test_react_topics(self):
        topics = get_interview_topics("React")
        assert len(topics) == 3
        assert any("hook" in t.lower() for t in topics)

    def test_postgresql_topics(self):
        topics = get_interview_topics("PostgreSQL")
        assert len(topics) == 3
        assert any("EXPLAIN" in t for t in topics)

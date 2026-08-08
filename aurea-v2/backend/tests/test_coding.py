"""Coding endpoints and services tests."""
import pytest
from fastapi.testclient import TestClient
from app.services.coding_engine import list_problems, starter, review_code, PROBLEMS, TOPICS, DIFFICULTIES


class TestCodingEngine:
    def test_all_topics_have_problems(self):
        for topic in TOPICS:
            for diff in DIFFICULTIES:
                problems = list_problems(topic, diff)
                assert len(problems) >= 3, f"{topic}/{diff} has only {len(problems)} problems"

    def test_easy_medium_have_ten_plus(self):
        for topic in TOPICS:
            for diff in ("Easy", "Medium"):
                problems = list_problems(topic, diff)
                assert len(problems) >= 10, f"{topic}/{diff} has only {len(problems)} — needs 10+"

    def test_starter_code_generated(self):
        p = PROBLEMS[0]
        for lang in ["Python", "Java", "JavaScript", "C++"]:
            code = starter(p, lang)
            assert isinstance(code, str)
            assert len(code) > 10

    def test_review_code_structure(self):
        p = next(x for x in PROBLEMS if x["id"] == "arr-e-1")
        result = review_code(p, "Python", "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen: return [seen[target-n], i]\n        seen[n] = i")
        assert "verdict" in result
        assert "issues" in result
        assert "suggestions" in result
        assert result["verdict"] in ("Looks good", "Too short to fully evaluate", "Needs work")

    def test_review_detects_todo(self):
        p = PROBLEMS[0]
        result = review_code(p, "Python", "def solution():\n    # TODO: implement this\n    pass")
        assert any("TODO" in i or "pass" in i for i in result["issues"])

    def test_problem_ids_unique(self):
        ids = [p["id"] for p in PROBLEMS]
        assert len(ids) == len(set(ids)), "Duplicate problem IDs found!"

    def test_problem_required_fields(self):
        for p in PROBLEMS:
            assert "id" in p
            assert "title" in p
            assert "description" in p
            assert "topic" in p
            assert "difficulty" in p
            assert "hints" in p
            assert len(p["hints"]) >= 1


class TestCodingAPI:
    def test_get_languages(self, client: TestClient):
        resp = client.get("/api/coding/languages")
        assert resp.status_code == 200
        langs = resp.json()["languages"]
        assert "Python" in langs
        assert "Java" in langs

    def test_get_topics(self, client: TestClient):
        resp = client.get("/api/coding/topics")
        assert resp.status_code == 200
        assert len(resp.json()["topics"]) >= 8

    def test_get_problems_default_count(self, client: TestClient):
        resp = client.get("/api/coding/problems/Arrays%20%26%20Strings/Easy")
        assert resp.status_code == 200
        problems = resp.json()["problems"]
        assert len(problems) == 10  # default count

    def test_get_problems_custom_count(self, client: TestClient):
        resp = client.get("/api/coding/problems/Dynamic%20Programming/Medium?count=5")
        assert resp.status_code == 200
        assert len(resp.json()["problems"]) == 5

    def test_get_starter_code(self, client: TestClient):
        resp = client.get("/api/coding/starter/arr-e-1/Python")
        assert resp.status_code == 200
        data = resp.json()
        assert "starter" in data
        assert "problem" in data

    def test_review_requires_auth(self, client: TestClient):
        resp = client.post("/api/coding/review", json={
            "problem_id": "arr-e-1",
            "language": "Python",
            "code": "def solution(): pass",
        })
        assert resp.status_code == 403

    def test_review_authenticated(self, client: TestClient, auth_headers: dict):
        resp = client.post("/api/coding/review", json={
            "problem_id": "arr-e-1",
            "language": "Python",
            "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target-n in seen: return [seen[target-n], i]\n        seen[n] = i\n    return []",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] in ("Strong solution", "Partially correct", "Needs work", "Looks good", "Too short to fully evaluate")

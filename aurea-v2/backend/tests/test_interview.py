"""Interview & quiz endpoint tests."""
import pytest
from fastapi.testclient import TestClient


class TestInterviewEndpoints:
    def test_get_roles(self, client: TestClient):
        resp = client.get("/api/interview/roles")
        assert resp.status_code == 200
        roles = resp.json()["roles"]
        assert isinstance(roles, list)
        assert len(roles) >= 5
        assert "Software Engineer" in roles

    def test_get_topics(self, client: TestClient):
        resp = client.get("/api/interview/topics")
        assert resp.status_code == 200
        topics = resp.json()["topics"]
        assert "Data Structures" in topics
        assert "System Design" in topics

    def test_get_difficulties(self, client: TestClient):
        resp = client.get("/api/interview/difficulties")
        assert resp.status_code == 200
        diffs = resp.json()["difficulties"]
        assert set(diffs) == {"Easy", "Medium", "Hard"}

    def test_generate_questions_default_count(self, client: TestClient):
        resp = client.post("/api/interview/questions", json={
            "role": "Software Engineer",
            "topic": "Data Structures",
            "difficulty": "Easy",
        })
        assert resp.status_code == 200
        qs = resp.json()["questions"]
        assert isinstance(qs, list)
        assert len(qs) == 10  # default count

    def test_generate_questions_custom_count(self, client: TestClient):
        resp = client.post("/api/interview/questions", json={
            "role": "Python Developer",
            "topic": "DBMS & SQL",
            "difficulty": "Medium",
            "count": 15,
        })
        assert resp.status_code == 200
        qs = resp.json()["questions"]
        assert len(qs) == 15

    def test_generate_questions_invalid_role(self, client: TestClient):
        resp = client.post("/api/interview/questions", json={
            "role": "NonExistentRole",
            "topic": "Data Structures",
            "difficulty": "Easy",
        })
        assert resp.status_code == 400

    def test_evaluate_answer(self, client: TestClient):
        resp = client.post("/api/interview/evaluate", json={
            "question": "What is a stack?",
            "answer": "A stack is a LIFO data structure. Push adds elements to the top and pop removes from the top. Used in recursion and undo operations.",
            "topic": "Data Structures",
            "difficulty": "Easy",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "verdict" in data
        assert "strengths" in data
        assert "gaps" in data
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 100


class TestQuizEndpoints:
    def test_get_quiz_topics(self, client: TestClient):
        resp = client.get("/api/quiz/topics")
        assert resp.status_code == 200
        topics = resp.json()["topics"]
        assert len(topics) >= 4

    def test_get_difficulties_for_topic(self, client: TestClient):
        resp = client.get("/api/quiz/difficulties/Data%20Structures")
        assert resp.status_code == 200
        diffs = resp.json()["difficulties"]
        assert "Easy" in diffs

    def test_get_quiz_questions_count(self, client: TestClient):
        resp = client.get("/api/quiz/questions/Data%20Structures/Easy?count=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 10
        qs = data["questions"]
        # Correct answer must NOT be in response
        for q in qs:
            assert "correct" not in q
            assert "options" in q
            assert len(q["options"]) >= 2

    def test_get_quiz_questions_20(self, client: TestClient):
        resp = client.get("/api/quiz/questions/DBMS%20%26%20SQL/Hard?count=20")
        assert resp.status_code == 200
        assert resp.json()["total"] == 20

    def test_submit_quiz(self, client: TestClient, auth_headers: dict):
        qs_resp = client.get("/api/quiz/questions/Data%20Structures/Easy?count=5")
        questions = qs_resp.json()["questions"]
        answers = {q["id"]: 0 for q in questions}  # answer 0 for all
        resp = client.post(
            "/api/quiz/submit/Data%20Structures/Easy",
            json={"answers": answers},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "correct" in data
        assert "total" in data
        assert "results" in data
        assert data["total"] >= 5
        # Each result must have correct_option
        for r in data["results"]:
            assert "correct_option" in r
            assert "is_correct" in r

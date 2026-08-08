from app.services.answer_library import get_questions, get_topics


def test_library_covers_every_interview_topic_and_difficulty():
    for topic in get_topics():
        for difficulty in ("Easy", "Medium", "Hard"):
            answers = get_questions(topic, difficulty)
            assert len(answers) >= 20
            assert all(answer["direct_answer"] and answer["key_points"] for answer in answers)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import date, datetime, timezone
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.progress import ProgressEvent

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.query(ProgressEvent).filter(ProgressEvent.user_id == current_user.id).all()
    today = date.today().isoformat()

    by_type = defaultdict(list)
    by_topic = defaultdict(list)
    today_counts = defaultdict(int)
    dates = set()
    daily = defaultdict(list)

    for e in events:
        score = e.score or 0
        by_type[e.event_type.value].append(score)
        if e.topic:
            by_topic[e.topic].append(score)
        event_date = e.created_at.date().isoformat() if e.created_at else None
        if event_date:
            dates.add(event_date)
            daily[event_date].append(score)
            if event_date == today:
                today_counts[e.event_type.value] += 1

    # Streak calculation
    streak = 0
    cursor = date.today()
    while cursor.isoformat() in dates:
        streak += 1
        cursor = date.fromordinal(cursor.toordinal() - 1)

    # Field summaries
    fields = {}
    field_map = {
        "quiz": "quiz_answer",
        "theory": "theory_evaluated",
        "coding": "code_review",
    }
    for key, event_type in field_map.items():
        scores = by_type.get(event_type, [])
        avg = round(sum(scores) / len(scores)) if scores else 0
        fields[key] = {
            "label": key.title(),
            "attempts": len(scores),
            "score": avg,
        }

    # Topic rows
    topic_rows = []
    for topic, scores in by_topic.items():
        avg = round(sum(scores) / len(scores))
        topic_rows.append({"topic": topic, "score": avg, "attempts": len(scores)})
    topic_rows.sort(key=lambda r: -r["score"])

    total = len(events)
    weekly = []
    for offset in range(6, -1, -1):
        day = date.fromordinal(date.today().toordinal() - offset)
        values = daily.get(day.isoformat(), [])
        weekly.append({"date": day.isoformat(), "label": day.strftime("%a"), "attempts": len(values), "score": round(sum(values) / len(values)) if values else 0})
    return {
        "total_assessments": total,
        "streak": streak,
        "active_days": len(dates),
        "today": dict(today_counts),
        "fields": fields,
        "topics": topic_rows,
        "strongest": [r["topic"] for r in topic_rows if r["score"] >= 70 and r["attempts"] >= 3],
        "focus": [r["topic"] for r in topic_rows if r["score"] < 70 and r["attempts"] >= 3],
        "weekly": weekly,
    }

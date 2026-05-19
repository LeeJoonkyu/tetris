from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas, auth


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_nickname(db: Session, nickname: str) -> models.User | None:
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def create_user(db: Session, data: schemas.RegisterIn) -> models.User:
    user = models.User(
        email=data.email,
        nickname=data.nickname,
        password_hash=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_score(db: Session, user: models.User, data: schemas.ScoreIn) -> models.Score:
    s = models.Score(
        user_id=user.id,
        score=data.score,
        lines=data.lines,
        level=data.level,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def top_scores(db: Session, limit: int = 10) -> list[schemas.LeaderboardEntry]:
    # Best score per user, sorted desc. Simple approach: take top N rows globally
    # then dedupe by nickname, keeping highest. Plenty for small dataset.
    stmt = (
        select(models.Score, models.User.nickname)
        .join(models.User, models.User.id == models.Score.user_id)
        .order_by(models.Score.score.desc())
        .limit(limit * 5)
    )
    rows = db.execute(stmt).all()
    seen: dict[str, schemas.LeaderboardEntry] = {}
    for score_row, nickname in rows:
        if nickname in seen:
            continue
        seen[nickname] = schemas.LeaderboardEntry(
            nickname=nickname,
            score=score_row.score,
            lines=score_row.lines,
            level=score_row.level,
            played_at=score_row.played_at,
        )
        if len(seen) >= limit:
            break
    return list(seen.values())


def my_scores(db: Session, user: models.User, limit: int = 10) -> list[models.Score]:
    return (
        db.query(models.Score)
        .filter(models.Score.user_id == user.id)
        .order_by(models.Score.played_at.desc())
        .limit(limit)
        .all()
    )

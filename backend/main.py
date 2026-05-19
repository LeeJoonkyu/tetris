from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Tetris API", version="1.0.0", lifespan=lifespan)

# CORS: allow GitHub Pages frontend + local dev origins
default_origins = [
    "https://leejoonkyu.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
extra = os.environ.get("FRONTEND_ORIGIN", "").strip()
if extra and extra not in default_origins:
    default_origins.append(extra)

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="email already registered")
    if crud.get_user_by_nickname(db, data.nickname):
        raise HTTPException(status_code=409, detail="nickname already taken")
    try:
        user = crud.create_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="user already exists")
    return user


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )
    token = auth.create_access_token(sub=user.email)
    return schemas.TokenOut(access_token=token, nickname=user.nickname)


@app.get("/auth/me", response_model=schemas.UserOut)
def me(current: models.User = Depends(auth.get_current_user)):
    return current


@app.post("/scores", response_model=schemas.ScoreOut, status_code=201)
def submit_score(
    data: schemas.ScoreIn,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    return crud.create_score(db, current, data)


@app.get("/scores/top", response_model=list[schemas.LeaderboardEntry])
def get_top_scores(limit: int = 10, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    return crud.top_scores(db, limit=limit)


@app.get("/scores/me", response_model=list[schemas.ScoreOut])
def get_my_scores(
    limit: int = 10,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    limit = max(1, min(limit, 100))
    return crud.my_scores(db, current, limit=limit)

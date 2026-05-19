# NEON TETRIS

Browser Tetris with a Game Boy aesthetic, 8-bit chiptune BGM, line-clear fireworks,
account-based score history, and a global top-score leaderboard.

- **Live demo:** https://leejoonkyu.github.io/tetris/
- **API:** https://tetris-api.onrender.com (Render Free — first request may take ~30s to wake)
- **Source:** https://github.com/LeeJoonkyu/tetris

## Tech

- **Frontend:** single-file `index.html` (HTML + CSS + JS, no build step). Hosted on GitHub Pages.
- **Backend:** FastAPI + SQLite + JWT (bcrypt). Hosted on Render Free.

## Controls

| Key | Action |
|-----|--------|
| ← → | Move |
| ↓ | Soft drop |
| ↑ | Rotate |
| Space | Hard drop |
| P | Pause |
| R | Restart |
| M | Music on/off |

## Account & leaderboard

- Sign up (email + password + nickname) to record your scores.
- Each game-over auto-submits your final score.
- The sidebar shows the all-time top score across every player.
- Mobile / touch devices show a "DESKTOP ONLY" notice (keyboard required).

## Run locally

### Backend
```
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8001
```
Server: http://127.0.0.1:8001 (docs at `/docs`).

### Frontend
```
python3 -m http.server 8000
```
Open http://127.0.0.1:8000/ — the frontend auto-detects the local API when not
running on `leejoonkyu.github.io`.

## API summary

```
POST   /auth/register       {email, password, nickname}
POST   /auth/login          {email, password}              -> {access_token, nickname}
GET    /auth/me             Authorization: Bearer <jwt>
POST   /scores              Authorization + {score, lines, level}
GET    /scores/top?limit=10
GET    /scores/me           Authorization
GET    /healthz
```

## Notes / Limits

- Render Free uses ephemeral container disk — SQLite data may reset on
  redeploy / instance replacement. Fine for a demo; move to a persistent
  store (Render Disk, Fly volume, Postgres) for production.
- The server does not verify game logic — clients could submit arbitrary
  scores. Out of scope for this study project.

from .conftest import auth


# ---------- POST /scores ----------

def test_submit_score_happy(client, make_user):
    token = make_user("a@b.com", "pw1234", "alpha")
    r = client.post("/scores", headers=auth(token),
                    json={"score": 1500, "lines": 7, "level": 2})
    assert r.status_code == 201
    body = r.json()
    assert body["score"] == 1500
    assert body["lines"] == 7
    assert body["level"] == 2
    assert isinstance(body["id"], int)
    assert "played_at" in body


def test_submit_score_unauthenticated(client):
    r = client.post("/scores", json={"score": 100, "lines": 0, "level": 1})
    assert r.status_code == 401


def test_submit_score_negative_rejected(client, make_user):
    token = make_user("a@b.com", "pw1234", "alpha")
    r = client.post("/scores", headers=auth(token),
                    json={"score": -1, "lines": 0, "level": 1})
    assert r.status_code == 422


def test_submit_score_level_out_of_range_rejected(client, make_user):
    token = make_user("a@b.com", "pw1234", "alpha")
    r = client.post("/scores", headers=auth(token),
                    json={"score": 100, "lines": 0, "level": 200})
    assert r.status_code == 422


# ---------- GET /scores/top ----------

def test_top_scores_empty(client):
    r = client.get("/scores/top")
    assert r.status_code == 200
    assert r.json() == []


def test_top_scores_ordering_and_dedupe_per_user(client, make_user):
    """The leaderboard should keep only each user's best score and sort desc."""
    a = make_user("a@b.com", "pw1234", "alpha")
    b = make_user("b@b.com", "pw1234", "bravo")
    # alpha posts two; only the higher one should appear
    client.post("/scores", headers=auth(a), json={"score":  900, "lines": 4, "level": 1})
    client.post("/scores", headers=auth(a), json={"score": 1500, "lines": 7, "level": 2})
    client.post("/scores", headers=auth(b), json={"score": 3200, "lines": 15, "level": 3})

    r = client.get("/scores/top?limit=10")
    assert r.status_code == 200
    rows = r.json()
    nicks = [row["nickname"] for row in rows]
    assert nicks == ["bravo", "alpha"]
    assert rows[0]["score"] == 3200
    assert rows[1]["score"] == 1500  # alpha's BEST, not the older 900


def test_top_scores_respects_limit(client, make_user):
    for i in range(5):
        tok = make_user(f"u{i}@b.com", "pw1234", f"user{i}")
        client.post("/scores", headers=auth(tok),
                    json={"score": (i + 1) * 100, "lines": 0, "level": 1})
    r = client.get("/scores/top?limit=2")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 2
    assert rows[0]["score"] == 500
    assert rows[1]["score"] == 400


def test_top_scores_limit_is_clamped(client):
    # Non-positive / huge limits should be clamped without 500
    assert client.get("/scores/top?limit=0").status_code == 200
    assert client.get("/scores/top?limit=-5").status_code == 200
    assert client.get("/scores/top?limit=99999").status_code == 200


# ---------- GET /scores/me ----------

def test_my_scores_returns_only_own_newest_first(client, make_user):
    a = make_user("a@b.com", "pw1234", "alpha")
    b = make_user("b@b.com", "pw1234", "bravo")
    client.post("/scores", headers=auth(a), json={"score": 100, "lines": 1, "level": 1})
    client.post("/scores", headers=auth(a), json={"score": 200, "lines": 2, "level": 1})
    client.post("/scores", headers=auth(b), json={"score": 9999, "lines": 50, "level": 5})

    r = client.get("/scores/me", headers=auth(a))
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 2
    assert {row["score"] for row in rows} == {100, 200}
    assert rows[0]["score"] == 200  # newest first
    assert rows[1]["score"] == 100


def test_my_scores_requires_auth(client):
    r = client.get("/scores/me")
    assert r.status_code == 401

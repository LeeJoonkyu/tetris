from .conftest import auth


# ---------- /auth/register ----------

def test_register_happy(client):
    r = client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "alpha",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@b.com"
    assert body["nickname"] == "alpha"
    assert isinstance(body["id"], int)


def test_register_duplicate_email(client):
    p1 = {"email": "dup@b.com", "password": "pw1234", "nickname": "one"}
    p2 = {"email": "dup@b.com", "password": "pw1234", "nickname": "two"}
    assert client.post("/auth/register", json=p1).status_code == 201
    r = client.post("/auth/register", json=p2)
    assert r.status_code == 409
    assert "email" in r.json()["detail"].lower()


def test_register_duplicate_nickname(client):
    assert client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "same",
    }).status_code == 201
    r = client.post("/auth/register", json={
        "email": "c@b.com", "password": "pw1234", "nickname": "same",
    })
    assert r.status_code == 409
    assert "nickname" in r.json()["detail"].lower()


def test_register_invalid_email(client):
    r = client.post("/auth/register", json={
        "email": "not-an-email", "password": "pw1234", "nickname": "xy",
    })
    assert r.status_code == 422


def test_register_short_password(client):
    r = client.post("/auth/register", json={
        "email": "a@b.com", "password": "123", "nickname": "alpha",
    })
    assert r.status_code == 422


def test_register_short_nickname(client):
    r = client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "x",
    })
    assert r.status_code == 422


def test_register_nickname_with_space_is_rejected(client):
    r = client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "with space",
    })
    assert r.status_code == 422


def test_register_hangul_nickname(client):
    r = client.post("/auth/register", json={
        "email": "k@b.com", "password": "pw1234", "nickname": "준규",
    })
    assert r.status_code == 201
    assert r.json()["nickname"] == "준규"


def test_register_mixed_hangul_nickname(client):
    r = client.post("/auth/register", json={
        "email": "m@b.com", "password": "pw1234", "nickname": "jklee_준규",
    })
    assert r.status_code == 201
    assert r.json()["nickname"] == "jklee_준규"


# ---------- /auth/login ----------

def test_login_happy(client):
    client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "alpha",
    })
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "pw1234"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["nickname"] == "alpha"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "a@b.com", "password": "pw1234", "nickname": "alpha",
    })
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/auth/login", json={"email": "nope@b.com", "password": "pw1234"})
    assert r.status_code == 401


# ---------- /auth/me ----------

def test_me_with_token(client, make_user):
    token = make_user("u@b.com", "pw1234", "uone")
    r = client.get("/auth/me", headers=auth(token))
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "u@b.com"
    assert body["nickname"] == "uone"


def test_me_without_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_invalid_token(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not.a.real.jwt"})
    assert r.status_code == 401

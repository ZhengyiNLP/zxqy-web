def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

"""Tests for authentication endpoints."""
import pytest



class TestLogin:
    def test_login_success(self, client, admin_user):
        user, _ = admin_user
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "token" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    def test_login_wrong_password(self, client, admin_user):
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={"username": "nobody", "password": "test123"})
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post("/api/auth/login", json={"username": "admin"})
        assert resp.status_code == 422


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "display_name": "新用户",
            "password": "newpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "newuser"

    def test_register_duplicate_username(self, client, admin_user):
        resp = client.post("/api/auth/register", json={
            "username": "admin",
            "display_name": "另一个管理员",
            "password": "test123",
        })
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]

    def test_register_duplicate_display_name(self, client, admin_user):
        resp = client.post("/api/auth/register", json={
            "username": "another",
            "display_name": "管理员",
            "password": "test123",
        })
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "short",
            "display_name": "短密码",
            "password": "123",
        })
        assert resp.status_code == 422


class TestChangePassword:
    def test_change_password_success(self, client, admin_user):
        _, token = admin_user
        resp = client.post("/api/auth/change-password", json={
            "old_password": "admin123",
            "new_password": "newadmin456",
        }, headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_change_password_wrong_old(self, client, admin_user):
        _, token = admin_user
        resp = client.post("/api/auth/change-password", json={
            "old_password": "wrongpass",
            "new_password": "newadmin456",
        }, headers=auth_header(token))
        assert resp.status_code == 400

    def test_change_password_no_auth(self, client):
        resp = client.post("/api/auth/change-password", json={
            "old_password": "admin123",
            "new_password": "newadmin456",
        })
        assert resp.status_code == 401


class TestGetMe:
    def test_get_me(self, client, admin_user):
        _, token = admin_user
        resp = client.get("/api/auth/me", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == "admin"
        assert data["is_admin"] is True

    def test_get_me_no_auth(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


class TestCheckUsername:
    def test_available(self, client):
        resp = client.get("/api/auth/check-username?username=newname")
        assert resp.status_code == 200
        assert resp.json()["data"]["available"] is True

    def test_taken(self, client, admin_user):
        resp = client.get("/api/auth/check-username?username=admin")
        assert resp.status_code == 200
        assert resp.json()["data"]["available"] is False

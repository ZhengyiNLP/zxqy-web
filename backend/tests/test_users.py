def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

"""Tests for user management endpoints."""
import pytest



class TestCreateUser:
    def test_admin_create_user(self, client, admin_user):
        _, token = admin_user
        resp = client.post("/api/users", json={
            "username": "newuser",
            "password": "pass123",
            "display_name": "新用户",
        }, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == "newuser"
        assert data["must_change_password"] is True

    def test_non_admin_create_user_forbidden(self, client, normal_user):
        _, token = normal_user
        resp = client.post("/api/users", json={
            "username": "hacker",
            "password": "pass123",
            "display_name": "黑客",
        }, headers=auth_header(token))
        assert resp.status_code == 403

    def test_create_duplicate_username(self, client, admin_user, normal_user):
        _, token = admin_user
        resp = client.post("/api/users", json={
            "username": "testuser",
            "password": "pass123",
            "display_name": "重复用户",
        }, headers=auth_header(token))
        assert resp.status_code == 400


class TestListUsers:
    def test_admin_list_users(self, client, admin_user, normal_user):
        _, token = admin_user
        resp = client.get("/api/users", headers=auth_header(token))
        assert resp.status_code == 200
        users = resp.json()["data"]
        assert len(users) == 2

    def test_non_admin_list_forbidden(self, client, normal_user):
        _, token = normal_user
        resp = client.get("/api/users", headers=auth_header(token))
        assert resp.status_code == 403


class TestUpdateUser:
    def test_admin_update_user(self, client, admin_user, normal_user):
        _, token = admin_user
        user, _ = normal_user
        resp = client.put(f"/api/users/{user.id}", json={
            "display_name": "更新后的名字",
        }, headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["data"]["display_name"] == "更新后的名字"

    def test_update_nonexistent_user(self, client, admin_user):
        _, token = admin_user
        resp = client.put("/api/users/9999", json={"display_name": "xx"}, headers=auth_header(token))
        assert resp.status_code == 404


class TestDeleteUser:
    def test_admin_delete_user(self, client, admin_user, normal_user):
        _, token = admin_user
        user, _ = normal_user
        resp = client.delete(f"/api/users/{user.id}", headers=auth_header(token))
        assert resp.status_code == 200

    def test_cannot_delete_self(self, client, admin_user):
        user, token = admin_user
        resp = client.delete(f"/api/users/{user.id}", headers=auth_header(token))
        assert resp.status_code == 400
        assert "不能删除自己" in resp.json()["detail"]

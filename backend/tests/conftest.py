"""Shared test fixtures for the weekly report backend."""
import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from auth import hash_password, create_access_token
from models import User, Team, TeamMember, Project, AIConfig, AIPrompt, DailyItem

# Use a temp directory for test database
_test_dir = tempfile.mkdtemp()
_test_db_path = os.path.join(_test_dir, "test.db")
TEST_DATABASE_URL = f"sqlite:///{_test_db_path}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_user(db):
    # RBAC 下仅 is_super_admin 可绕过权限检查；测试库不初始化角色/权限数据，
    # 故管理员夹具必须带 is_super_admin，否则所有接口 403
    user = User(
        username="admin",
        password_hash=hash_password("admin123"),
        display_name="管理员",
        is_admin=True,
        is_super_admin=True,
        must_change_password=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return user, token


@pytest.fixture
def normal_user(db):
    user = User(
        username="testuser",
        password_hash=hash_password("test123"),
        display_name="测试用户",
        is_admin=False,
        must_change_password=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return user, token


@pytest.fixture
def default_team(db, admin_user):
    user, _ = admin_user
    team = Team(name="测试团队", creator_id=user.id, invite_code="ABCDEF")
    db.add(team)
    db.commit()
    db.refresh(team)
    membership = TeamMember(team_id=team.id, user_id=user.id, role="admin")
    db.add(membership)
    db.commit()
    return team


@pytest.fixture
def default_project(db, default_team, admin_user):
    user, _ = admin_user
    project = Project(name="个人工作", is_default=True, team_id=None, user_id=user.id, description="个人默认项目")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def team_project(db, default_team):
    """归属团队的普通项目（日报接口按团队提交场景使用）"""
    project = Project(name="团队项目", team_id=default_team.id, is_default=False)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

from app.core.security import create_access_token


def test_create_access_token() -> None:
    token = create_access_token("user-1", {"role": "admin", "email": "a@example.com", "workspace_id": "w"})
    assert token.count(".") == 2


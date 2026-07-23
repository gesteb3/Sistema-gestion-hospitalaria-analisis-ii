from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing() -> None:
    password = "Admin12345"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("Incorrecta123", hashed)


def test_access_token() -> None:
    token = create_access_token(
        subject="1",
        additional_claims={
            "username": "admin",
            "roles": ["ADMINISTRADOR"],
        },
        expires_minutes=5,
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["username"] == "admin"
    assert payload["roles"] == ["ADMINISTRADOR"]

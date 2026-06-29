from bestiaux.auth.domain import UserEntity


class TestUserEntity:
    def test_hash_password_produces_different_hash(self) -> None:
        # GIVEN
        password = "password123"

        # WHEN
        hash1 = UserEntity.hash_password(password)
        hash2 = UserEntity.hash_password(password)

        # THEN
        assert hash1 != password
        assert hash1 != hash2  # bcrypt uses random salt

    def test_verify_password_accepts_correct_password(self) -> None:
        # GIVEN
        user = UserEntity(password_hash=UserEntity.hash_password("password123"))

        # WHEN / THEN
        assert user.verify_password("password123")

    def test_verify_password_rejects_wrong_password(self) -> None:
        # GIVEN
        user = UserEntity(password_hash=UserEntity.hash_password("password123"))

        # WHEN / THEN
        assert not user.verify_password("wrong")

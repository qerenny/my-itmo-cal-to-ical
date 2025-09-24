from unittest import TestCase
from credentials_hashing import get_credentials_hash   


class CredentialsHashingTests(TestCase):
    def test_get_credentials_hash_deterministic(self):
        # Arrange
        username = "user"
        password = "pass"
        expected_hash = "BdSWkrdVaZxFBLUQQY7a7uv9RmiSVA8nrPmjGjJtZQQ"

        # Act
        result = get_credentials_hash(username, password)

        # Assert
        self.assertEqual(result, expected_hash)

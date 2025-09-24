from unittest import TestCase
from unittest.mock import patch
from auth import generate_code_verifier, get_code_challenge   


class AuthHelpersTests(TestCase):
    def test_get_code_challenge_known_value(self):
        # Arrange
        code_verifier = "abc123"
        expected_challenge = "bKE9UspwyIPg8LsQHkJaiehiTeUdstI5JZOvaoQRgJA"

        # Act
        challenge = get_code_challenge(code_verifier)

        # Assert
        self.assertEqual(challenge, expected_challenge)
        self.assertNotIn("=", challenge)

    @patch("auth.os.urandom", return_value=b"\xff\xff\xff\xff")
    def test_generate_code_verifier_sanitizes_non_alphanumeric(self, mocked_urandom):
        # Arrange & Act
        verifier = generate_code_verifier()

        # Assert
        self.assertRegex(verifier, r"^[a-zA-Z0-9]+$")
        self.assertGreater(len(verifier), 0)
        mocked_urandom.assert_called_once()

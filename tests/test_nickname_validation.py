import unittest

from input_validation import validate_nickname


class NicknameValidationTests(unittest.TestCase):
    def test_letters_only_are_allowed(self):
        self.assertTrue(validate_nickname("Alice")[0])

    def test_letters_and_numbers_are_allowed_when_letters_are_present(self):
        self.assertTrue(validate_nickname("Alice2")[0])
        self.assertTrue(validate_nickname("A1")[0])

    def test_numbers_only_are_rejected(self):
        self.assertFalse(validate_nickname("123")[0])

    def test_special_characters_are_rejected(self):
        self.assertFalse(validate_nickname("Alice!")[0])
        self.assertFalse(validate_nickname("A_B")[0])


if __name__ == "__main__":
    unittest.main()

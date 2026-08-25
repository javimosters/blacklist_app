import unittest
from unittest.mock import MagicMock
from src.services.blacklist_service import BlacklistService


class TestCheckBlacklist(unittest.TestCase):

    def setUp(self):
        self.service = BlacklistService()
        self.service.repository = MagicMock()

    def test_email_esta_en_blacklist(self):
        mock_blacklist = MagicMock()
        mock_blacklist.blocked_reason = "Spam activity"
        self.service.repository.get_by_email.return_value = mock_blacklist

        result = self.service.check_blacklist("malo@test.com")

        self.assertTrue(result["is_blacklisted"])
        self.assertEqual(result["email"], "malo@test.com")
        self.assertEqual(result["blocked_reason"], "Spam activity")

    def test_email_no_esta_en_blacklist(self):
        self.service.repository.get_by_email.return_value = None

        result = self.service.check_blacklist("bueno@test.com")

        self.assertFalse(result["is_blacklisted"])
        self.assertEqual(result["email"], "bueno@test.com")
        self.assertIsNone(result["blocked_reason"])


if __name__ == '__main__':
    unittest.main()
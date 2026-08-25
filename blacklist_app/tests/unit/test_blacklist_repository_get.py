import unittest
from unittest.mock import patch, MagicMock
from src.repositories.blacklist_repository import BlacklistRepository


class TestBlacklistRepositoryGet(unittest.TestCase):

    def setUp(self):
        self.repository = BlacklistRepository()

    @patch('src.repositories.blacklist_repository.db')
    def test_get_by_email_encontrado(self, mock_db):
        mock_result = MagicMock()
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_result

        result = self.repository.get_by_email("malo@test.com")

        self.assertEqual(result, mock_result)

    @patch('src.repositories.blacklist_repository.db')
    def test_exists_by_email_true(self, mock_db):
        mock_db.session.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = self.repository.exists_by_email("malo@test.com")

        self.assertTrue(result)

    @patch('src.repositories.blacklist_repository.db')
    def test_exists_by_email_false(self, mock_db):
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        result = self.repository.exists_by_email("bueno@test.com")

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError
from src.repositories.blacklist_repository import BlacklistRepository
from src.models.errors import ConflictError


class TestBlacklistRepositoryPost(unittest.TestCase):

    def setUp(self):
        self.repository = BlacklistRepository()

    @patch('src.repositories.blacklist_repository.db')
    def test_create_guarda_en_base_de_datos(self, mock_db):
        blacklist_data = {
            "email": "malo@test.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "blocked_reason": "Spam activity",
            "ip_address": "127.0.0.1"
        }

        self.repository.create(blacklist_data)

        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_db.session.refresh.assert_called_once()

    @patch('src.repositories.blacklist_repository.db')
    def test_create_email_duplicado_lanza_conflict_error(self, mock_db):
        mock_db.session.commit.side_effect = IntegrityError(
            "stmt", "params", Exception("duplicate key")
        )

        with self.assertRaises(ConflictError):
            self.repository.create({"email": "malo@test.com"})

        mock_db.session.rollback.assert_called_once()

    @patch('src.repositories.blacklist_repository.db')
    def test_create_error_de_integridad_no_relacionado_se_relanza(self, mock_db):
        mock_db.session.commit.side_effect = IntegrityError(
            "stmt", "params", Exception("not null constraint")
        )

        with self.assertRaises(IntegrityError):
            self.repository.create({"email": "malo@test.com"})
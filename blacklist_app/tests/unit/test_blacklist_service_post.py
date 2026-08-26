import unittest
from unittest.mock import MagicMock
from datetime import datetime
from src.services.blacklist_service import BlacklistService
from src.models.errors import ConflictError


class TestAddToBlacklist(unittest.TestCase):

    def setUp(self):
        self.service = BlacklistService()
        self.service.repository = MagicMock()

    def test_agrega_email_valido(self):
        mock_created = MagicMock()
        mock_created.id = "some-uuid"
        mock_created.email = "malo@test.com"
        mock_created.created_at = datetime(2026, 8, 26)
        self.service.repository.create.return_value = mock_created

        result = self.service.add_to_blacklist(
            email="malo@test.com",
            app_uuid="550e8400-e29b-41d4-a716-446655440000",
            blocked_reason="Spam activity",
            ip_address="127.0.0.1"
        )

        self.assertIn("added to blacklist successfully", result["message"])
        self.assertEqual(result["email"], "malo@test.com")

    def test_email_duplicado_propaga_conflict_error(self):
        self.service.repository.create.side_effect = ConflictError("ya existe")
        with self.assertRaises(ConflictError):
            self.service.add_to_blacklist(
                email="malo@test.com",
                app_uuid="550e8400-e29b-41d4-a716-446655440000",
                blocked_reason=None,
                ip_address="127.0.0.1"
            )
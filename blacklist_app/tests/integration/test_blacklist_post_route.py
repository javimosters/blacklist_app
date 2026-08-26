import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import unittest
from unittest.mock import patch
from src.main import app
from src.models.errors import ConflictError


class TestBlacklistPostRoute(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        os.environ['BEARER_TOKEN'] = 'test-token-123'

    def test_post_sin_token_retorna_401(self):
        response = self.client.post('/blacklists', json={
            "email": "malo@test.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000"
        })
        self.assertEqual(response.status_code, 401)

    @patch('src.routes.blacklist_router.blacklist_service.add_to_blacklist')
    def test_post_exitoso_retorna_201(self, mock_add):
        mock_add.return_value = {
            "message": "Email malo@test.com added to blacklist successfully",
            "id": "some-uuid",
            "email": "malo@test.com",
            "created_at": "2026-08-26T00:00:00"
        }

        response = self.client.post(
            '/blacklists',
            json={
                "email": "malo@test.com",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
                "blocked_reason": "Spam activity"
            },
            headers={'Authorization': 'Bearer test-token-123'}
        )

        self.assertEqual(response.status_code, 201)

    @patch('src.routes.blacklist_router.blacklist_service.add_to_blacklist')
    def test_post_email_faltante_retorna_400(self, mock_add):
        response = self.client.post(
            '/blacklists',
            json={"app_uuid": "550e8400-e29b-41d4-a716-446655440000"},
            headers={'Authorization': 'Bearer test-token-123'}
        )
        self.assertEqual(response.status_code, 400)
        mock_add.assert_not_called()

    @patch('src.routes.blacklist_router.blacklist_service.add_to_blacklist')
    def test_post_app_uuid_invalido_retorna_400(self, mock_add):
        response = self.client.post(
            '/blacklists',
            json={"email": "malo@test.com", "app_uuid": "no-es-uuid"},
            headers={'Authorization': 'Bearer test-token-123'}
        )
        self.assertEqual(response.status_code, 400)
        mock_add.assert_not_called()

    @patch('src.routes.blacklist_router.blacklist_service.add_to_blacklist')
    def test_post_email_duplicado_retorna_409(self, mock_add):
        mock_add.side_effect = ConflictError("ya existe")

        response = self.client.post(
            '/blacklists',
            json={"email": "malo@test.com", "app_uuid": "550e8400-e29b-41d4-a716-446655440000"},
            headers={'Authorization': 'Bearer test-token-123'}
        )
        self.assertEqual(response.status_code, 409)



import os

# Debe ir ANTES de importar src.main, porque main.py necesita esta variable
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import unittest
from unittest.mock import patch
from src.main import app


class TestBlacklistGetRoute(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        os.environ['BEARER_TOKEN'] = 'test-token-123'

    def test_get_sin_token_retorna_401(self):
        response = self.client.get('/blacklists/alguien@test.com')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['error'], 'Unauthorized')

    def test_get_con_formato_invalido_retorna_401(self):
        response = self.client.get(
            '/blacklists/alguien@test.com',
            headers={'Authorization': 'Token abc123'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_con_token_invalido_retorna_401(self):
        response = self.client.get(
            '/blacklists/alguien@test.com',
            headers={'Authorization': 'Bearer token-incorrecto'}
        )
        self.assertEqual(response.status_code, 401)

    @patch('src.routes.blacklist_router.blacklist_service.check_blacklist')
    def test_get_llama_service_con_email_correcto(self, mock_check):
        mock_check.return_value = {
            "is_blacklisted": False,
            "email": "prueba@test.com",
            "blocked_reason": None
        }

        response = self.client.get(
            '/blacklists/prueba@test.com',
            headers={'Authorization': 'Bearer test-token-123'}
        )

        self.assertEqual(response.status_code, 200)
        mock_check.assert_called_once_with("prueba@test.com")

    @patch('src.routes.blacklist_router.blacklist_service.check_blacklist')
    def test_get_email_no_blacklisted_con_token_valido(self, mock_check):
        mock_check.return_value = {
            "is_blacklisted": False,
            "email": "bueno@test.com",
            "blocked_reason": None
        }

        response = self.client.get(
            '/blacklists/bueno@test.com',
            headers={'Authorization': 'Bearer test-token-123'}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['is_blacklisted'])
        self.assertEqual(data['email'], 'bueno@test.com')

    @patch('src.routes.blacklist_router.blacklist_service.check_blacklist')
    def test_get_email_blacklisted_con_token_valido(self, mock_check):
        mock_check.return_value = {
            "is_blacklisted": True,
            "email": "malo@test.com",
            "blocked_reason": "Spam activity"
        }

        response = self.client.get(
            '/blacklists/malo@test.com',
            headers={'Authorization': 'Bearer test-token-123'}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['is_blacklisted'])
        self.assertEqual(data['blocked_reason'], 'Spam activity')


if __name__ == '__main__':
    unittest.main()
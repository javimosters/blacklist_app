import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import unittest
from unittest.mock import patch
from src.main import app


class TestPingRoute(unittest.TestCase):
    """Cubre el endpoint /blacklists/ping, hoy sin ninguna prueba (línea 127)."""

    def setUp(self):
        self.client = app.test_client()

    def test_ping_no_requiere_token(self):
        response = self.client.get('/blacklists/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "pong"})


class TestPostBodyVacio(unittest.TestCase):
    """Cubre la línea 50 de blacklist_router.py: body completamente vacío."""

    def setUp(self):
        self.client = app.test_client()
        os.environ['BEARER_TOKEN'] = 'test-token-123'
        self.headers = {'Authorization': 'Bearer test-token-123'}

    def test_post_con_json_vacio_retorna_400(self):
        response = self.client.post('/blacklists', json={}, headers=self.headers)
        self.assertEqual(response.status_code, 400)


class TestErrores500(unittest.TestCase):
    """Cubre los bloques except Exception (líneas 82-83 y 110-111) que hoy nunca se disparan."""

    def setUp(self):
        self.client = app.test_client()
        os.environ['BEARER_TOKEN'] = 'test-token-123'
        self.headers = {'Authorization': 'Bearer test-token-123'}
        self.payload_valido = {
            "email": "spam@test.com",
            "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "blocked_reason": "motivo"
        }

    @patch('src.routes.blacklist_router.blacklist_service.add_to_blacklist')
    def test_post_con_error_inesperado_retorna_500(self, mock_add):
        mock_add.side_effect = RuntimeError("fallo inesperado en base de datos")

        response = self.client.post('/blacklists', json=self.payload_valido, headers=self.headers)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["error"], "Internal Server Error")

    @patch('src.routes.blacklist_router.blacklist_service.check_blacklist')
    def test_get_con_error_inesperado_retorna_500(self, mock_check):
        mock_check.side_effect = RuntimeError("fallo inesperado consultando")

        response = self.client.get('/blacklists/algo@test.com', headers=self.headers)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["error"], "Internal Server Error")


if __name__ == '__main__':
    unittest.main()

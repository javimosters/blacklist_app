import unittest
from flask import Request
from werkzeug.test import EnvironBuilder

from src.models.errors import (
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
    ConflictError
)
from src.utils.validation import validate_uuid, get_client_ip


class TestErrors(unittest.TestCase):
    """Cubre src/models/errors.py, que hoy está al 59%."""

    def test_bad_request_error_con_mensaje_y_errores(self):
        error = BadRequestError("Email inválido", errors={"email": ["formato incorrecto"]})
        self.assertEqual(error.message, "Email inválido")
        self.assertEqual(error.errors, {"email": ["formato incorrecto"]})

    def test_bad_request_error_valores_por_defecto(self):
        error = BadRequestError()
        self.assertEqual(error.message, "Bad request")
        self.assertIsNone(error.errors)

    def test_not_found_error(self):
        error = NotFoundError("Email no encontrado")
        self.assertEqual(error.message, "Email no encontrado")

    def test_not_found_error_valor_por_defecto(self):
        error = NotFoundError()
        self.assertEqual(error.message, "Resource not found")

    def test_unauthorized_error(self):
        error = UnauthorizedError("Token vencido")
        self.assertEqual(error.message, "Token vencido")

    def test_conflict_error(self):
        error = ConflictError("El email ya existe")
        self.assertEqual(error.message, "El email ya existe")


class TestValidateUuid(unittest.TestCase):
    """Cubre validate_uuid en src/utils/validation.py."""

    def test_uuid_valido_retorna_true(self):
        resultado = validate_uuid("123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(resultado)

    def test_uuid_invalido_lanza_bad_request_error(self):
        with self.assertRaises(BadRequestError):
            validate_uuid("esto-no-es-un-uuid")


class TestGetClientIp(unittest.TestCase):
    """Cubre get_client_ip en src/utils/validation.py."""

    def _request_con_headers(self, headers=None, remote_addr="10.0.0.5"):
        builder = EnvironBuilder(path="/blacklists", headers=headers or {})
        env = builder.get_environ()
        env["REMOTE_ADDR"] = remote_addr
        return Request(env)

    def test_con_x_forwarded_for_retorna_primera_ip(self):
        request = self._request_con_headers(
            headers={"X-Forwarded-For": "203.0.113.5, 10.0.0.1, 10.0.0.2"}
        )
        ip = get_client_ip(request)
        self.assertEqual(ip, "203.0.113.5")

    def test_sin_x_forwarded_for_retorna_remote_addr(self):
        request = self._request_con_headers(headers={}, remote_addr="192.168.1.10")
        ip = get_client_ip(request)
        self.assertEqual(ip, "192.168.1.10")


if __name__ == '__main__':
    unittest.main()
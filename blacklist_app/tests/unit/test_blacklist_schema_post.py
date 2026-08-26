import unittest
from marshmallow import ValidationError
from src.schemas.blacklist_schema import BlacklistPostSchema


class TestBlacklistPostSchema(unittest.TestCase):

    def setUp(self):
        self.schema = BlacklistPostSchema()

    def test_datos_validos_pasan(self):
        data = self.schema.load({
            "email": "malo@test.com",
            "app_id": "550e8400-e29b-41d4-a716-446655440000",
            "reason": "Spam activity"
        })
        self.assertEqual(data["email"], "malo@test.com")

    def test_sin_reason_es_valido(self):
        data = self.schema.load({
            "email": "malo@test.com",
            "app_id": "550e8400-e29b-41d4-a716-446655440000"
        })
        self.assertNotIn("reason", data)

    def test_email_invalido_lanza_error(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                "email": "no-es-email",
                "app_id": "550e8400-e29b-41d4-a716-446655440000"
            })

    def test_app_id_invalido_lanza_error(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                "email": "malo@test.com",
                "app_id": "no-es-uuid"
            })

    def test_reason_muy_largo_lanza_error(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                "email": "malo@test.com",
                "app_id": "550e8400-e29b-41d4-a716-446655440000",
                "reason": "a" * 256
            })


if __name__ == '__main__':
    unittest.main()
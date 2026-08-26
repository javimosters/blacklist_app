from marshmallow import Schema, fields, validate


class BlacklistPostSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "El email es obligatorio",
        "invalid": "El email no tiene un formato válido"
    })
    app_id = fields.UUID(required=True, error_messages={
        "required": "app_id es obligatorio",
        "invalid": "app_id debe ser un UUID válido"
    })
    reason = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
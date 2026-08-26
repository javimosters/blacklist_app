import os
import pytest

# Aseguramos que estas variables existan ANTES de importar la app,
# porque src/main.py las lee apenas se importa (init_db, create_tables
# hace db.create_all() de inmediato). Usamos SQLite en memoria para que
# las pruebas NO necesiten Docker ni Postgres corriendo.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("BEARER_TOKEN", "test-token-123")

from src.main import app as flask_app  # noqa: E402
from src.db.database import db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    """
    La app de Flask ya viene creada y conectada a la base de datos
    (con las tablas creadas) desde src/main.py, solo la marcamos
    como TESTING para que Flask maneje mejor los errores en pruebas.
    """
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture
def client(app):
    """Cliente HTTP falso para hacer requests a la app sin levantar un servidor real."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Header de autorización correcto, listo para usar en cualquier request."""
    return {"Authorization": f"Bearer {os.environ['BEARER_TOKEN']}"}


@pytest.fixture(autouse=True)
def limpiar_base_de_datos(app):
    """
    Se ejecuta automáticamente ANTES de cada prueba (autouse=True).
    Borra todo lo que haya en la tabla blacklists para que una prueba
    no deje datos que dañen la siguiente (ej. el email ya existe -> 409).
    """
    with app.app_context():
        db.session.execute(db.text("DELETE FROM blacklists"))
        db.session.commit()
    yield
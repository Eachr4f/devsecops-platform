import pytest
from app import create_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_empty_list(client):
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.get_json() == {"items": []}


def test_create_and_read_item(client):
    response = client.post("/api/items", json={"name": "  Docker  "})
    assert response.status_code == 201

    item = response.get_json()
    assert isinstance(item["id"], int)
    assert item["name"] == "Docker"

    response = client.get("/api/items")
    assert response.get_json() == {"items": [item]}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"name": "   "},
        {"name": 123},
        {"name": None},
        {"name": "a" * 101},
        {"name": "Docker", "admin": True},
        [],
    ],
)
def test_invalid_input_is_not_saved(client, payload):
    response = client.post("/api/items", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert client.get("/api/items").get_json() == {"items": []}


def test_maximum_name_length(client):
    response = client.post("/api/items", json={"name": "a" * 100})
    assert response.status_code == 201


def test_wrong_content_type(client):
    response = client.post("/api/items", data="name=Docker")
    assert response.status_code == 415


def test_malformed_json(client):
    response = client.post(
        "/api/items",
        data='{"name":',
        content_type="application/json",
    )
    assert response.status_code == 400


def test_oversized_request(client):
    response = client.post("/api/items", json={"name": "a" * 20000})
    assert response.status_code == 413


def test_persistence_between_app_instances(app):
    first_client = app.test_client()
    response = first_client.post("/api/items", json={"name": "Persistant"})
    assert response.status_code == 201
    item = response.get_json()

    second_app = create_app()
    second_app.config["TESTING"] = True

    response = second_app.test_client().get("/api/items")
    assert response.status_code == 200
    assert response.get_json() == {"items": [item]}

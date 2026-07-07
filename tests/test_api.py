from fastapi.testclient import TestClient

import app.main as main


class FakePredictor:
    device = "cpu"
    model_loaded = True

    def predict(self, text):
        return {"intent": "search", "confidence": 0.99, "scores": {"search": 0.99, "chat": 0.01}}


def test_health(monkeypatch):
    monkeypatch.setattr(main, "predictor", FakePredictor())
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict(monkeypatch):
    monkeypatch.setattr(main, "predictor", FakePredictor())
    client = TestClient(main.app)
    response = client.post("/predict", json={"text": "帮我查新闻"})
    assert response.status_code == 200
    assert response.json()["intent"] == "search"


def test_route(monkeypatch):
    monkeypatch.setattr(main, "predictor", FakePredictor())
    client = TestClient(main.app)
    response = client.post("/route", json={"text": "帮我查新闻"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "search"
    assert body["route_to"] == "web_search"

import torch

from app.predictor import IntentPredictor
from tinyintent.model import TinyTransformerClassifier
from tinyintent.tokenizer import CharTokenizer
from tinyintent.utils import save_json


def create_fake_artifacts(root):
    tokenizer = CharTokenizer(max_len=8).fit(["帮我搜索新闻", "陪我聊天"])
    tokenizer.save(root / "vocab.json")
    label_to_id = {"search": 0, "chat": 1}
    save_json(root / "label_map.json", {"label_to_id": label_to_id, "id_to_label": {"0": "search", "1": "chat"}})
    config = {"max_len": 8, "d_model": 16, "nhead": 4, "num_layers": 1, "dim_feedforward": 32, "batch_size": 2, "epochs": 1, "learning_rate": 0.001}
    save_json(root / "config.json", config)
    model = TinyTransformerClassifier(vocab_size=len(tokenizer.vocab), num_labels=2, max_len=8, d_model=16, nhead=4, num_layers=1, dim_feedforward=32)
    torch.save(model.state_dict(), root / "model.pt")


def test_predictor_predicts_when_model_exists(tmp_path):
    create_fake_artifacts(tmp_path)
    predictor = IntentPredictor(artifacts_dir=tmp_path)
    result = predictor.predict("帮我搜索新闻")
    assert result["intent"] in {"search", "chat"}
    assert 0 <= result["confidence"] <= 1
    assert set(result["scores"]) == {"search", "chat"}

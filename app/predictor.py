from pathlib import Path

import torch

from tinyintent.model import TinyTransformerClassifier
from tinyintent.tokenizer import CharTokenizer
from tinyintent.utils import get_device, load_json


class IntentPredictor:
    def __init__(self, artifacts_dir="artifacts"):
        self.artifacts_dir = Path(artifacts_dir)
        self.device = get_device()
        self.model = None
        self.tokenizer = None
        self.label_to_id = None
        self.id_to_label = None
        self.config = None
        self.load()

    @property
    def model_loaded(self):
        return self.model is not None

    def load(self):
        required = {
            "model": self.artifacts_dir / "model.pt",
            "vocab": self.artifacts_dir / "vocab.json",
            "label_map": self.artifacts_dir / "label_map.json",
            "config": self.artifacts_dir / "config.json",
        }
        missing = [str(path) for path in required.values() if not path.exists()]
        if missing:
            self.model = None
            return

        self.tokenizer = CharTokenizer.load(required["vocab"])
        label_map = load_json(required["label_map"])
        self.label_to_id = label_map["label_to_id"]
        self.id_to_label = {int(k): v for k, v in label_map["id_to_label"].items()}
        self.config = load_json(required["config"])
        self.model = TinyTransformerClassifier(
            vocab_size=len(self.tokenizer.vocab),
            num_labels=len(self.label_to_id),
            max_len=self.config["max_len"],
            d_model=self.config["d_model"],
            nhead=self.config["nhead"],
            num_layers=self.config["num_layers"],
            dim_feedforward=self.config["dim_feedforward"],
            pad_id=self.tokenizer.pad_id,
        ).to(self.device)
        self.model.load_state_dict(torch.load(required["model"], map_location=self.device, weights_only=True))
        self.model.eval()

    def predict(self, text):
        if not self.model_loaded:
            raise RuntimeError(
                "Model artifacts not found. Please run:\n"
                "python scripts\\make_dataset.py\n"
                "python scripts\\train_model.py"
            )
        encoded = self.tokenizer.encode(text)
        input_ids = torch.tensor([encoded["input_ids"]], dtype=torch.long, device=self.device)
        attention_mask = torch.tensor([encoded["attention_mask"]], dtype=torch.float32, device=self.device)
        with torch.no_grad():
            probs = torch.softmax(self.model(input_ids, attention_mask), dim=-1).squeeze(0).cpu()
        scores = {self.id_to_label[idx]: round(float(value), 4) for idx, value in enumerate(probs)}
        pred_id = int(probs.argmax().item())
        return {"intent": self.id_to_label[pred_id], "confidence": round(float(probs[pred_id]), 4), "scores": scores}

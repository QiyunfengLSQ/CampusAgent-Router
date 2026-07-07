import json
import random
from pathlib import Path

import numpy as np
import torch


LABELS = ["search", "rag_qa", "summarize", "code", "reminder", "translate", "chat"]


DEFAULT_CONFIG = {
    "max_len": 64,
    "d_model": 128,
    "nhead": 4,
    "num_layers": 2,
    "dim_feedforward": 256,
    "batch_size": 32,
    "epochs": 10,
    "learning_rate": 0.001,
}


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

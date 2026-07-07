from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from torch.utils.data import DataLoader

from tinyintent.dataset import IntentDataset
from tinyintent.model import TinyTransformerClassifier
from tinyintent.tokenizer import CharTokenizer
from tinyintent.utils import get_device, load_json, save_json


def evaluate_model(data_dir="data/processed", artifacts_dir="artifacts", reports_dir="reports"):
    data_dir = Path(data_dir)
    artifacts_dir = Path(artifacts_dir)
    reports_dir = Path(reports_dir)
    required = [artifacts_dir / "model.pt", artifacts_dir / "vocab.json", artifacts_dir / "label_map.json", artifacts_dir / "config.json"]
    if any(not path.exists() for path in required):
        raise RuntimeError("Model artifacts missing. Please run: python scripts\\make_dataset.py and python scripts\\train_model.py")

    tokenizer = CharTokenizer.load(artifacts_dir / "vocab.json")
    label_map = load_json(artifacts_dir / "label_map.json")
    config = load_json(artifacts_dir / "config.json")
    label_to_id = label_map["label_to_id"]
    id_to_label = {int(k): v for k, v in label_map["id_to_label"].items()}
    ds = IntentDataset(data_dir / "test.jsonl", tokenizer, label_to_id)
    loader = DataLoader(ds, batch_size=config.get("batch_size", 32))
    device = get_device()
    model = TinyTransformerClassifier(
        vocab_size=len(tokenizer.vocab),
        num_labels=len(label_to_id),
        max_len=config["max_len"],
        d_model=config["d_model"],
        nhead=config["nhead"],
        num_layers=config["num_layers"],
        dim_feedforward=config["dim_feedforward"],
        pad_id=tokenizer.pad_id,
    ).to(device)
    model.load_state_dict(torch.load(artifacts_dir / "model.pt", map_location=device, weights_only=True))
    model.eval()

    y_true, y_pred, confidences, texts = [], [], [], []
    with torch.no_grad():
        for batch in loader:
            logits = model(batch["input_ids"].to(device), batch["attention_mask"].to(device))
            probs = torch.softmax(logits, dim=-1).cpu()
            pred_ids = probs.argmax(dim=-1).tolist()
            y_pred.extend(pred_ids)
            y_true.extend(batch["labels"].tolist())
            confidences.extend(probs.max(dim=-1).values.tolist())
            texts.extend(batch["text"])

    labels = [id_to_label[i] for i in sorted(id_to_label)]
    report = classification_report(y_true, y_pred, target_names=labels, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(labels)))).tolist()
    metrics = {"accuracy": accuracy_score(y_true, y_pred), "per_class": report, "confusion_matrix": matrix, "labels": labels}
    save_json(artifacts_dir / "metrics.json", metrics)

    reports_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Badcase Analysis", "", "| text | true_label | pred_label | confidence |", "|---|---|---|---|"]
    for text, true_id, pred_id, conf in zip(texts, y_true, y_pred, confidences):
        if true_id != pred_id:
            safe_text = str(text).replace("|", "\\|")
            lines.append(f"| {safe_text} | {id_to_label[true_id]} | {id_to_label[pred_id]} | {conf:.4f} |")
    if len(lines) == 4:
        lines.append("| No badcases on this test split. | - | - | - |")
    (reports_dir / "badcases.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"accuracy: {metrics['accuracy']:.4f}")
    print(f"confusion_matrix: {matrix}")
    return metrics

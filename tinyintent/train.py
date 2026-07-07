from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from tinyintent.dataset import IntentDataset, read_jsonl
from tinyintent.model import TinyTransformerClassifier
from tinyintent.tokenizer import CharTokenizer
from tinyintent.utils import DEFAULT_CONFIG, LABELS, get_device, save_json, set_seed


def run_epoch(model, dataloader, criterion, device, optimizer=None):
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    total_correct = 0
    total = 0
    for batch in tqdm(dataloader, leave=False):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        if training:
            optimizer.zero_grad()
        logits = model(input_ids, attention_mask)
        loss = criterion(logits, labels)
        if training:
            loss.backward()
            optimizer.step()
        total_loss += loss.item() * labels.size(0)
        total_correct += (logits.argmax(dim=-1) == labels).sum().item()
        total += labels.size(0)
    return total_loss / max(total, 1), total_correct / max(total, 1)


def train_model(data_dir="data/processed", artifacts_dir="artifacts", config=None):
    set_seed()
    config = {**DEFAULT_CONFIG, **(config or {})}
    data_dir = Path(data_dir)
    artifacts_dir = Path(artifacts_dir)
    train_rows = read_jsonl(data_dir / "train.jsonl")
    if not train_rows:
        raise RuntimeError("No training data found. Please run: python scripts\\make_dataset.py")

    tokenizer = CharTokenizer(max_len=config["max_len"]).fit([row["text"] for row in train_rows])
    label_to_id = {label: idx for idx, label in enumerate(LABELS)}
    id_to_label = {str(idx): label for label, idx in label_to_id.items()}
    train_ds = IntentDataset(data_dir / "train.jsonl", tokenizer, label_to_id)
    valid_ds = IntentDataset(data_dir / "valid.jsonl", tokenizer, label_to_id)
    train_loader = DataLoader(train_ds, batch_size=config["batch_size"], shuffle=True)
    valid_loader = DataLoader(valid_ds, batch_size=config["batch_size"])

    device = get_device()
    print(f"device: {device}")
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
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"])

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    best_acc = -1.0
    for epoch in range(1, config["epochs"] + 1):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, device, optimizer)
        with torch.no_grad():
            valid_loss, valid_acc = run_epoch(model, valid_loader, criterion, device)
        print(
            f"epoch: {epoch} train_loss: {train_loss:.4f} train_acc: {train_acc:.4f} "
            f"valid_loss: {valid_loss:.4f} valid_acc: {valid_acc:.4f}"
        )
        if valid_acc > best_acc:
            best_acc = valid_acc
            torch.save(model.state_dict(), artifacts_dir / "model.pt")

    tokenizer.save(artifacts_dir / "vocab.json")
    save_json(artifacts_dir / "label_map.json", {"label_to_id": label_to_id, "id_to_label": id_to_label})
    save_json(artifacts_dir / "config.json", config)
    return {"best_valid_acc": best_acc, "device": str(device)}

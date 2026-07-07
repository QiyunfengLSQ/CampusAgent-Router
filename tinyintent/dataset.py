import json
from pathlib import Path

import torch
from torch.utils.data import Dataset


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


class IntentDataset(Dataset):
    def __init__(self, path, tokenizer, label_to_id):
        self.rows = read_jsonl(path)
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        encoded = self.tokenizer.encode(row["text"])
        return {
            "input_ids": torch.tensor(encoded["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(encoded["attention_mask"], dtype=torch.float32),
            "labels": torch.tensor(self.label_to_id[row["label"]], dtype=torch.long),
            "text": row["text"],
            "label": row["label"],
        }

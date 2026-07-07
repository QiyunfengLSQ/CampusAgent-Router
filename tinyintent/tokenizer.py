import json
from collections import Counter
from pathlib import Path


PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


class CharTokenizer:
    def __init__(self, vocab=None, max_len=64):
        self.max_len = max_len
        self.vocab = vocab or {PAD_TOKEN: 0, UNK_TOKEN: 1}
        self.id_to_token = {idx: tok for tok, idx in self.vocab.items()}

    @property
    def pad_id(self):
        return self.vocab[PAD_TOKEN]

    @property
    def unk_id(self):
        return self.vocab[UNK_TOKEN]

    def fit(self, texts, min_freq=1):
        counter = Counter()
        for text in texts:
            counter.update(str(text))
        self.vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
        for char, freq in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
            if freq >= min_freq and char not in self.vocab:
                self.vocab[char] = len(self.vocab)
        self.id_to_token = {idx: tok for tok, idx in self.vocab.items()}
        return self

    def encode(self, text, max_len=None):
        limit = max_len or self.max_len
        ids = [self.vocab.get(ch, self.unk_id) for ch in str(text)[:limit]]
        attention_mask = [1] * len(ids)
        pad_count = limit - len(ids)
        if pad_count > 0:
            ids.extend([self.pad_id] * pad_count)
            attention_mask.extend([0] * pad_count)
        return {"input_ids": ids, "attention_mask": attention_mask}

    def decode(self, ids):
        chars = []
        for idx in ids:
            token = self.id_to_token.get(int(idx), UNK_TOKEN)
            if token not in {PAD_TOKEN, UNK_TOKEN}:
                chars.append(token)
        return "".join(chars)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"max_len": self.max_len, "vocab": self.vocab}, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(vocab=data["vocab"], max_len=data.get("max_len", 64))

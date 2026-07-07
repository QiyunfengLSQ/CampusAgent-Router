import torch
from torch import nn


class TinyTransformerClassifier(nn.Module):
    def __init__(
        self,
        vocab_size,
        num_labels,
        max_len=64,
        d_model=128,
        nhead=4,
        num_layers=2,
        dim_feedforward=256,
        dropout=0.1,
        pad_id=0,
    ):
        super().__init__()
        self.pad_id = pad_id
        self.max_len = max_len
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position_embedding = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)
        self.classifier = nn.Linear(d_model, num_labels)

    def forward(self, input_ids, attention_mask):
        batch_size, seq_len = input_ids.shape
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, seq_len)
        hidden = self.embedding(input_ids) + self.position_embedding(positions)
        key_padding_mask = attention_mask == 0
        encoded = self.encoder(hidden, src_key_padding_mask=key_padding_mask)
        mask = attention_mask.unsqueeze(-1).to(encoded.dtype)
        pooled = (encoded * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
        return self.classifier(pooled)

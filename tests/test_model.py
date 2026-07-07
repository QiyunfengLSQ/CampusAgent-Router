import torch

from tinyintent.model import TinyTransformerClassifier


def test_model_forward_shape():
    model = TinyTransformerClassifier(vocab_size=20, num_labels=7, max_len=8, d_model=16, nhead=4, num_layers=1, dim_feedforward=32)
    input_ids = torch.randint(0, 20, (2, 8))
    attention_mask = torch.ones(2, 8)
    logits = model(input_ids, attention_mask)
    assert logits.shape == (2, 7)

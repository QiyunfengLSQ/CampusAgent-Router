from tinyintent.dataset import IntentDataset, write_jsonl
from tinyintent.tokenizer import CharTokenizer


def test_dataset_loads(tmp_path):
    path = tmp_path / "train.jsonl"
    write_jsonl(path, [{"text": "帮我搜索新闻", "label": "search"}])
    tokenizer = CharTokenizer(max_len=8).fit(["帮我搜索新闻"])
    dataset = IntentDataset(path, tokenizer, {"search": 0})
    item = dataset[0]
    assert len(dataset) == 1
    assert item["input_ids"].shape[0] == 8
    assert item["labels"].item() == 0

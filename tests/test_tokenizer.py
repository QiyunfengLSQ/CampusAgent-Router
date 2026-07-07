from tinyintent.tokenizer import CharTokenizer


def test_tokenizer_encode_decode():
    tokenizer = CharTokenizer(max_len=8).fit(["帮我搜索AI"])
    encoded = tokenizer.encode("帮我搜索AI")
    assert len(encoded["input_ids"]) == 8
    assert encoded["attention_mask"][:6] == [1, 1, 1, 1, 1, 1]
    assert tokenizer.decode(encoded["input_ids"]).startswith("帮我搜索AI")

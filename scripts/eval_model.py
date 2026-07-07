import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tinyintent.evaluate import evaluate_model


if __name__ == "__main__":
    evaluate_model()

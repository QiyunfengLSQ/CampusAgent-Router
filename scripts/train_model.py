import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tinyintent.train import train_model


if __name__ == "__main__":
    result = train_model()
    print(result)

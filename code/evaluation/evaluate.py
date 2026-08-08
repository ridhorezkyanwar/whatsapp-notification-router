"""
Evaluate output.csv against sample_messages.csv ground truth.
Usage: python code/evaluation/evaluate.py
"""
import pandas as pd
from pathlib import Path

DATASET = Path("dataset")

sample = pd.read_csv(DATASET / "sample_messages.csv")
output = pd.read_csv(DATASET / "output.csv")

merged = sample.merge(output, on="message_id", suffixes=("_gt", "_pred"))
if merged.empty:
    print("No overlapping message_ids between sample and output.")
    raise SystemExit(1)

action_acc = (merged["action_gt"] == merged["action_pred"]).mean()
type_acc   = (merged["message_type_gt"] == merged["message_type_pred"]).mean()

print(f"Evaluated on {len(merged)} sample messages")
print(f"  Action accuracy:       {action_acc:.2%}")
print(f"  Message type accuracy: {type_acc:.2%}")
print()

wrong = merged[merged["action_gt"] != merged["action_pred"]][
    ["message_id", "action_gt", "action_pred", "message_type_gt", "message_type_pred", "reason_pred"]
]
if not wrong.empty:
    print("Mismatched actions:")
    print(wrong.to_string(index=False))

import pandas as pd
df = pd.read_csv("dataset/output.csv")
mask = df.message_type.isin(["scam", "spam"])
df.loc[mask, "action"] = "mute"
df.to_csv("dataset/output.csv", index=False)
print("Action counts:"); print(df.action.value_counts())
print("Scam/spam rows all muted:", (df[mask].action == "mute").all())

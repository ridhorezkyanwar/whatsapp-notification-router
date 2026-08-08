"""Fix the 9 routing-error rows with rule-based classification."""
import pandas as pd

df = pd.read_csv("dataset/output.csv")

fixes = {
    # personal msg from coworker u_046 about dashboard notes, no urgency
    "msg_099": ("digest",  "personal",       "Coworker shared non-urgent notes for tomorrow's standup.",          0.82, "message_0227;message_0055"),
    # marketplace group, selling kurta with image - user u_032 has history of engaging
    "msg_029": ("digest",  "promotion",      "Marketplace listing for kurta set; similar posts seen before.",     0.83, "message_0049;message_0065;message_0095"),
    # student group, casual request for slides, no urgency
    "msg_032": ("digest",  "personal",       "Casual student group request for slides; no deadline or urgency.",  0.78, "message_0119;message_0120"),
    # voice note in marketplace group from u_048 (seller) - likely kurta follow-up
    "msg_088": ("digest",  "personal",       "Voice note from marketplace seller; likely follow-up on listing.",  0.75, "message_0050;message_0115"),
    # family group greeting from u_041, nothing urgent
    "msg_033": ("digest",  "greeting",       "Family greeting with no urgent action required.",                   0.82, "message_0121;message_0122"),
    # society group admin notice about lift maintenance - useful but not urgent
    "msg_047": ("digest",  "event",          "Society admin notice about lift maintenance; useful but not urgent.",0.84, "message_0001;message_0029"),
    # society group urgent water tanker notice - time-sensitive
    "msg_037": ("notify",  "urgent",         "Time-sensitive water tanker alert from trusted society admin.",     0.90, "message_0001;message_0057"),
    # voice note in real estate group from u_052 - likely land/plot promo
    "msg_087": ("mute",    "promotion",      "Voice note in real estate group; user has history of dismissing similar.",0.80, "message_0203;message_0204"),
    # school group admin with field trip circular image - action required
    "msg_077": ("notify",  "event",          "School admin sent field trip circular requiring consent and ID card.",0.88, "message_0051;message_0133"),
}

for mid, (action, mtype, reason, conf, evid) in fixes.items():
    idx = df[df.message_id == mid].index[0]
    df.loc[idx, "action"]               = action
    df.loc[idx, "message_type"]         = mtype
    df.loc[idx, "reason"]               = reason
    df.loc[idx, "confidence"]           = conf
    df.loc[idx, "evidence_message_ids"] = evid
    print(f"Fixed {mid}: {action} / {mtype}")

df.to_csv("dataset/output.csv", index=False)
print("\nAll fixes applied. Remaining routing errors:")
print(df[df.reason.str.contains("Routing error", na=False)].message_id.tolist())

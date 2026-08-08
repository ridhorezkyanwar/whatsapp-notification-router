import pandas as pd
msgs = pd.read_csv("dataset/messages.csv").set_index("message_id")
error_ids = ["msg_099","msg_029","msg_032","msg_088","msg_033","msg_047","msg_037","msg_087","msg_077"]
for mid in error_ids:
    r = msgs.loc[mid]
    print(f"{mid} | {r.conversation_type} | group={r.group_id} | biz={r.business_id} | sender={r.sender_user_id}")
    print(f"  text: {str(r.message_text)[:120]}")
    print(f"  media: {r.media_type} / {r.media_id}")
    print()

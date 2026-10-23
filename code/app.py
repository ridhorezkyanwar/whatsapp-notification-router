"""Local review app for the WhatsApp notification router."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"


@st.cache_data
def read_csv(name: str) -> list[dict[str, str]]:
    path = DATASET / name
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def value(row: dict[str, str], key: str, default: str = "") -> str:
    return (row.get(key) or default).strip()


def read_groq_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except Exception:
        return ""


st.set_page_config(page_title="Router Notifikasi", page_icon="🔔", layout="wide")
st.title("🔔 Router Notifikasi WhatsApp")
st.caption("Tinjau pesan, keputusan routing, bukti historis, dan media dari dataset lokal.")

messages = read_csv("messages.csv")
predictions = read_csv("output.csv")
history = {value(row, "message_id"): row for row in read_csv("message_history.csv")}
events = read_csv("message_events.csv")
events_by_message: dict[str, list[dict[str, str]]] = {}
for event in events:
    events_by_message.setdefault(value(event, "message_id"), []).append(event)

prediction_by_id = {value(row, "message_id"): row for row in predictions}
missing_ids = {value(row, "message_id") for row in messages} - set(prediction_by_id)
groq_api_key = read_groq_api_key()
key_available = bool(groq_api_key)

with st.sidebar:
    st.header("Kontrol")
    st.write(f"Pesan masuk: **{len(messages)}**")
    st.write(f"Prediksi tersimpan: **{len(predictions)}**")
    if missing_ids:
        st.warning(f"{len(missing_ids)} pesan belum memiliki prediksi.")
    else:
        st.success("Setiap pesan memiliki satu prediksi.")

    st.divider()
    st.subheader("Jalankan model AI")
    if key_available:
        st.caption("GROQ_API_KEY tersedia dengan aman untuk aplikasi ini.")
        run_ai = st.button("Jalankan ulang semua pesan", type="primary", use_container_width=True)
        if run_ai:
            with st.status("Memproses pesan dengan Groq…", expanded=True) as status:
                try:
                    child_env = os.environ.copy()
                    child_env["GROQ_API_KEY"] = groq_api_key
                    completed = subprocess.run(
                        [sys.executable, str(ROOT / "code" / "main.py")],
                        cwd=ROOT,
                        env=child_env,
                        capture_output=True,
                        text=True,
                        timeout=1800,
                        check=False,
                    )
                    if completed.stdout:
                        st.code(completed.stdout[-10000:], language="text")
                    if completed.returncode:
                        if completed.stderr:
                            st.code(completed.stderr[-5000:], language="text")
                        status.update(label="Pemrosesan gagal; file output lama dipertahankan.", state="error")
                    else:
                        st.cache_data.clear()
                        status.update(label="Selesai. output.csv sudah diperbarui.", state="complete")
                        st.rerun()
                except subprocess.TimeoutExpired:
                    status.update(label="Waktu proses melewati 30 menit; output lama dipertahankan.", state="error")
                except OSError as error:
                    status.update(label=f"Tidak dapat menjalankan Python: {error}", state="error")
    else:
        st.warning("AI belum bisa dijalankan: GROQ_API_KEY belum tersedia.")
        st.markdown("**Aktifkan di Streamlit Cloud:** buka **Manage app → Settings → Secrets**, lalu tambahkan:")
        st.code('GROQ_API_KEY = "kunci-groq-anda"', language="toml")
        st.caption("Simpan Secrets, lalu pilih Reboot app. Jangan tempelkan API key di chat atau commit ke GitHub.")

    st.divider()
    st.subheader("Unduh hasil")
    output_path = DATASET / "output.csv"
    if output_path.exists():
        st.download_button(
            "Unduh output.csv",
            data=output_path.read_bytes(),
            file_name="output.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.caption("Belum ada output.csv untuk diunduh.")

if not messages:
    st.error("dataset/messages.csv tidak ditemukan atau tidak berisi pesan.")
    st.stop()

if not predictions:
    st.info("Belum ada prediksi. Tambahkan GROQ_API_KEY di Secrets, lalu jalankan model AI.")
elif missing_ids:
    st.warning("Output saat ini belum mencakup semua pesan. Jalankan ulang model sebelum submit.")

actions = [value(row, "action", "unknown") for row in predictions]
count_notify = sum(action == "notify" for action in actions)
count_digest = sum(action == "digest" for action in actions)
count_mute = sum(action == "mute" for action in actions)
metric_cols = st.columns(4)
metric_cols[0].metric("Pesan", len(messages))
metric_cols[1].metric("Notify", count_notify)
metric_cols[2].metric("Digest", count_digest)
metric_cols[3].metric("Mute", count_mute)

if predictions:
    st.caption("Output yang tampil adalah isi dataset/output.csv saat ini. Aplikasi tidak menganggapnya sebagai label kebenaran.")

st.subheader("Jelajahi pesan")
control_cols = st.columns([1, 1, 2])
user_ids = sorted({value(row, "user_id") for row in messages if value(row, "user_id")})
selected_user = control_cols[0].selectbox("Pengguna", ["Semua", *user_ids])
action_options = ["Semua", "notify", "digest", "mute", "Belum diproses"]
selected_action = control_cols[1].selectbox("Keputusan", action_options)
search = control_cols[2].text_input("Cari pesan / pengirim / ID")

filtered = []
for message in messages:
    message_id = value(message, "message_id")
    prediction = prediction_by_id.get(message_id, {})
    action = value(prediction, "action", "Belum diproses")
    if selected_user != "Semua" and value(message, "user_id") != selected_user:
        continue
    if selected_action != "Semua" and action != selected_action:
        continue
    haystack = " ".join(
        value(message, field)
        for field in ("message_id", "message_text", "sender_user_id", "business_id", "group_id")
    ).casefold()
    if search.casefold() not in haystack:
        continue
    filtered.append({
        "message_id": message_id,
        "user_id": value(message, "user_id"),
        "waktu": value(message, "created_at"),
        "pengirim": value(message, "sender_user_id") or value(message, "business_id"),
        "jenis pesan": value(prediction, "message_type", "—"),
        "keputusan": action,
        "keyakinan": value(prediction, "confidence", "—"),
        "isi": value(message, "message_text") or f"Media {value(message, 'media_type', 'tidak diketahui')}",
    })

st.caption(f"Menampilkan {len(filtered)} dari {len(messages)} pesan.")
st.dataframe(filtered, hide_index=True, width="stretch", height=380)

if filtered:
    selected_id = st.selectbox("Buka detail pesan", [row["message_id"] for row in filtered])
    message = next(row for row in messages if value(row, "message_id") == selected_id)
    prediction = prediction_by_id.get(selected_id, {})
    detail_cols = st.columns([2, 1])
    with detail_cols[0]:
        st.markdown(f"### Pesan `{selected_id}`")
        st.write(value(message, "message_text") or "Tidak ada teks; lihat media di sebelah kanan.")
        st.write(f"**Alasan:** {value(prediction, 'reason', 'Belum ada keputusan.')}")
        st.write(f"**Pengguna:** {value(message, 'user_id')} · **Jenis chat:** {value(message, 'conversation_type')}")
        evidence_ids = [item.strip() for item in value(prediction, "evidence_message_ids", "none").split(";") if item.strip() and item.strip() != "none"]
        st.markdown("**Bukti historis**")
        if not evidence_ids:
            st.caption("Tidak ada bukti historis yang dicantumkan.")
        for evidence_id in evidence_ids:
            old_message = history.get(evidence_id)
            if old_message:
                st.write(f"`{evidence_id}` — {value(old_message, 'message_text', '(tanpa teks)')}")
                for event in events_by_message.get(evidence_id, []):
                    if value(event, "user_id") == value(message, "user_id"):
                        reactions = ", ".join(
                            f"{field}={value(event, field)}"
                            for field in ("message_opened", "message_replied", "notification_dismissed", "message_reported")
                            if value(event, field)
                        )
                        if reactions:
                            st.caption(f"Interaksi pengguna: {reactions}")
                        break
            else:
                st.caption(f"ID bukti {evidence_id} tidak ditemukan di message_history.csv.")

    with detail_cols[1]:
        media_id = value(message, "media_id")
        media_type = value(message, "media_type")
        if media_type == "image" and media_id:
            image_path = DATASET / "media" / "images" / f"{media_id}.jpg"
            if image_path.exists():
                st.image(str(image_path), caption=f"Gambar {media_id}", width="stretch")
            else:
                st.warning(f"File gambar {media_id} tidak ditemukan.")
        elif media_type == "voice" and media_id:
            audio_path = DATASET / "media" / "audio" / f"{media_id}.mp3"
            if audio_path.exists():
                st.audio(str(audio_path))
            else:
                st.warning(f"File audio {media_id} tidak ditemukan.")
        else:
            st.caption("Pesan ini tidak memiliki media.")

st.divider()
st.caption("Aplikasi berjalan lokal. Saat routing AI dijalankan, teks, konteks, dan media pesan dikirim ke Groq untuk diproses.")

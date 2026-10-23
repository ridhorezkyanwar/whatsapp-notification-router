# WhatsApp Notification Router

A local Python application for reviewing incoming messages and routing them to `notify`, `digest`, or `mute`. It uses the participant-facing context data and can send text, image, and voice-note content to Groq for AI classification.

## What the application does

- Browse messages and saved predictions in a local Streamlit interface.
- Filter by user and routing decision; search message text and IDs.
- Inspect the selected message, image or audio, model reason, and cited historical evidence.
- Download the current `dataset/output.csv`.
- Run the AI router for the complete input file and write one result per message.

The current contents of `dataset/output.csv` are shown as saved predictions. The app does not treat them as verified ground truth. Running AI classification requires a Groq account, an API key, internet access, and may use account credits.

## Setup and run (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r code\requirements.txt
$env:GROQ_API_KEY = "your-groq-api-key"
python -m streamlit run code\app.py
```

Open the local address printed by Streamlit. Keep the terminal open while using the app. To run the batch router without the interface:

```powershell
python code\main.py
```

## Setup and run (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
export GROQ_API_KEY="your-groq-api-key"
python -m streamlit run code/app.py
```

The default Groq model is `qwen/qwen3.8-27b`. Set `GROQ_MODEL` in the environment to use another compatible model. Keep API keys outside the repository; the app reads the key from its environment and does not save it.

## Output contract

The router writes `dataset/output.csv` with exactly these columns:

```text
message_id,action,message_type,reason,confidence,evidence_message_ids
```

It reads incoming messages and context from `dataset/`. If routing or media transcription fails, the current output file is kept as-is and the error is shown; the program does not silently label failed messages as `digest`.

## Known limits

- AI predictions are model-generated and are not guaranteed to match hidden evaluation labels.
- Routing makes one model request per message; voice notes also require transcription. Processing can take time and consume API quota.
- Image content is sent to the vision-capable model when the image file is present. Voice notes are transcribed through Groq before classification.
- The Streamlit interface is a local review tool, not a WhatsApp integration or a hosted production service.

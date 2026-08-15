# WhatsApp Notification Router

An AI-powered message routing system that classifies incoming WhatsApp messages as **notify**, **digest**, or **mute** — built for the HackerRank Orchestrate 24-hour hackathon.

## Problem

WhatsApp is noisy. A single message stream can contain family chats, society notices, school updates, work messages, business promotions, and scams. Treating every message the same causes two bad outcomes: important messages get missed, and unwanted messages interrupt the user.

This system makes personalized routing decisions for each message using context about the user, sender, group, and message history.

## How It Works

```
messages.csv + context CSVs
        │
        ▼
  Context Builder
  (user prefs, group info, business metadata, behavioral history)
        │
        ▼
  LLM Router (Groq — Qwen3.6 27B)
  + Whisper ASR for voice notes
  + Rule-based safety layer (scam/spam detection)
        │
        ▼
  output.csv (action, message_type, reason, confidence, evidence)
```

For each message, the system:
1. Pulls relevant context: user DND window, group role, business verification status, opt-out history
2. Retrieves historical messages as behavioral evidence
3. Transcribes voice notes via Whisper
4. Sends a structured prompt to LLaMA 3.3 70B via Groq API
5. Validates and sanitizes the JSON output

## Output Schema

| Column | Values |
|---|---|
| `action` | `notify` / `digest` / `mute` |
| `message_type` | `personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, `unknown` |
| `reason` | Short human-readable explanation |
| `confidence` | 0.0 – 1.0 |
| `evidence_message_ids` | Semicolon-separated historical message IDs, or `none` |

## Tech Stack

- **LLM**: Qwen3.6 27B via [Groq API](https://groq.com) (fast inference)
- **ASR**: Whisper Large v3 (voice note transcription)
- **Data**: pandas for CSV joins and context retrieval
- **Language**: Python 3.10+

## Setup & Run

```bash
pip install -r code/requirements.txt

# Set your Groq API key
set GROQ_API_KEY=your_key_here        # Windows
export GROQ_API_KEY=your_key_here     # Linux/macOS

python code/main.py
```

Output is written to `dataset/output.csv`.

## Project Structure

```
.
├── code/
│   ├── main.py           # Main routing pipeline
│   ├── requirements.txt
│   └── evaluation/       # Evaluation scripts
├── dataset/
│   ├── output.csv        # Predictions
│   └── sample_messages.csv
└── problem_statement.md
```

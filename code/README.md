# HackerRank Orchestrate — Message Notification Router

This repository is a starter pack for the **HackerRank Orchestrate** challenge. The goal is to design a WhatsApp-style notification router that decides, for every incoming message, whether the user should be interrupted immediately, whether the message can be included in a later digest, or whether it should be muted.

The system must make personalized decisions using multimodal WhatsApp data: text, images, voice notes, business accounts, group context, user behavior, and historical message interactions.

## Project Overview

For each message in `dataset/messages.csv`, your solution must generate a single row in `dataset/output.csv` with the columns:

- `message_id`
- `action` (`notify`, `digest`, or `mute`)
- `message_type` (best-fit category)
- `reason` (short human-readable explanation)
- `confidence` (number between `0` and `1`)
- `evidence_message_ids` (historical message IDs or `none`)

Your model should balance urgency, relevance, user preferences, safety, and noise reduction.

## Why This Problem Matters

WhatsApp conversations mix personal chats, group announcements, business updates, promotions, image posters, voice notes, and scam attempts. A good router helps users by:

- surfacing urgent personal or event messages right away
- deferring low-priority content into a digest
- muting unwanted, repeating, or risky content

The challenge is to make these decisions in a personalized way based on the available context.

## Repository Structure

```text
.
├── AGENTS.md                         # AI tool guidelines and transcript logging rules
├── CLAUDE.md                         # Additional model-specific guidance
├── README.md                         # Project explanation and usage instructions
├── problem_statement.md              # Full challenge spec and data schema
├── dataset/                          # Participant-facing data files
│   ├── messages.csv                  # Incoming messages to route
│   ├── output.csv                    # Prediction destination template
│   ├── sample_messages.csv           # Example predictions and style guide
│   ├── users.csv                     # User notification behavior and settings
│   ├── groups.csv                    # Group chat metadata
│   ├── group_members.csv             # User-group membership and behavior
│   ├── business_accounts.csv         # Business sender metadata
│   ├── user_business_history.csv     # User relationships with business accounts
│   ├── message_history.csv           # Historical messages for evidence
│   ├── message_events.csv            # Historical user interactions
│   ├── images.csv                    # Image media IDs and file paths
│   ├── voice_notes.csv               # Voice media IDs and file paths
│   ├── daily_notification_summary.csv # Notification load summaries by user
│   └── media/                        # Image and audio media files
└── code/
    └── main.py                       # Intended entry point for the routing system
```

## Data Files and Usage

- `dataset/messages.csv`: the only file that needs predictions.
- `dataset/sample_messages.csv`: solved examples showing how `action`, `message_type`, `reason`, `confidence`, and `evidence_message_ids` should look.
- `dataset/users.csv`, `dataset/groups.csv`, `dataset/group_members.csv`: user and group context for personalization.
- `dataset/business_accounts.csv`, `dataset/user_business_history.csv`: business sender trust and relationship signals.
- `dataset/message_history.csv`, `dataset/message_events.csv`: past messages and user reactions for evidence-based reasoning.
- `dataset/images.csv`, `dataset/voice_notes.csv`: media IDs and file paths for image and voice-note content.
- `dataset/media/`: raw image and audio files referenced by the media CSV files.

## Required Output Format

Every row in `dataset/messages.csv` must produce exactly one corresponding row in `dataset/output.csv`.

- `action`: `notify`, `digest`, or `mute`
- `message_type`: one of `personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, or `unknown`
- `reason`: a concise explanation for the decision
- `confidence`: a float between `0` and `1`
- `evidence_message_ids`: semicolon-separated historical message IDs, or `none`

Keep the output columns in the exact order above.

## Suggested Development Workflow

1. Review `problem_statement.md` carefully to understand the input schema, allowed values, and scoring expectations.
2. Explore `dataset/sample_messages.csv` to learn the intended output style.
3. Build a routing system that loads `dataset/messages.csv`, enriches each message using the context data, and writes `dataset/output.csv`.
4. If your approach uses media content, load the files referenced by `dataset/images.csv` and `dataset/voice_notes.csv` from `dataset/media/`.
5. Validate the final output contains one row per incoming message and the correct columns.

## Running the Solution

The expected entry point is `code/main.py`. Implement your routing logic there so that running the script produces `dataset/output.csv`.

Example command (Python):

```powershell
python code\main.py
```

If you use a different language or structure, document the exact command here.

## Submission Requirements

A complete submission should include:

- a runnable solution that reads `dataset/` and writes `dataset/output.csv`
- a populated `dataset/output.csv` with one row per `dataset/messages.csv` entry
- a README explaining the project and how to run it
- the AI chat transcript log described in `AGENTS.md`

## Evaluation Criteria

The final output will be judged based on:

- correct routing decision (`action`)
- correct message category (`message_type`)
- meaningful and consistent `reason`
- relevant historical evidence in `evidence_message_ids`
- calibrated `confidence` values

High-quality solutions will combine structured metadata, historical behavior, media understanding, safety checks, and personalization.

## Notes

- Use only participant-facing files in `dataset/` for predictions.
- Do not hardcode labels from the dataset.
- Keep the system deterministic where possible.
- Read any secrets from environment variables only; do not store them in the repository.
- Preserve the required `output.csv` schema exactly.

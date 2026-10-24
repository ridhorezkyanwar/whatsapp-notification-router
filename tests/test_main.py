"""Offline unit tests for code/main.py.

Run from the repository root:
    python -m unittest discover -s tests -v

These tests mock Groq calls and never use a real API key.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import main as router  # noqa: E402


def groq_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class SanitizeTests(unittest.TestCase):
    def test_normalizes_invalid_action_and_type_and_filters_evidence(self):
        result = router.sanitize(
            {
                "action": "delete",
                "message_type": "malware",
                "reason": "r" * 140,
                "confidence": "1.7",
                "evidence_message_ids": "hist-1; invented; hist-2;invented",
            },
            ["hist-1", "hist-2"],
        )

        self.assertEqual(result["action"], "digest")
        self.assertEqual(result["message_type"], "unknown")
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["evidence_message_ids"], "hist-1;hist-2")
        self.assertEqual(len(result["reason"]), 120)

    def test_falls_back_for_non_numeric_confidence_and_missing_fields(self):
        result = router.sanitize(
            {"confidence": "not-a-number", "evidence_message_ids": "not-real"},
            [],
        )

        self.assertEqual(result["action"], "digest")
        self.assertEqual(result["message_type"], "unknown")
        self.assertEqual(result["confidence"], 0.5)
        self.assertEqual(result["evidence_message_ids"], "none")

    def test_clamps_negative_confidence(self):
        result = router.sanitize(
            {
                "action": "mute",
                "message_type": "scam",
                "confidence": -4,
                "evidence_message_ids": "none",
            },
            [],
        )
        self.assertEqual(result["confidence"], 0.0)


class GroqRetryTests(unittest.TestCase):
    def test_retries_429_then_returns_successful_content(self):
        rate_limit_error = RuntimeError("rate limit")
        rate_limit_error.status_code = 429
        rate_limit_error.response = SimpleNamespace(
            headers={"retry-after": "0"}
        )

        client_mock = Mock()
        client_mock.chat.completions.create.side_effect = [
            rate_limit_error,
            groq_response(' {"action":"digest"} '),
        ]

        with patch.object(router, "client", client_mock), patch.object(
            router.time, "sleep"
        ) as sleep_mock:
            content = router.call_groq("system", [{"role": "user", "content": "hi"}], "test-model")

        self.assertEqual(content, '{"action":"digest"}')
        self.assertEqual(client_mock.chat.completions.create.call_count, 2)
        sleep_mock.assert_called_once_with(1.25)

        call_kwargs = client_mock.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "test-model")
        self.assertEqual(call_kwargs["response_format"], router.ROUTING_RESPONSE_FORMAT)

    def test_does_not_retry_non_429_error(self):
        api_error = RuntimeError("service unavailable")
        api_error.status_code = 503
        client_mock = Mock()
        client_mock.chat.completions.create.side_effect = api_error

        with patch.object(router, "client", client_mock), patch.object(
            router.time, "sleep"
        ) as sleep_mock:
            with self.assertRaisesRegex(RuntimeError, "service unavailable"):
                router.call_groq("system", [], "test-model")

        self.assertEqual(client_mock.chat.completions.create.call_count, 1)
        sleep_mock.assert_not_called()

    def test_raises_when_groq_returns_empty_content(self):
        client_mock = Mock()
        client_mock.chat.completions.create.return_value = groq_response("  ")

        with patch.object(router, "client", client_mock):
            with self.assertRaisesRegex(RuntimeError, "empty response"):
                router.call_groq("system", [], "test-model")


class RoutingFailureTests(unittest.TestCase):
    def test_wraps_malformed_json_as_routing_failure(self):
        row = SimpleNamespace(
            message_id="msg-test-1",
            user_id="user-test-1",
            message_text="hello",
            media_type="text",
            media_id=None,
            conversation_type="direct",
            sender_user_id="sender-test-1",
            business_id=None,
            created_at="2026-01-01T00:00:00Z",
            forwarded_count=0,
        )

        with patch.object(router, "build_context", return_value=("context", [])), patch.object(
            router, "call_groq", return_value="not-json"
        ):
            with self.assertRaisesRegex(RuntimeError, "Routing failed for msg-test-1"):
                router.route_message(row)


class StructuredOutputContractTests(unittest.TestCase):
    def test_schema_is_strict_and_requires_all_output_fields(self):
        schema = router.ROUTING_RESPONSE_FORMAT["json_schema"]
        self.assertTrue(schema["strict"])
        self.assertFalse(schema["schema"]["additionalProperties"])
        self.assertEqual(
            set(schema["schema"]["required"]),
            {
                "action",
                "message_type",
                "reason",
                "confidence",
                "evidence_message_ids",
            },
        )


if __name__ == "__main__":
    unittest.main()

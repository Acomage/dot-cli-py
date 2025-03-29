"""Output manager for the Dot CLI tool."""

import json
import os
import sys
from typing import Dict, Any, Optional

# Global constants
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "zh"]
MESSAGES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "i18n")


class OutputManager:
    """Manage output messages with internationalization support."""

    def __init__(self) -> None:
        """Initialize the output manager."""
        self.language = self._determine_language()
        self.messages = self._load_messages()

    def _determine_language(self) -> str:
        """Determine the language to use."""
        # Check environment variable
        lang = os.environ.get("DOT_LANGUAGE", "").lower()
        if lang in SUPPORTED_LANGUAGES:
            return lang

        # Default to system language or English
        system_lang = os.environ.get("LANG", "").split(".")[0].split("_")[0].lower()
        if system_lang in SUPPORTED_LANGUAGES:
            return system_lang

        return DEFAULT_LANGUAGE

    def _load_messages(self) -> Dict[str, str]:
        """Load messages for the current language."""
        try:
            with open(
                os.path.join(MESSAGES_PATH, f"{self.language}.json"),
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to English
            try:
                with open(
                    os.path.join(MESSAGES_PATH, "en.json"), "r", encoding="utf-8"
                ) as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Critical error, can't load messages
                print(
                    "Error: Could not load messages. The installation might be corrupted.",
                    file=sys.stderr,
                )
                sys.exit(1)
        return {}

    def get(self, key: str, **kwargs: Any) -> str:
        """Get a message by key with format parameters."""
        message = self.messages.get(key, key)
        if kwargs:
            return message.format(**kwargs)
        return message

    def print(self, key: str, **kwargs: Any) -> None:
        """Print a message by key with format parameters."""
        print(self.get(key, **kwargs))

    def print_error(self, key: str, **kwargs: Any) -> None:
        """Print an error message by key with format parameters."""
        print(self.get(key, **kwargs), file=sys.stderr)

    def prompt(self, key: str, choices: Optional[str] = None, **kwargs: Any) -> str:
        """Prompt the user for input."""
        prompt_text = self.get(key, **kwargs)
        if choices:
            prompt_text = f"{prompt_text} ({choices}): "
        else:
            prompt_text = f"{prompt_text}: "

        return input(prompt_text)


# Create a global instance for use throughout the application
output_manager = OutputManager()

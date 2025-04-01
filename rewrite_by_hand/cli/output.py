import json
import os
import sys
from typing import Dict, Any, Optional

from ..data.variables import DEFAULT_LANGUAGE, MESSAGES_PATH


class OutputManager:
    """Manage output messages with internationalization support."""

    def __init__(self) -> None:
        """Initialize the output manager."""
        self.language = DEFAULT_LANGUAGE
        self.messages = self._load_messages()

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
            print(
                f"Warning: Could not load messages for {self.language}, can't find {os.path.join(MESSAGES_PATH, f'{self.language}.json')}. Falling back to English.",
                file=sys.stderr,
            )
            try:
                with open(
                    os.path.join(MESSAGES_PATH, "en.json"), "r", encoding="utf-8"
                ) as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Critical error, can't load messages
                print(
                    "Error: You don't have any language file. The installation might be corrupted.",
                    file=sys.stderr,
                )
                sys.exit(1)

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

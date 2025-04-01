from enum import Enum


class OutputText(Enum):
    HELLO = "Hello, {}!"
    FILE_READ = "File {} read successfully."


class ErrorText(Enum):
    FILE_NOT_FOUND = "Error: File {} not found!"
    INVALID_INPUT = "Error: Invalid input '{}'."


class PromptText(Enum):
    INPUT_NAME = "Enter your name: "
    INPUT_AGE = "Age (default: {default_age}): "
    RETRY_INPUT = "Invalid input, please try again: "
    INPUT_COUNTRY = "Select country ({choices}): "

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Result(Generic[T, E]):
    success: bool
    value: T | None = None
    error: E | None = None

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        return cls(success=True, value=value)

    @classmethod
    def err(cls, error: E) -> "Result[T, E]":
        return cls(success=False, error=error)


if __name__ == "__main__":

    def divide(a: int, b: int) -> Result[int, str]:
        if b == 0:
            return Result.err("Division by zero")
        return Result.ok(a // b)

    result = divide(10, 0)
    if result.success:
        print("Result:", result.value)
    else:
        print("Error:", result.error)

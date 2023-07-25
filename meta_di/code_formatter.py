from typing import Protocol


class CodeFormatterProto(Protocol):
    def format(self, code: str) -> str:
        ...


try:
    import black
    import black.mode

    class BlackCodeFormatter(CodeFormatterProto):
        def format(self, code: str) -> str:
            return black.format_str(code, mode=black.mode.Mode())

    DEFAULT_CODE_FORMATTER = BlackCodeFormatter()
except ImportError:
    DEFAULT_CODE_FORMATTER = None  # type: ignore

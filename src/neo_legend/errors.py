"""Application-specific errors."""


class LegendRenderError(ValueError):
    """Base error for legend rendering failures."""


class UnknownLegendTypeError(LegendRenderError):
    """Raised when a legend type has no registered renderer."""

    def __init__(self, legend_type: str) -> None:
        self.legend_type = legend_type
        super().__init__(f"Unknown legend type: {legend_type}")


class UnknownStyleError(LegendRenderError):
    """Raised when a renderer does not support the requested style."""

    def __init__(self, legend_type: str, style: str, allowed_styles: list[str]) -> None:
        self.legend_type = legend_type
        self.style = style
        self.allowed_styles = allowed_styles
        allowed = ", ".join(allowed_styles)
        super().__init__(f"Unknown style '{style}' for {legend_type}. Allowed styles: {allowed}")

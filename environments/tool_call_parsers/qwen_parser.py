"""
Qwen 2.5 tool call parser.

Uses the same <tool_call> format as Openzuma.
Registered as a separate parser name for clarity when using --tool-parser=qwen.
"""

from environments.tool_call_parsers import register_parser
from environments.tool_call_parsers.openzuma_parser import OpenzumaToolCallParser


@register_parser("qwen")
class QwenToolCallParser(OpenzumaToolCallParser):
    """
    Parser for Qwen 2.5 tool calls.
    Same <tool_call>{"name": ..., "arguments": ...}</tool_call> format as Openzuma.
    """

    pass  # Identical format -- inherits everything from Openzuma

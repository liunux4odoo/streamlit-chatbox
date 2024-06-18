from typing import *
# from streamlit_option_menu import option_menu
import asyncio
from .messages import *


__version__ = "1.1.12.post3"


__all__ = [
    "ChatBox",
    "Markdown",
    "Image",
    "Audio",
    "Video",
    "OutputElement",
    "FakeLLM",
    "FakeAgent",
]


def run_async(cor) -> Any:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(cor)

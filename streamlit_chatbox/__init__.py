from typing import *
# from streamlit_option_menu import option_menu
import asyncio
from .messages import *
from .thirdpart import *


__version__ = "1.1.13.post1"


__all__ = [
    "ChatBox",
    "Markdown",
    "Image",
    "Audio",
    "Video",
    "Json",
    "OutputElement",
    "FakeLLM",
    "FakeAgent",
]


def run_async(cor) -> Any:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(cor)

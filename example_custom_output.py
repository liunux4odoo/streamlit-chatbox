# example to define output method

from streamlit_chatbox import *
from streamlit_markdown import st_hack_markdown, st_streaming_markdown

ChatBox.register_output_method("richmd", st_hack_markdown)

cb = ChatBox()
cb.user_say(OutputElement("user defined output method", output_method="richmd", theme_color="blue", mermaid_theme_CSS=""))

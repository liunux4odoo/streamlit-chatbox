from streamlit_markdown import st_markdown, st_hack_markdown

from .messages import ChatBox


# ChatBox.register_output_method("richmd", st_markdown)
ChatBox.register_output_method("richmd", st_hack_markdown)

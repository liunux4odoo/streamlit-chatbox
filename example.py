import streamlit as st
from streamlit_chatbox import st_chatbox
import time


st.write('start to chat')
streaming = st.checkbox('streaming', False)
chat_box = st_chatbox(greetings=['welcome to chat', '\n```streamlit``` is a great tool!'])


q = st.text_input('input', placeholder='input your question here')
if q:
    chat_box.user_say(q)
    text = f'my answer to:\n\n{q}\n\n```this is some code```\n\n'
    if streaming:
        chat_box.robot_say('')
		chat_box.output_messages() # you need output the msg first for streaming output
        for i in range(1, len(text)+10, 5):
            chat_box.update_last_box_text(text[:i])
            time.sleep(0.3)
    else:
        chat_box.robot_say(text)

chat_box.output_messages()

import streamlit as st
from streamlit_chatbox import st_chatbox, MsgType
import time


st.write('start to chat')
streaming = st.checkbox('streaming', False)
chat_box = st_chatbox(
	greetings=['welcome to chat', '\n```streamlit``` is a great tool!'])
# use help(st_chatbox) to see costom params

q = st.text_input('input', placeholder='input your question here')
if q:
    chat_box.user_say(q)
    text = f'my answer to:\n\n{q}\n\n```this is some code```'
    if streaming:
        chat_box.robot_stream(text)
    else:
        chat_box.robot_say(text)

    chat_box.robot_say('https://tse4-mm.cn.bing.net/th/id/OIP-C.cy76ifbr2oQPMEs2H82D-QHaEv?w=284&h=181&c=7&r=0&o=5&dpr=1.5&pid=1.7', MsgType.IMAGE)

    chat_box.robot_say('https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4', MsgType.VIDEO, format='viedo/mp4')

    chat_box.robot_say('https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4', MsgType.AUDIO, format='audio/mp4')

chat_box.output_messages()

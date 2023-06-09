# Attention!

Since version 1.24.0 streamlit provides official elements to [build conversational apps](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps).

The new elements are more flexible, extensible and better supported, I would suggest to use them. 

However, streamlit>=1.23 requires protobuf>=4 when some package requires protobuf<=3. In this condition you can use this package with streamlit<=1.22 as alternative. They are all simple to render text messages.


# Chatbox component for streamlit

A Streamlit component to show chat messages.

## Features

- user can custom the bg_color and icon of message senders.
- support streaming output.
- support image/video/audio messages


This make it easy to chat with LLMs in streamlit.


## Install

just `pip install streamlit-chatbox`

## Usage examples

```python
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
```

![demo](https://github.com/liunux4odoo/streamlit-chatbox/blob/master/demo.gif)


## Todos

- input messages:
	- [x] TEXT
	- [ ] IMAGE
		- [ ] file upload
		- [ ] paste from clipboard(streamlit_bokeh_events)
	- [ ] VIDEO
		- [ ] file upload
	- [ ] AUDIO
		- [ ] file upload
		- [ ] audio-recorder-streamlit

- output messages:
	- [x] TEXT
	- [x] IMAGE
	- [x] VIDEO
	- [x] AUDIO

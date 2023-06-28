import streamlit as st
import time
# from streamlit_option_menu import option_menu


class MsgType:
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    AUDIO = 4


class StChatBox:
    def __init__(
        self,
        chat_box,
        session_var='chat_box',
        greetings=[],
        box_margin='10%',
        box_border='1px solid',
        user_bg_color='#77ff77',
        user_icon='',
        robot_bg_color='#ccccee',
        robot_icon='',
    ):
        self.session_var = session_var
        self.greetings = greetings
        self.box_margin = box_margin
        self.box_border = box_border
        self.user_bg_color = user_bg_color
        self.user_icon = user_icon
        self.robot_bg_color = robot_bg_color
        self.robot_icon = robot_icon
        self.last_response = None
        self.chat_box = chat_box
        self.init_session()
        self.show_welcome()

    def init_session(self):
        st.session_state.setdefault(
            self.session_var, {'history': [], 'welcomed': False})

    @property
    def history(self):
        return st.session_state.get(self.session_var, {}).get('history', [])

    @property
    def welcomed(self):
        return st.session_state.get(self.session_var, {}).get('welcomed', False)

    @welcomed.setter
    def welcomed(self, val):
        st.session_state[self.session_var]['welcomed'] = bool(val)

    def format_md(self, msg, is_user=False, bg_color=None, margin=None, border=None):
        '''
        将文本消息格式化为markdown文本
        '''
        msg = '\n' + msg.strip() # prepend '\n' to make first line paragraph
        margin = margin or self.box_margin
        border = border or self.box_border
        if is_user:
            bg_color = bg_color or self.user_bg_color
            text = f'''
                    <div style="background:{bg_color};
                            margin-left:{margin};
                            border: {border};
                            word-break:break-all;
                            float:right;
                            padding:2%;
                            border-radius:0 20px 0 0;">
                    {msg}
                    </div>
                    '''
        else:
            bg_color = bg_color or self.robot_bg_color
            text = f'''
                    <div style="background:{bg_color};
                            margin-right:{margin};
                            border: {border};
                            word-break:break-all;
                            padding:2%;
                            border-radius:20px 0 0 0;">
                    {msg}
                    </div>
                    '''
        return text

    def robot_say(self, msg, msg_type=MsgType.TEXT, **kw):
        kw.update(is_user=False, content=msg, msg_type=msg_type)
        self.history.append(kw)

    def user_say(self, msg, msg_type=MsgType.TEXT, **kw):
        kw.update(is_user=True, content=msg, msg_type=msg_type)
        self.history.append(kw)

    def render_msg(self,
                   msg,
                   is_user=False,
                   msg_type=MsgType.TEXT,
                   icon=None,
                   bg_color=None,
                   margin=None,
                   **kw,
                   ):
        '''
        渲染单条消息。
        '''
        margin = margin or self.box_margin
        cols = st.columns([1, 10, 1])
        empty = cols[1].empty()
        if is_user:
            icon = icon or self.user_icon
            bg_color = bg_color or self.user_bg_color
            if icon:
                cols[2].image(icon, width=40)
            if msg_type == MsgType.TEXT:
                text = self.format_md(msg, is_user, bg_color, margin)
                empty.markdown(text, unsafe_allow_html=True)
            elif msg_type == MsgType.IMAGE:
                empty.image(msg, use_column_width='auto')
            elif msg_type == MsgType.VIDEO:
                empty.video(msg, format=kw.get('format', 'video/mp4'))
            elif msg_type == MsgType.AUDIO:
                empty.audio(msg, format=kw.get('format', 'audio/wav'))
            else:
                raise RuntimeError(f'unsupported message type: {msg_type} .')
        else:
            icon = icon or self.robot_icon
            bg_color = bg_color or self.robot_bg_color
            if icon:
                cols[0].image(icon, width=40)
            if msg_type == MsgType.TEXT:
                text = self.format_md(msg, is_user, bg_color, margin)
                empty.markdown(text, unsafe_allow_html=True)
            elif msg_type == MsgType.IMAGE:
                empty.image(msg, use_column_width='auto')
            elif msg_type == MsgType.VIDEO:
                empty.video(msg, format=kw.get('format', 'video/mp4'))
            elif msg_type == MsgType.AUDIO:
                empty.audio(msg, format=kw.get('format', 'audio/wav'))
            else:
                raise RuntimeError(f'unsupported message type: {msg_type} .')
        return empty

    def show_welcome(self):
        if self.greetings and not self.welcomed:
            greetings = self.greetings
            if not isinstance(greetings, list):
                greetings = [greetings]
            for g in greetings:
                if isinstance(g, str):
                    self.robot_say(g)
                elif isinstance(g, dict):
                    self.robot_say(**g)
            self.welcomed = True

    def output_messages(
        self,
        user_bg_color=None,
        robot_bg_color=None,
        user_icon=None,
        robot_icon=None,
    ):
        with self.chat_box.container():
            for msg in self.history:
                bg_color = user_bg_color if msg['is_user'] else robot_bg_color
                icon = user_icon if msg['is_user'] else robot_icon
                empty = self.render_msg(msg['content'],
                                        is_user=msg['is_user'],
                                        icon=icon,
                                        msg_type=msg['msg_type'],
                                        bg_color=bg_color,

                                        )
                if not msg['is_user']:
                    self.last_response = empty
        return self.last_response

    def update_last_box_text(self, msg):
        if self.last_response is not None:
            self.history[-1]['content'] = msg
            self.last_response.markdown(
                self.format_md(msg, False),
                unsafe_allow_html=True
            )

    def robot_stream(self, msg, init_msg='', words_per_sec=10, max_seconds=10):
        step = max(words_per_sec, len(msg) // max_seconds + 1) // 5 + 1
        self.robot_say(init_msg)
        self.output_messages()
        for i in range(step, len(msg) + step * 2, step):
            time.sleep(0.2)
            self.update_last_box_text(msg[:i])

    def clear_history(self, welcome_again=False):
        self.history = []
        if welcome_again:
            self.show_welcome()


def st_chatbox(
        session_var='chat_box',
        greetings=[],
        box_margin='10%',
        box_border='1px solid',
        user_bg_color='#77ff77',
        user_icon='https://tse2-mm.cn.bing.net/th/id/OIP-C.LTTKrxNWDr_k74wz6jKqBgHaHa?w=203&h=203&c=7&r=0&o=5&pid=1.7',
        robot_bg_color='#ccccee',
        robot_icon='https://ts1.cn.mm.bing.net/th/id/R-C.5302e2cc6f5c7c4933ebb3394e0c41bc?rik=z4u%2b7efba5Mgxw&riu=http%3a%2f%2fcomic-cons.xyz%2fwp-content%2fuploads%2fStar-Wars-avatar-icon-C3PO.png&ehk=kBBvCvpJMHPVpdfpw1GaH%2brbOaIoHjY5Ua9PKcIs%2bAc%3d&risl=&pid=ImgRaw&r=0',
):
    '''
    :param session_var: variable name used to store chat history in session_state
    :param greetings: show messages when chat box first inited
    :param box_margin: blank area of a single message box
    :param user_bg_color: background color of user's message box
    :param user_icon: icon of user
    :param robot_bg_color: background color of robot's message box
    :param robot_icon: icon of robot
    :return: instance of StChatBox, use it to append and render messages
    '''
    empty = st.empty()
    return StChatBox(
        chat_box=empty,
        session_var=session_var,
        greetings=greetings,
        box_margin=box_margin,
        box_border=box_border,
        user_bg_color=user_bg_color,
        user_icon=user_icon,
        robot_bg_color=robot_bg_color,
        robot_icon=robot_icon
    )


def _msg_type_format_func(val):
    return {
        MsgType.TEXT: 'TEXT',
        MsgType.IMAGE: 'IMAGE',
        MsgType.VIDEO: 'VIDEO',
        MsgType.AUDIO: 'AUDIO',
    }[val]


# def st_chat_input(
#     prefix='chat',
#     send_btn='send',
#     ):

#     cols1 = st.columns([1, 5])
#     msg_type = cols1[0].selectbox(
#                     'MsgType',
#                     [MsgType.TEXT, MsgType.IMAGE, MsgType.VIDEO, MsgType.AUDIO],
#                     # label_visibility='collapsed',
#                     format_func=_msg_type_format_func,
#                     )
#     with cols1[1].form(f'{prefix}_input_form', clear_on_submit=True):
#         cols2 = st.columns([5, 1])
#         if msg_type == MsgType.TEXT:
#             msg = cols2[0].text_input('text', label_visibility='collapsed')
#         elif msg_type == MsgType.IMAGE:
#             msg = None
#             cols3 = cols2[0].columns(2)
#             file = cols3[0].file_uploader('file', ['jpg', 'bmp', 'jpeg', 'png'], label_visibility='collapsed')
#             clipboard = cols3[0].button('从剪切板粘贴')
#             if file:
#                 cols3[1].image(file)
#                 msg = file.getvalue()
                

#         submit = cols2[1].form_submit_button(send_btn)

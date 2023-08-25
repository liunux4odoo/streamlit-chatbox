from streamlit_chatbox.elements import *
import time
import inspect
import simplejson as json


class ChatBox:
    def __init__(
        self,
        chat_name: str = "default",
        session_key: str = "messages",
        user_avatar: str = "user",
        assistant_avatar: str = "assistant",
        greetings: Union[str, OutputElement, List[Union[str, OutputElement]]] = [],
    ) -> None:
        self._chat_name = chat_name
        self._session_key = session_key
        self._user_avatar = user_avatar
        self._assistant_avatar = assistant_avatar
        if not isinstance(greetings, list):
            greetings = [greetings]
        for i, greeting in enumerate(greetings):
            if isinstance(greeting, str):
                greetings[i] = Markdown(greeting)
        self._greetings = greetings


    @property
    def chat_inited(self):
        return self._session_key in st.session_state

    def init_session(self, clear: bool =False):
        if not self.chat_inited or clear:
            st.session_state[self._session_key] = {}
            self.reset_history(self._chat_name)

    def reset_history(self, name=None):
        assert self.chat_inited, "please call init_session first"
        name = name or self._chat_name
        st.session_state[self._session_key].update({name: []})
        if self._greetings:
            st.session_state[self._session_key][name] = [{
                    "role": "assistant",
                    "elements": self._greetings,
            }]

    def use_chat_name(self, name: str ="default") -> None:
        assert self.chat_inited, "please call init_session first"
        self._chat_name = name
        if name not in st.session_state[self._session_key]:
            self.reset_history(name)

    def del_chat_name(self, name: str):
        assert self.chat_inited, "please call init_session first"
        if name in st.session_state[self._session_key]:
            msgs = st.session_state[self._session_key].pop(name)
            self._chat_name=self.get_chat_names()[0]
        return msgs

    def get_chat_names(self):
        assert self.chat_inited, "please call init_session first"
        return list(st.session_state[self._session_key].keys())

    @property
    def cur_chat_name(self):
        return self._chat_name

    @property
    def history(self) -> List:
        assert self.chat_inited, "please call init_session first"
        return st.session_state[self._session_key].get(self._chat_name, [])

    def other_history(self, chat_name: str, default: List=[]) -> Optional[List]:
        assert self.chat_inited, "please call init_session first"
        chat_name = chat_name or self.cur_chat_name
        return st.session_state[self._session_key].get(chat_name, default)

    def filter_history(
        self,
        history_len: int = None,
        filter: Callable = None,
        stop: Callable = None,
        chat_name: str = None,
    ) -> List:
        '''
        history_len: the length of conversation pairs
        filter: custom filter fucntion with arguments (msg,) or (msg, index), return None if skipping msg. default filter returns all text/markdown content.
        stop: custom function to stop filtering with arguments (history,) history is already filtered messages, return True if stop. default stop on history_len
        '''
        assert self.chat_inited, "please call init_session first"

        def default_filter(msg, index=None):
            '''
            filter text messages only with the format {"role":role, "content":content}
            '''
            content = [x._content for x in msg["elements"] if x._output_method in ["markdown", "text"]]
            return {
                "role": msg["role"],
                "content": "\n\n".join(content),
            }

        def default_stop(history):
            if isinstance(history_len, int):
                ai_count = len(x for x in history if x["role"] == "user")
                return ai_count >= history_len
            else:
                return False

        if filter is None:
            filter = default_filter

        if stop is None:
            stop = default_stop

        result = []
        args_len = len(inspect.signature(filter).parameters)
        history = self.other_history(chat_name)
        for i, msg in enumerate(history[-1::-1]):
            if args_len == 1:
                filtered = filter(msg)
            else:
                filtered = filter(msg, i)
            if filtered is not None:
                result.insert(0, filtered)
                if isinstance(history_len, int) and len(result) >= history_len:
                    break

        return result

    def export2md(
        self,
        chat_name: str = None,
        filter: Callable = None,
        user_avatar: str = "User",
        ai_avatar: str = "AI",
        user_bg_color: str = "#DCFDC8",
        ai_bg_color: str = "#E0F7FA",
        callback: Callable = None,
    ) -> List[str]:
        '''
        default export messages as table of text.
        use callback(msg) to custom exported content.
        '''
        assert self.chat_inited, "please call init_session first"
        lines = [
            "<style> td, th {border: none!important;}</style>\n"
            "|  |  |\n",
            "|--|--|\n",
        ]
        def set_bg_color(text, bg_color):
            text = text.replace("\n", "<br>")
            return f"<div style=\"background-color:{bg_color}\">{text}</div>"

        history = self.other_history(chat_name)
        for msg in history:
            if callable(callback):
                line = callback(msg)
            else:
                contents = [e._content for e in msg["elements"]]
                if msg["role"] == "user":
                    content = "<br><br>".join(set_bg_color(c, user_bg_color) for c in contents)
                    avatar = set_bg_color(user_avatar, user_bg_color)
                else:
                    avatar = set_bg_color(ai_avatar, ai_bg_color)
                    content = "<br><br>".join(set_bg_color(c, ai_bg_color) for c in contents)
                line = f"|{avatar}|{content}|\n"
            lines.append(line)
        return lines

    def to_dict(
        self,
    ) -> Dict:
        '''
        export current state to dict
        '''
        assert self.chat_inited, "please call init_session first"

        def p(val):
            if isinstance(val, (list, tuple)):
                return [p(x) for x in val]
            elif isinstance(val, dict):
                return {k: p(v) for k, v in val.items()}
            elif isinstance(val, OutputElement):
                return val.to_dict()
            else:
                return val

        histories = {x: p(self.other_history(x)) for x in self.get_chat_names()}
        return {
            "cur_chat_name": self.cur_chat_name,
            "session_key": self._session_key,
            "user_avatar": self._user_avatar,
            "assistant_avatar": self._assistant_avatar,
            "greetings": p(self._greetings),
            "histories": histories,
        }

    def to_json(
        self,
        pretty: bool = True,
    ) -> str:
        data = self.to_dict()
        kwargs = {"ensure_ascii": False}
        if pretty:
            kwargs["indent"] = 2
        return json.dumps(data, **kwargs)

    def from_dict(
        self,
        data: Dict,
    ) -> "ChatBox":
        '''
        load state from dict
        '''
        self._chat_name=data["cur_chat_name"]
        self._session_key=data["session_key"]
        self._user_avatar=data["user_avatar"]
        self._assistant_avatar=data["assistant_avatar"]
        self._greetings=[OutputElement.from_dict(x) for x in data["greetings"]]
        self.init_session(clear=True)

        for name, history in data["histories"].items():
            self.reset_history(name)
            for h in history:
                msg = {
                    "role": h["role"],
                    "elements": [OutputElement.from_dict(y) for y in h["elements"]],
                    }
                self.other_history(name).append(msg)

        self.use_chat_name(data["cur_chat_name"])
        return self

    def _prepare_elements(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]],
    ) -> List[OutputElement]:
        if isinstance(elements, str):
            elements = [Markdown(elements)]
        elif isinstance(elements, OutputElement):
            elements = [elements]
        elif isinstance(elements, list):
            elements = [Markdown(e) if isinstance(
                e, str) else e for e in elements]
        return elements

    def user_say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]],
        to_history: bool = True,
        not_render: bool = False,
    ) -> List[OutputElement]:
        assert self.chat_inited, "please call init_session first"
        elements = self._prepare_elements(elements)
        if not not_render:
            with st.chat_message("user", avatar=self._user_avatar):
                for element in elements:
                    element()
        if to_history:
            self.history.append({"role": "user", "elements": elements})
        return elements

    def ai_say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]],
        to_history: bool = True,
        not_render: bool = False,
    ) -> List[OutputElement]:
        assert self.chat_inited, "please call init_session first"
        elements = self._prepare_elements(elements)
        if not not_render:
            with st.chat_message("assistant", avatar=self._assistant_avatar):
                for element in elements:
                    element()
        if to_history:
            self.history.append({"role": "assistant", "elements": elements})
        return elements

    def output_messages(self):
        assert self.chat_inited, "please call init_session first"
        for msg in self.history:
            avatar = self._user_avatar if msg["role"] == "user" else self._assistant_avatar
            with st.chat_message(msg["role"], avatar=avatar):
                for element in msg["elements"]:
                    element()

    def update_msg(
        self,
        element: Union["OutputElement", str],
        element_index: int = -1,
        history_index: int = -1,
        streaming: Optional[bool] = None,
    ) -> st._DeltaGenerator:
        assert self.chat_inited, "please call init_session first"
        if isinstance(element, str):
            element = Markdown(element)
            if streaming is None:
                streaming = True
        if streaming and isinstance(element, Markdown):
            element._content += " ▌"

        old_element = self.history[history_index]["elements"][element_index]
        dg = old_element.update_element(
            element, streaming
        )
        element.attrs_from(old_element)
        self.history[history_index]["elements"][element_index] = element
        return dg


class FakeLLM:
    def _answer(self, query: str) -> str:
        answer = f"this is my answer for your question:\n\n{query}"
        docs = ["reference 1", "reference 2", "reference 3"]
        return answer, docs

    def chat(self, query: str) -> str:
        return self._answer(query)

    def chat_stream(self, query: str):
        text, docs = self._answer(query)
        for t in text:
            yield t, docs
            time.sleep(0.1)

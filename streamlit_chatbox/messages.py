from streamlit_chatbox.elements import *
import time


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
        self.init_session()

    def init_session(self):
        if self._session_key not in st.session_state:
            st.session_state[self._session_key] = {}
            self.reset_history("default")

    def reset_history(self, name=None):
        name = name or self._chat_name
        st.session_state[self._session_key].update({
            name: [{
                "role": "assistant",
                "elements": self._greetings,
        }]})

    def use_chat_name(self, name: str ="default") -> None:
        self._chat_name = name
        if name not in st.session_state[self._session_key]:
            self.reset_history(name)

    def del_chat_name(self, name: str):
        if name in st.session_state[self._session_key]:
            msgs = st.session_state[self._session_key].pop(name)
            self._chat_name=self.get_chat_names()[0]
        return msgs

    def get_chat_names(self):
        return list(st.session_state[self._session_key].keys())

    @property
    def cur_chat_name(self):
        return self._chat_name

    @property
    def history(self) -> List:
        return st.session_state.get(self._session_key).get(self._chat_name)

    def filter_history(
        self,
        history_len: int,
        filter: Callable = None,
    ) -> List:
        def default_filter(index, msg):
            '''
            filter text messages only with the format {"role":role, "content":content}
            '''
            content = [x._content for x in msg["elements"] if x._output_method in ["markdown", "text"]]
            return {
                "role": msg["role"],
                "content": "\n\n".join(content),
            }

        if filter is None:
            filter = default_filter

        result = []
        for msg in self.history[-1::-1]:
            filtered = filter(msg)
            if filtered is not None:
                result.insert(0, filtered)
                if len(result) >= history_len:
                    break

        return result

    def export2md(self, chat_name: str ="default", filter: Callable =None) -> List[str]:
        lines = [
            "<style> td, th {border: none!important;}</style>\n"
            "|  |  |\n",
            "|--|--|\n",
        ]
        for msg in self.history:
            if msg["role"] == "user":
                avatar = '''<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp51 css-fblp2m ex0cdmw0"><path fill="none" d="M0 0h24v24H0V0z"></path><path d="M10.25 13a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0zM15 11.75a1.25 1.25 0 100 2.5 1.25 1.25 0 000-2.5zm7 .25c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2s10 4.48 10 10zM10.66 4.12C12.06 6.44 14.6 8 17.5 8c.46 0 .91-.05 1.34-.12C17.44 5.56 14.9 4 12 4c-.46 0-.91.05-1.34.12zM4.42 9.47a8.046 8.046 0 003.66-4.44 8.046 8.046 0 00-3.66 4.44zM20 12c0-.78-.12-1.53-.33-2.24-.7.15-1.42.24-2.17.24a10 10 0 01-7.76-3.69A10.016 10.016 0 014 11.86c.01.04 0 .09 0 .14 0 4.41 3.59 8 8 8s8-3.59 8-8z"></path></svg>'''
            else:
                avatar = '''<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp51 css-fblp2m ex0cdmw0"><rect width="24" height="24" fill="none"></rect><path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zm-2 10H6V7h12v12zm-9-6c-.83 0-1.5-.67-1.5-1.5S8.17 10 9 10s1.5.67 1.5 1.5S9.83 13 9 13zm7.5-1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zM8 15h8v2H8v-2z"></path></svg>'''
            content = "\n\n".join(e._content for e in msg["elements"])
            line = f"|{avatar}|{content}|\n"
            lines.append(line)
        return lines

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
        elements = self._prepare_elements(elements)
        if not not_render:
            with st.chat_message("assistant", avatar=self._assistant_avatar):
                for element in elements:
                    element()
        if to_history:
            self.history.append({"role": "assistant", "elements": elements})
        return elements

    def output_messages(self):
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

from streamlit_chatbox.elements import *
import time


class ChatBox:
    def __init__(
        self,
        session_name: str = "messages",
        user_avatar: str = "user",
        assistant_avatar: str = "assistant",
    ) -> None:
        self._session_name = session_name
        self._user_avatar = user_avatar
        self._assistant_avatar = assistant_avatar
        st.session_state.setdefault(self._session_name, [])

    @property
    def history(self):
        return st.session_state.get(self._session_name, [])

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
    ) -> List[OutputElement]:
        elements = self._prepare_elements(elements)
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
    ) -> List[OutputElement]:
        elements = self._prepare_elements(elements)
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

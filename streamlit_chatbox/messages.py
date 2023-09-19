from streamlit_chatbox.elements import *
import time
import inspect
import simplejson as json


# main concept：
# ChatBox is the top level object, repsents all history messages。
# every message is feed to st.chat_message，including two objects：
#   - role
#   - elements: list of OutputElement to render. every element includes：
#       - content and output_method, ie. st.output_method(content, **kwargs)
#       - in_exapander decides the element is rendered directly or in st.status
#           - if directly: element is rendered in a st.empty in the st.container
#           - if in expander: element is rendered in a st.empty in the st.status


class ChatBox:
    def __init__(
        self,
        chat_name: str = "default",
        session_key: str = "chat_history",
        user_avatar: str = "user",
        assistant_avatar: str = "assistant",
        greetings: Union[str, OutputElement, List[Union[str, OutputElement]]] = [],
    ) -> None:
        self._chat_name = chat_name
        self._chat_containers = []
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
        return self._session_key in st.session_state.keys()

    def init_session(self, clear: bool =False):
        if not self.chat_inited or clear:
            st.session_state[self._session_key] = {}
            time.sleep(0.1)
            self.reset_history(self._chat_name)

    def reset_history(self, name=None):
        if not self.chat_inited:
            st.session_state[self._session_key] = {}

        name = name or self._chat_name
        st.session_state[self._session_key][name] = []
        if self._greetings:
            st.session_state[self._session_key][name] = [{
                    "role": "assistant",
                    "elements": self._greetings,
                    "metadata": {},
            }]

    def use_chat_name(self, name: str ="default") -> None:
        self.init_session()
        self._chat_name = name
        if name not in st.session_state[self._session_key]:
            self.reset_history(name)

    def del_chat_name(self, name: str):
        self.init_session()
        if name in st.session_state[self._session_key]:
            msgs = st.session_state[self._session_key].pop(name)
            self._chat_name=self.get_chat_names()[0]
        return msgs

    def get_chat_names(self):
        self.init_session()
        return list(st.session_state[self._session_key].keys())

    @property
    def cur_chat_name(self):
        return self._chat_name

    @property
    def history(self) -> List:
        self.init_session()
        return st.session_state[self._session_key].get(self._chat_name, [])

    def other_history(self, chat_name: str, default: List=[]) -> Optional[List]:
        self.init_session()
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
        self.init_session()

        def default_filter(msg, index=None):
            '''
            filter text messages only with the format {"role":role, "content":content}
            '''
            content = [x.content for x in msg["elements"] if x._output_method in ["markdown", "text"]]
            return {
                "role": msg["role"],
                "content": "\n\n".join(content),
            }

        def default_stop(history):
            if isinstance(history_len, int):
                user_count = len([x for x in history if x["role"] == "user"])
                return user_count >= history_len
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

            if stop(history):
                break

        return result

    def export2md(
        self,
        chat_name: str = None,
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
        self.init_session()
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
                contents = [e.content for e in msg["elements"]]
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
        self.init_session()

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
        return elements or []

    def user_say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]] = None,
        metadata: Dict = {},
    ) -> List[OutputElement]:
        self.init_session()
        elements = self._prepare_elements(elements)

        chat_ele = st.chat_message("user", avatar=self._user_avatar)
        self._chat_containers.append(chat_ele)
        for element in elements:
            element(render_to=chat_ele)

        self.history.append({"role": "user", "elements": elements, "metadata": metadata})
        return elements

    def ai_say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]] = None,
        metadata: Dict = {},
    ) -> List[OutputElement]:
        self.init_session()
        elements = self._prepare_elements(elements)

        chat_ele = st.chat_message("assistant", avatar=self._assistant_avatar)
        container = chat_ele.container()
        self._chat_containers.append(container)
        for element in elements:
            element(render_to=container)

        self.history.append({"role": "assistant", "elements": elements, "metadata": metadata})
        return elements

    def output_messages(self):
        self.init_session()
        self._chat_containers = []
        for msg in self.history:
            avatar = self._user_avatar if msg["role"] == "user" else self._assistant_avatar
            chat_ele = st.chat_message(msg["role"], avatar=avatar)
            container = chat_ele.container()
            self._chat_containers.append(container)
            for element in msg["elements"]:
                element(render_to=container)

    def update_msg(
        self,
        element: Union["OutputElement", str] = None,
        *,
        element_index: int = -1,
        history_index: int = -1,
        streaming: Optional[bool] = None,
        title: str = None,
        expanded: bool = None,
        state: bool = None,
    ) -> st._DeltaGenerator:
        self.init_session()
        if not self.history or not self.history[history_index]["elements"]:
            return

        if isinstance(element, str):
            element = Markdown(element)
            if streaming is None:
                streaming = True
        if streaming and isinstance(element, Markdown):
            element._content += " ▌"

        old_element: OutputElement = self.history[history_index]["elements"][element_index]
        if element is not None:
            element.status_from(old_element)
            self.history[history_index]["elements"][element_index] = element

        dg = old_element.update_element(
            element,
            title=title,
            expanded=expanded,
            state=state,
        )
        return dg

    def insert_msg(
        self,
        element: Union["OutputElement", str],
        *,
        history_index: int = -1,
        pos: int = -1,
    ) -> OutputElement:
        self.init_session()
        if isinstance(element, str):
            element = Markdown(element)
        elements = self.history[history_index]["elements"]
        if pos < 0:
            pos += len(elements) + 1
        elements.insert(pos, element)

        element(render_to=self._chat_containers[history_index])
        return element


class FakeLLM:
    def _answer(self, query: str) -> str:
        answer = f"this is llm answer for your question:\n\n{query}"
        docs = ["reference 1", "reference 2", "reference 3"]
        return answer, docs

    def chat(self, query: str) -> str:
        return self._answer(query)

    def chat_stream(self, query: str):
        text, docs = self._answer(query)
        for t in text:
            yield t, docs
            time.sleep(0.1)


class FakeAgent:
    llm = FakeLLM()
    tools = ["search", "math"]

    def thought(self, msg):
        return f"thought {msg}"

    def action(self, msg):
        return f"action {msg}"

    def run(self, query: str = "", steps: int = 2):
        result = []
        for i in range(1, steps + 1):
            thought = self.thought(i)
            result.append({
                "type": "thought",
                "id": i,
                "text": thought,
                "llm_output": self.llm.chat(thought)[0]
            })

            action = self.action(i)
            result.append({
                "type": "action",
                "id": i,
                "text": action,
                "llm_output": self.llm.chat(action)[0]
            })

        result.append({
            "type": "complete",
            "llm_output": "final answer"
        })

        return result

    def run_stream(self, query: str = "", steps: int = 2):
        for i in range(1, steps + 1):
            thought = self.thought(i)

            yield {
                "type": "thought",
                "id": i,
                "text": thought,
                "status": 1,
                "llm_output": "",
            }

            for chunk, _ in self.llm.chat_stream(thought):
                d = {
                    "type": "thought",
                    "id": i,
                    "text": thought,
                    "status": 2,
                    "llm_output": chunk,
                }
                print(d)
                yield d

            yield {
                "type": "thought",
                "id": i,
                "text": thought,
                "status": 3,
                "llm_output": "",
            }

            action = self.action(i)
            yield {
                "type": "action",
                "id": i,
                "text": action,
                "status": 1,
                "llm_output": "",
            }

            for chunk, _ in self.llm.chat_stream(action):
                d = {
                    "type": "action",
                    "id": i,
                    "text": action,
                    "status": 2,
                    "llm_output": chunk,
                }
                print(d)
                yield d

            yield {
                "type": "action",
                "id": i,
                "text": action,
                "status": 3,
                "llm_output": "",
            }

        yield {
            "type": "complete",
            "llm_output": "final answer"
        }

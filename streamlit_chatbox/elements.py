from typing import *
import streamlit as st
from pydantic import BaseModel, Field


class Element:
    '''
    wrapper of streamlit component to make them suitable for chat history.
    '''

    def __init__(self,
                 output_method: str = "markdown",
                 *args: Any,
                 **kwargs: Any,
                 ) -> None:
        self._output_method = output_method
        self._args = args
        self._kwargs = kwargs
        self._defualt_kwargs = {
            "markdown": {
                "unsafe_allow_html": True,
            },
            "audio": {
                "format": "mp3",
            },
            "vidio": {
                "format": "mp4",
            },
            "image": {
                "use_column_width": "auto",
            },
        }
        self._set_default_kwargs()
        self._element = None
        self._place_holder = None

    def _set_default_kwargs(self) -> None:
        if default := self._defualt_kwargs.get(self._output_method):
            for k, v in default.items():
                self._kwargs.setdefault(k, v)

    def __call__(self) -> st._DeltaGenerator:
        # assert self._element is None, "Every element can be rendered once only."
        self._place_holder = st.empty()
        output_method = getattr(self._place_holder, self._output_method)
        assert callable(
            output_method), f"The attribute st.{self._output_mehtod} is not callable."
        self._element = output_method(*self._args, **self._kwargs)
        return self._element


class OutputElement(Element):
    def __init__(self,
                 content: Union[str, bytes] = "",
                 output_method: str = "markdown",
                 title: str = "",
                 in_expander: bool = False,
                 expanded: bool = False,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(output_method=output_method, **kwargs)
        self._content = content
        self._title = title
        self._in_expander = in_expander
        self._expanded = expanded

    def __call__(self) -> st._DeltaGenerator:
        self._args = (self._content,)
        if self._in_expander:
            with st.expander(self._title, self._expanded):
                return super().__call__()
        else:
            return super().__call__()

    def __repr__(self) -> str:
        method = self._output_method.capitalize()
        return f"{method} Element:\n{self._content}"

    def update_element(
        self,
        element: Union["OutputElement", str],
        streaming: Optional[bool] = None,
    ) -> st._DeltaGenerator:
        assert self._place_holder is not None, "You must render the element before setting new element."
        if isinstance(element, str):
            element = Markdown(element)
            if streaming is None:
                streaming = True
        if streaming and isinstance(element, Markdown):
            element._content += " ▌"
        with self._place_holder:
            self._element = element()
        return self._element


class InputElement(Element):
    pass


class Markdown(OutputElement):
    def __init__(self, content: Union[str, bytes] = "", title: str = "", in_expander: bool = False, expanded: bool = False, **kwargs: Any) -> None:
        super().__init__(content, output_method="markdown", title=title,
                         in_expander=in_expander, expanded=expanded, **kwargs)


class Image(OutputElement):
    def __init__(self, content: Union[str, bytes] = "", title: str = "", in_expander: bool = False, expanded: bool = False, **kwargs: Any) -> None:
        super().__init__(content, output_method="image", title=title,
                         in_expander=in_expander, expanded=expanded, **kwargs)


class Audio(OutputElement):
    def __init__(self, content: Union[str, bytes] = "", title: str = "", in_expander: bool = False, expanded: bool = False, **kwargs: Any) -> None:
        super().__init__(content, output_method="audio", title=title,
                         in_expander=in_expander, expanded=expanded, **kwargs)


class Video(OutputElement):
    def __init__(self, content: Union[str, bytes] = "", title: str = "", in_expander: bool = False, expanded: bool = False, **kwargs: Any) -> None:
        super().__init__(content, output_method="video", title=title,
                         in_expander=in_expander, expanded=expanded, **kwargs)

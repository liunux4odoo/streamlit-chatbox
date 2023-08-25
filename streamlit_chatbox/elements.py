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
        self._dg = None
        self._place_holder = None

    def _set_default_kwargs(self) -> None:
        if default := self._defualt_kwargs.get(self._output_method):
            for k, v in default.items():
                self._kwargs.setdefault(k, v)

    def __call__(self) -> st._DeltaGenerator:
        # assert self._dg is None, "Every element can be rendered once only."
        self._place_holder = st.empty()
        output_method = getattr(self._place_holder, self._output_method)
        assert callable(
            output_method), f"The attribute st.{self._output_mehtod} is not callable."
        self._dg = output_method(*self._args, **self._kwargs)
        return self._dg


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

    def to_dict(self) -> Dict:
        return {
            "content": self._content,
            "output_method": self._output_method,
            "title": self._title,
            "in_expander": self._in_expander,
            "expanded": self._expanded,
            "kwargs": self._kwargs,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "OutputElement":
        cls_maps = {
            "markdown": Markdown,
            "image": Image,
            "audio": Audio,
            "video": Video,
        }

        factory_cls = cls_maps.get(d.get("output_method"), cls)
        kwargs = dict(
            content=d.get("content"),
            title=d.get("title"),
            in_expander=d.get("in_expander"),
            expanded=d.get("expanded"),
            **d.get("kwargs", {}),
            )
        if factory_cls is cls:
            kwargs["output_method"] = d.get("output_method")

        return factory_cls(**kwargs)

    def update_element(
        self,
        element: "OutputElement",
        streaming: Optional[bool] = None,
    ) -> st._DeltaGenerator:
        assert self._place_holder is not None, "You must render the element before setting new element."
        with self._place_holder:
            self._dg = element()
        return self._dg

    def attrs_from(self, target):
        for attr in ["_in_expander", "_expanded", "_title"]:
            setattr(self, attr, getattr(target, attr))


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

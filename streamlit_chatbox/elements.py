from typing import *
import streamlit as st
# from pydantic import BaseModel, Field


class Element:
    '''
    wrapper of streamlit component to make them suitable for chat history.
    '''

    def __init__(self,
                 *,
                 output_method: str = "markdown",
                 metadata: Dict = {},
                 **kwargs: Any,
                 ) -> None:
        self._output_method = output_method
        self._metadata = metadata
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

    def __call__(self, render_to: st._DeltaGenerator=None) -> st._DeltaGenerator:
        # assert self._dg is None, "Every element can be rendered once only."
        render_to = render_to or st
        self._place_holder = render_to.empty()
        output_method = getattr(self._place_holder, self._output_method)
        assert callable(
            output_method), f"The attribute st.{self._output_mehtod} is not callable."
        self._dg = output_method(*self._args, **self._kwargs)
        return self._dg

    @property
    def dg(self) -> st._DeltaGenerator:
        return self._dg

    @property
    def place_holder(self) -> st._DeltaGenerator:
        return self._place_holder

    @property
    def metadata(self) -> Dict:
        return self._metadata


class OutputElement(Element):
    def __init__(self,
                 content: Union[str, bytes] = "",
                 output_method: str = "markdown",
                 title: str = "",
                 in_expander: bool = False,
                 expanded: bool = False,
                 state: Literal["running", "complete", "error"] = "running",
                 **kwargs: Any,
                 ) -> None:
        super().__init__(output_method=output_method, **kwargs)
        self._content = content
        self._title = title
        self._in_expander = in_expander
        self._expanded = expanded
        self._state = state
        self._attrs = ["_content", "_output_method", "_kwargs", "_metadata",
                       "_title", "_in_expander", "_expanded", "_state",]

    def clone(self) -> "OutputElement":
        obj = type(self)()
        for n in self._attrs:
            setattr(obj, n, getattr(self, n))
        return obj

    @property
    def content(self) -> Union[str, bytes]:
        return self._content

    def __repr__(self) -> str:
        method = self._output_method.capitalize()
        return f"{method} Element:\n{self.content}"

    def to_dict(self) -> Dict:
        return {
            "content": self._content,
            "output_method": self._output_method,
            "title": self._title,
            "in_expander": self._in_expander,
            "expanded": self._expanded,
            "state": self._state,
            "metadata": self._metadata,
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
            state=d.get("state"),
            metadata=d.get("metadata", {}),
            **d.get("kwargs", {}),
            )
        if factory_cls is cls:
            kwargs["output_method"] = d.get("output_method")

        return factory_cls(**kwargs)

    def __call__(self, render_to: st._DeltaGenerator=None, direct: bool=False) -> st._DeltaGenerator:
        if render_to is None:
            if self._place_holder is None:
                self._place_holder = st.empty()
        else:
            if direct:
                self._place_holder = render_to
            else:
                self._place_holder = render_to.empty()
        temp_dg = self._place_holder

        if self._in_expander:
            temp_dg = self._place_holder.status(self._title, expanded=self._expanded, state=self._state)
        output_method = getattr(temp_dg, self._output_method)
        assert callable(
            output_method), f"The attribute st.{self._output_mehtod} is not callable."
        self._dg = output_method(self._content, **self._kwargs)
        return self._dg

    def update_element(
        self,
        element: "OutputElement" = None,
        *,
        title: str = None,
        expanded: bool = None,
        state: bool = None,
    ) -> st._DeltaGenerator:
        assert self.place_holder is not None, f"You must render the element {self} before setting new element."
        attrs = {}
        if title is not None:
            attrs["_title"] = title
        if expanded is not None:
            attrs["_expanded"] = expanded
        if state is not None:
            attrs["_state"] = state

        if element is None:
            element = self
        for k, v in attrs.items():
            setattr(element, k, v)
        
        element(self.place_holder, direct=True)
        return self._dg

    def status_from(self, target):
        for attr in ["_in_expander", "_expanded", "_title", "_state"]:
            setattr(self, attr, getattr(target, attr))


class InputElement(Element):
    pass


class Markdown(OutputElement):
    def __init__(
        self,
        content: Union[str, bytes] = "",
        title: str = "",
        in_expander: bool = False,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        **kwargs: Any,
    ) -> None:
        super().__init__(content, output_method="markdown", title=title,
                         in_expander=in_expander, expanded=expanded,
                         state=state, **kwargs)


class Image(OutputElement):
    def __init__(
        self,
        content: Union[str, bytes] = "",
        title: str = "",
        in_expander: bool = False,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        **kwargs: Any,
    ) -> None:
        super().__init__(content, output_method="image", title=title,
                         in_expander=in_expander, expanded=expanded,
                         state=state, **kwargs)


class Audio(OutputElement):
    def __init__(
        self,
        content: Union[str, bytes] = "",
        title: str = "",
        in_expander: bool = False,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        **kwargs: Any,
    ) -> None:
        super().__init__(content, output_method="audio", title=title,
                         in_expander=in_expander, expanded=expanded,
                         state=state, **kwargs)


class Video(OutputElement):
    def __init__(
        self,
        content: Union[str, bytes] = "",
        title: str = "",
        in_expander: bool = False,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        **kwargs: Any,
    ) -> None:
        super().__init__(content, output_method="video", title=title,
                         in_expander=in_expander, expanded=expanded,
                         state=state, **kwargs)

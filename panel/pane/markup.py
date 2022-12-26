"""
Pane class which render various markup languages including HTML,
Markdown, and also regular strings.
"""
from __future__ import annotations

import json
import textwrap

from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional, Type,
)

import param

from ..models import HTML as _BkHTML, JSON as _BkJSON
from ..util import escape
from ..viewable import Layoutable
from .base import PaneBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class DivPaneBase(PaneBase):
    """
    Baseclass for Panes which render HTML inside a Bokeh Div.
    See the documentation for Bokeh Div for more detail about
    the supported options like style and sizing_mode.
    """

    style = param.Dict(default=None, doc="""
        Dictionary of CSS property:value pairs to apply to this Div.""")

    _bokeh_model: ClassVar[Model] = _BkHTML

    _rename: ClassVar[Mapping[str, str | None]] = {'object': 'text'}

    _updates: ClassVar[bool] = True

    __abstract = True

    def _get_properties(self):
        return {p : getattr(self, p) for p in list(Layoutable.param) + ['style']
                if getattr(self, p) is not None}

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self._bokeh_model(**self._get_properties())
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref: str, model: Model) -> None:
        model.update(**self._get_properties())


class HTML(DivPaneBase):
    """
    `HTML` panes renders HTML strings and objects with a `_repr_html_` method.

    The `height` and `width` can optionally be specified, to
    allow room for whatever is being wrapped.

    Reference: https://panel.holoviz.org/reference/panes/HTML.html

    :Example:

    >>> HTML(
    ...     "<h1>This is a HTML pane</h1>",
    ...     style={'background-color': '#F6F6F6'}
    ... )
    """

    disable_math = param.Boolean(default=True, doc="""
        Whether to disable support for MathJax math rendering for
        strings escaped with $$ delimiters.""")

    # Priority is dependent on the data type
    priority: ClassVar[float | bool | None] = None

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        module, name = getattr(obj, '__module__', ''), type(obj).__name__
        if ((any(m in module for m in ('pandas', 'dask')) and
            name in ('DataFrame', 'Series')) or hasattr(obj, '_repr_html_')):
            return 0.2
        elif isinstance(obj, str):
            return None
        else:
            return False

    def _get_properties(self):
        properties = super()._get_properties()
        text = '' if self.object is None else self.object
        if hasattr(text, '_repr_html_'):
            text = text._repr_html_()
        return dict(properties, text=escape(text))


class DataFrame(HTML):
    """
    The `DataFrame` pane renders pandas, dask and streamz DataFrame types using
    their custom HTML repr.

    In the case of a streamz DataFrame the rendered data will update
    periodically.

    Reference: https://panel.holoviz.org/reference/panes/DataFrame.html

    :Example:

    >>> DataFrame(df, index=False, max_rows=25, width=400)
    """

    bold_rows = param.Boolean(default=True, doc="""
        Make the row labels bold in the output.""")

    border = param.Integer(default=0, doc="""
        A ``border=border`` attribute is included in the opening
        `<table>` tag.""")

    classes = param.List(default=['panel-df'], doc="""
        CSS class(es) to apply to the resulting html table.""")

    col_space = param.ClassSelector(default=None, class_=(str, int), doc="""
        The minimum width of each column in CSS length units. An int
        is assumed to be px units.""")

    decimal = param.String(default='.', doc="""
        Character recognized as decimal separator, e.g. ',' in Europe.""")

    escape = param.Boolean(default=True, doc="""
        Whether or not to escape the dataframe HTML. For security reasons
        the default value is True.""")

    float_format = param.Callable(default=None, doc="""
        Formatter function to apply to columns' elements if they are
        floats. The result of this function must be a unicode string.""")

    formatters = param.ClassSelector(default=None, class_=(dict, list), doc="""
        Formatter functions to apply to columns' elements by position
        or name. The result of each function must be a unicode string.""")

    header = param.Boolean(default=True, doc="""
        Whether to print column labels.""")

    index = param.Boolean(default=True, doc="""
        Whether to print index (row) labels.""")

    index_names = param.Boolean(default=True, doc="""
        Prints the names of the indexes.""")

    justify = param.ObjectSelector(default=None, allow_None=True, objects=[
        'left', 'right', 'center', 'justify', 'justify-all', 'start',
        'end', 'inherit', 'match-parent', 'initial', 'unset'], doc="""
        How to justify the column labels.""")

    max_rows = param.Integer(default=None, doc="""
        Maximum number of rows to display.""")

    max_cols = param.Integer(default=None, doc="""
        Maximum number of columns to display.""")

    na_rep = param.String(default='NaN', doc="""
        String representation of NAN to use.""")

    render_links = param.Boolean(default=False, doc="""
        Convert URLs to HTML links.""")

    show_dimensions = param.Boolean(default=False, doc="""
        Display DataFrame dimensions (number of rows by number of
        columns).""")

    sparsify = param.Boolean(default=True, doc="""
        Set to False for a DataFrame with a hierarchical index to
        print every multi-index key at each row.""")

    _object = param.Parameter(default=None, doc="""Hidden parameter.""")

    _dask_params: ClassVar[List[str]] = ['max_rows']

    _rerender_params: ClassVar[List[str]] = [
        'object', '_object', 'bold_rows', 'border', 'classes',
        'col_space', 'decimal', 'escape', 'float_format', 'formatters',
        'header', 'index', 'index_names', 'justify', 'max_rows',
        'max_cols', 'na_rep', 'render_links', 'show_dimensions',
        'sparsify', 'sizing_mode'
    ]

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._stream = None
        self._setup_stream()

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        module = getattr(obj, '__module__', '')
        name = type(obj).__name__
        if (any(m in module for m in ('pandas', 'dask', 'streamz')) and
            name in ('DataFrame', 'Series', 'Random', 'DataFrames', 'Seriess', 'Styler')):
            return 0.3
        else:
            return False

    def _set_object(self, object):
        self._object = object

    @param.depends('object', watch=True)
    def _setup_stream(self):
        if not self._models or not hasattr(self.object, 'stream'):
            return
        elif self._stream:
            self._stream.destroy()
            self._stream = None
        self._stream = self.object.stream.latest().rate_limit(0.5).gather()
        self._stream.sink(self._set_object)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._setup_stream()
        return model

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        if not self._models and self._stream:
            self._stream.destroy()
            self._stream = None

    def _get_properties(self):
        properties = DivPaneBase._get_properties(self)
        if self._stream:
            df = self._object
        else:
            df = self.object
        if hasattr(df, 'to_frame'):
            df = df.to_frame()

        module = getattr(df, '__module__', '')
        if hasattr(df, 'to_html'):
            if 'dask' in module:
                html = df.to_html(max_rows=self.max_rows).replace('border="1"', '')
            elif 'style' in module:
                classes = ' '.join(self.classes)
                html = df.to_html(table_attributes=f'class="{classes}"')
            else:
                kwargs = {p: getattr(self, p) for p in self._rerender_params
                          if p not in DivPaneBase.param and p != '_object'}
                html = df.to_html(**kwargs)
        else:
            html = ''
        return dict(properties, text=escape(html))


class Str(DivPaneBase):
    """
    The `Str` pane allows rendering arbitrary text and objects in a panel.

    Unlike Markdown and HTML, a `Str` is interpreted as a raw string without
    applying any markup and is displayed in a fixed-width font by default.

    The pane will render any text, and if given an object will display the
    object’s Python `repr`.

    Reference: https://panel.holoviz.org/reference/panes/Str.html

    :Example:

    >>> Str(
    ...    'This raw string will not be formatted, except for the applied style.',
    ...    style={'font-size': '12pt'}
    ... )
    """

    priority: ClassVar[float | bool | None] = 0

    _bokeh_model: ClassVar[Type[Model]] = _BkHTML

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'object': """JSON.stringify(value).replace(/,/g, ", ").replace(/:/g, ": ")"""
    }

    @classmethod
    def applies(cls, obj: Any) -> bool:
        return True

    def _get_properties(self):
        properties = super()._get_properties()
        if self.object is None or (isinstance(self.object, str) and self.object == ''):
            text = '<pre> </pre>'
        else:
            text = '<pre>'+str(self.object)+'</pre>'
        return dict(properties, text=escape(text))


class Markdown(DivPaneBase):
    """
    The `Markdown` pane allows rendering arbitrary markdown strings in a panel.

    It renders strings containing valid Markdown as well as objects with a
    `_repr_markdown_` method, and may define custom CSS styles.

    Reference: https://panel.holoviz.org/reference/panes/Markdown.html

    :Example:

    >>> Markdown("# This is a header")
    """

    dedent = param.Boolean(default=True, doc="""
        Whether to dedent common whitespace across all lines.""")

    disable_math = param.Boolean(default=False, doc="""
        Whether to disable support for MathJax math rendering for
        strings escaped with $$ delimiters.""")

    extensions = param.List(default=[
        "extra", "smarty", "codehilite"], doc="""
        Markdown extension to apply when transforming markup.""")

    # Priority depends on the data type
    priority: ClassVar[float | bool | None] = None

    _target_transforms: ClassVar[Mapping[str, str | None]] = {'object': None}

    _rerender_params: ClassVar[List[str]] = [
        'object', 'dedent', 'extensions', 'css_classes'
    ]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if hasattr(obj, '_repr_markdown_'):
            return 0.3
        elif isinstance(obj, str):
            return 0.1
        else:
            return False

    def _get_properties(self):
        import markdown
        data = self.object
        if data is None:
            data = ''
        elif not isinstance(data, str):
            data = data._repr_markdown_()
        if self.dedent:
            data = textwrap.dedent(data)
        properties = super()._get_properties()
        properties['style'] = properties.get('style', {})
        css_classes = properties.pop('css_classes', []) + ['markdown']
        html = markdown.markdown(data, extensions=self.extensions,
                                 output_format='html5')
        return dict(properties, text=escape(html), css_classes=css_classes)



class JSON(DivPaneBase):
    """
    The `JSON` pane allows rendering arbitrary JSON strings, dicts and other
    json serializable objects in a panel.

    Reference: https://panel.holoviz.org/reference/panes/JSON.html

    :Example:

    >>> JSON(json_obj, theme='light', height=300, width=500)
    """

    depth = param.Integer(default=1, bounds=(-1, None), doc="""
        Depth to which the JSON tree will be expanded on initialization.""")

    encoder = param.ClassSelector(class_=json.JSONEncoder, is_instance=False, doc="""
        Custom JSONEncoder class used to serialize objects to JSON string.""")

    hover_preview = param.Boolean(default=False, doc="""
        Whether to display a hover preview for collapsed nodes.""")

    margin = param.Parameter(default=(5, 20, 5, 5), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    theme = param.ObjectSelector(default="dark", objects=["light", "dark"], doc="""
        Whether the JSON tree view is expanded by default.""")

    priority: ClassVar[float | bool | None] = None

    _applies_kw: ClassVar[bool] = True

    _bokeh_model: ClassVar[Model] = _BkJSON

    _rename: ClassVar[Mapping[str, str | None]] = {
        "name": None, "object": "text", "encoder": None
    }

    _rerender_params: ClassVar[List[str]] = [
        'object', 'depth', 'encoder', 'hover_preview', 'theme'
    ]

    @classmethod
    def applies(cls, obj: Any, **params) -> float | bool | None:
        if isinstance(obj, (list, dict)):
            try:
                json.dumps(obj, cls=params.get('encoder', cls.encoder))
            except Exception:
                return False
            else:
                return 0.1
        elif isinstance(obj, str):
            return 0
        else:
            return None

    def _get_properties(self):
        properties = super()._get_properties()
        try:
            data = json.loads(self.object)
        except Exception:
            data = self.object
        text = json.dumps(data or {}, cls=self.encoder)
        depth = None if self.depth < 0 else self.depth
        return dict(text=text, theme=self.theme, depth=depth,
                    hover_preview=self.hover_preview, **properties)

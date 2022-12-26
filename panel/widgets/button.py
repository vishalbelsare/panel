"""
Defines the Button and button-like widgets which allow triggering
events or merely toggling between on-off states.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Mapping, Optional,
    Type,
)

import param

from bokeh.events import ButtonClick, MenuItemClick
from bokeh.models import (
    Button as _BkButton, Dropdown as _BkDropdown, Toggle as _BkToggle,
)

from ..links import Callback
from .base import Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..links import JSLinkTarget, Link


BUTTON_TYPES: List[str] = ['default', 'primary', 'success', 'warning', 'danger','light']


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=BUTTON_TYPES, doc="""
        A button theme; should be one of 'default' (white), 'primary'
        (blue), 'success' (green), 'info' (yellow), 'light' (light),
        or 'danger' (red).""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'label'}

    __abstract = True


class _ClickButton(_ButtonBase):

    __abstract = True

    _event: ClassVar[str] = 'button_click'

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events(self._event, model=model, doc=doc, comm=comm)
        return model

    def js_on_click(self, args: Dict[str, Any] = {}, code: str = "") -> Callback:
        """
        Allows defining a JS callback to be triggered when the button
        is clicked.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        code: str
          The Javascript code to execute when the button is clicked.

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        from ..links import Callback
        return Callback(self, code={'event:'+self._event: code}, args=args)

    def jscallback(self, args: Dict[str, Any] = {}, **callbacks: str) -> Callback:
        """
        Allows defining a Javascript (JS) callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        **callbacks: dict
          A mapping between properties on the source model and the code
          to execute when that property changes

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        for k, v in list(callbacks.items()):
            if k == 'clicks':
                k = 'event:'+self._event
            val = self._rename.get(v, v)
            if val is not None:
                callbacks[k] = val
        return Callback(self, code=callbacks, args=args)


class Button(_ClickButton):
    """
    The `Button` widget allows triggering events when the button is
    clicked.

    The Button provides a `value` parameter, which will toggle from
    `False` to `True` while the click event is being processed

    It also provides an additional `clicks` parameter, that can be
    watched to subscribe to click events.

    Reference: https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button

    :Example:

    >>> pn.widgets.Button(name='Click me', button_type='primary')
    """

    clicks = param.Integer(default=0, doc="""
        Number of clicks (can be listened to)""")

    value = param.Event(doc="""
        Toggles from False to True while the event is being processed.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'clicks': None, 'name': 'label', 'value': None}

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'event:button_click': None, 'value': None
    }

    _widget_type: ClassVar[Type[Model]] = _BkButton

    @property
    def _linkable_params(self) -> List[str]:
        return super()._linkable_params + ['value']

    def jslink(
        self, target: JSLinkTarget, code: Optional[Dict[str, str]] = None,
        args: Optional[Dict[str, Any]] = None, bidirectional: bool = False,
        **links: str
    ) -> Link:
        """
        Links properties on the this Button to those on the
        `target` object in Javascript (JS) code.

        Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Arguments
        ----------
        target: panel.viewable.Viewable | bokeh.model.Model | holoviews.core.dimension.Dimensioned
          The target to link the value(s) to.
        code: dict
          Custom code which will be executed when the widget value
          changes.
        args: dict
          A mapping of objects to make available to the JS callback
        bidirectional: boolean
          Whether to link source and target bi-directionally. Default is `False`.
        **links: dict[str,str]
          A mapping between properties on the source model and the
          target model property to link it to.

        Returns
        -------
        Link
          The Link can be used unlink the widget and the target model.
        """
        links = {'event:'+self._event if p == 'value' else p: v for p, v in links.items()}
        return super().jslink(target, code, args, bidirectional, **links)

    def _process_event(self, event: param.parameterized.Event) -> None:
        self.param.trigger('value')
        self.clicks += 1

    def on_click(
        self, callback: Callable[[param.parameterized.Event], None]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when the `Button` is clicked.

        The callback is given an `Event` argument declaring the number of clicks

        Arguments
        ---------
        callback: (Callable[[param.parameterized.Event], None])
            The function to run on click events. Must accept a positional `Event` argument

        Returns
        -------
        watcher: param.Parameterized.Watcher
          A `Watcher` that executes the callback when the button is clicked.
        """
        return self.param.watch(callback, 'clicks', onlychanged=False)


class Toggle(_ButtonBase):
    """The `Toggle` widget allows toggling a single condition between `True`/`False` states.

    This widget is interchangeable with the `Checkbox` widget.

    Reference: https://panel.holoviz.org/reference/widgets/Toggle.html

    :Example:

    >>> Toggle(name='Toggle', button_type='success')
    """

    value = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'value': 'active', 'name': 'label'}

    _supports_embed: ClassVar[bool] = True

    _widget_type: ClassVar[Type[Model]] = _BkToggle

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', 'cb_obj.active')


class MenuButton(_ClickButton):
    """
    The `MenuButton` widget allows specifying a list of menu items to
    select from triggering events when the button is clicked.

    Unlike other widgets, it does not have a `value`
    parameter. Instead it has a `clicked` parameter that can be
    watched to trigger events and which reports the last clicked menu
    item.

    Reference: https://panel.holoviz.org/reference/widgets/MenuButton.html

    :Example:

    >>> menu_items = [('Option A', 'a'), ('Option B', 'b'), None, ('Option C', 'c')]
    >>> MenuButton(name='Dropdown', items=menu_items, button_type='primary')
    """

    clicked = param.String(default=None, doc="""
      Last menu item that was clicked.""")

    items = param.List(default=[], doc="""
      Menu items in the dropdown. Allows strings, tuples of the form
      (title, value) or Nones to separate groups of items.""")

    split = param.Boolean(default=False, doc="""
      Whether to add separate dropdown area to button.""")

    _event: ClassVar[str] = 'menu_item_click'

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'label', 'items': 'menu', 'clicked': None}

    _widget_type: ClassVar[Type[Model]] = _BkDropdown

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('button_click', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event):
        if isinstance(event, MenuItemClick):
            item = event.item
        elif isinstance(event, ButtonClick):
            item = self.name
        self.clicked = item

    def on_click(
        self, callback: Callable[[param.parameterized.Event], None]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when the button is clicked.

        The callback is given an `Event` argument declaring the number of clicks

        Arguments
        ---------
        callback: (Callable[[param.parameterized.Event], None])
            The function to run on click events. Must accept a positional `Event` argument

        Returns
        -------
        watcher: param.Parameterized.Watcher
          A `Watcher` that executes the callback when the MenuButton is clicked.
        """
        return self.param.watch(callback, 'clicked', onlychanged=False)

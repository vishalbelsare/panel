from __future__ import annotations

import json
import sys

from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import PaneBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class ECharts(PaneBase):
    """
    ECharts panes allow rendering echarts.js dictionaries and pyecharts plots.

    Reference: https://panel.holoviz.org/reference/panes/ECharts.html

    :Example:

    >>> pn.extension('echarts')
    >>> ECharts(some_echart_dict_or_pyecharts_object, height=480, width=640)
    """

    object = param.Parameter(default=None, doc="""
        The Echarts object being wrapped. Can be an Echarts dictionary or a pyecharts chart""")

    renderer = param.ObjectSelector(default="canvas", objects=["canvas", "svg"], doc="""
       Whether to render as HTML canvas or SVG""")

    theme = param.ObjectSelector(default="default", objects=["default", "light", "dark"], doc="""
       Theme to apply to plots.""")

    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {"object": "data"}

    _rerender_params: ClassVar[List[str]] = []

    _updates: ClassVar[bool] = True

    @classmethod
    def applies(cls, obj: Any, **params) -> float | bool | None:
        if isinstance(obj, dict):
            return 0
        elif cls.is_pyecharts(obj):
            return 0.8
        return None

    @classmethod
    def is_pyecharts(cls, obj):
        if 'pyecharts' in sys.modules:
            import pyecharts
            return isinstance(obj, pyecharts.charts.chart.Chart)
        return False

    @classmethod
    def _get_dimensions(cls, props):
        if json is None:
            return
        responsive = props.get('data', {}).get('responsive')
        if responsive:
            props['sizing_mode'] = 'stretch_both'
        else:
            props['sizing_mode'] = 'fixed'

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        ECharts = lazy_load('panel.models.echarts', 'ECharts', isinstance(comm, JupyterComm), root)
        props = self._get_echart_dict(self.object)
        props.update(self._process_param_change(self._init_params()))
        self._get_dimensions(props)
        model = ECharts(**props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'data' in msg:
            msg.update(self._get_echart_dict(msg['data']))
        return msg

    def _get_echart_dict(self, object):
        if isinstance(object, dict):
            return {'data': dict(object)}
        elif object is not None:
            w, h = object.width, object.height
            params = {'data': json.loads(object.dump_options())}
            if not self.height and h:
                params['height'] = int(h.replace('px', ''))
            if not self.width and w:
                params['width'] = int(w.replace('px', ''))
            return params
        return {}

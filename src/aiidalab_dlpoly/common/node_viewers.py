"""Defines a custom AiiDA node visualiser."""

import ipywidgets as ipw
import traitlets as tl
from aiida.orm import Node, ProcessNode
from aiidalab_widgets_base.loaders import LoadingWidget
from aiidalab_widgets_base.viewers import AIIDA_VIEWER_MAPPING
from alc_aiidalab_widgets.viewers import ALC_AIIDA_VIEWER_MAPPING
from IPython.display import clear_output, display


class CustomAiidaNodeViewWidget(ipw.VBox):
    """
    Custom viewer based on a specific AiiDA node type.

    An extension of the aiidalab_widgets_base.viewers.AiidaNodeViewWidget which
    prioritises the ALC-developed node viewers (which handle the DL_POLY output
    node types such as trajectories, statistics arrays and structure files)
    before falling back to the default AiiDAlab viewers.
    """

    node = tl.Instance(Node, allow_none=True)

    def __init__(self, **kwargs):
        """CustomAiidaNodeViewWidget Constructor."""
        self._output = ipw.Output()
        self.node_views = {}
        self.node_view_loading_message = LoadingWidget("Loading Node View")
        super().__init__(**kwargs)
        self.add_class("aiida-node-view-widget")

    @tl.observe("node")
    def _observe_node(self, change):
        if not ((node := change["new"]) and node != change["old"]):
            return
        if node.uuid in self.node_views:
            self.children = [self.node_views[node.uuid]]
            return
        self.children = [self.node_view_loading_message]
        node_view = self._viewer(node)
        if isinstance(node_view, ipw.DOMWidget):
            self.node_views[node.uuid] = node_view
            self.children = [node_view]
        else:
            with self._output:
                clear_output()
                if change["new"]:
                    display(node_view)
            self.children = [self._output]

    def _viewer(self, node: Node, **kwargs):
        """Create a viewer based on the type of Node being visualised."""
        # First look for ALC developed node viewers.
        _viewer = ALC_AIIDA_VIEWER_MAPPING.get(node.node_type)
        if not _viewer:
            # Fall back to default AiiDAlab developed node viewers.
            _viewer = AIIDA_VIEWER_MAPPING.get(node.node_type)
        if isinstance(node, ProcessNode):
            # Allow to register specific viewers based on node.process_type.
            _viewer = ALC_AIIDA_VIEWER_MAPPING.get(node.process_type, _viewer)  # type: ignore
            if not _viewer:
                _viewer = AIIDA_VIEWER_MAPPING.get(node.process_type, _viewer)

        if _viewer:
            return _viewer(node, **kwargs)
        # No viewer registered for this type, return node itself.
        return node

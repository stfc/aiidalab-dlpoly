"""Widget for selecting a DL_POLY force field (FIELD) file from various sources."""

from __future__ import annotations

import ipywidgets as ipw
import traitlets as tl
from aiida.orm import SinglefileData
from alc_aiidalab_widgets.widgets import (
    AiiDADatabaseQueryWidget,
    FileUploadWidget,
)


class FieldSelectionWidget(ipw.VBox, tl.HasTraits):
    """Widget for selecting a force field file by upload or AiiDA database search.

    Exposes the selected file on the ``force_field`` trait as a
    ``SinglefileData`` node, regardless of whether it was uploaded or queried
    from the AiiDA database.
    """

    force_field = tl.Instance(SinglefileData, allow_none=True)

    def __init__(self, **kwargs):
        """FieldSelectionWidget constructor."""
        super().__init__(**kwargs)

        # Upload file.
        self.file_uploader = FileUploadWidget(description="Force field file: ")

        # AiiDA database search. Any ``SinglefileData`` node is a candidate; the
        # widget cannot tell a FIELD file from another single file on its own.
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData],
        )

        self.tabs = ipw.Tab()
        self.tabs.children = [
            self.file_uploader,
            self.database_widget,
        ]
        for i, title in enumerate(["Upload File", "AiiDA Database"]):
            self.tabs.set_title(i, title)

        self.children = [self.tabs]

        # An uploaded file propagates straight to ``force_field``.
        ipw.dlink((self.file_uploader, "file"), (self, "force_field"))
        # A database selection is applied only when it is a single file.
        self.database_widget.observe(self._on_database_search, "data_object")

        return

    def _on_database_search(self, change: dict) -> None:
        """Adopt a ``SinglefileData`` selected from the AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], SinglefileData):
            self.force_field = change["new"]
        return

    def disable(self, val: bool = True) -> None:
        """Disable the widget and all children."""
        for child in self.tabs.children:
            try:
                child.disable(val)
            except AttributeError:
                pass  # Not all tab widgets expose a disable() method.
        return

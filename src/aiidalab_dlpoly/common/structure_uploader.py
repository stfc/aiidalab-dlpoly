"""Widget for selecting an input structure from various sources."""

from __future__ import annotations

import ipywidgets as ipw
import traitlets as tl
from aiida.orm import SinglefileData, StructureData, TrajectoryData
from alc_aiidalab_widgets.widgets import (
    AiiDADatabaseQueryWidget,
    FileUploadWidget,
    StructureViewWidget,
)
from ase import Atoms


class StructureSelectionWidget(ipw.VBox, tl.HasTraits):
    """Widget for selecting an input structure from various sources."""

    structure_data = tl.Instance(StructureData, allow_none=True)
    structure_file = tl.Instance(SinglefileData, allow_none=True)
    trajectory_data = tl.Instance(TrajectoryData, allow_none=True)

    def __init__(self, **kwargs):
        """StructureSelectionWidget constructor."""
        super().__init__(**kwargs)

        # Upload file
        self.file_input_widget = ipw.VBox()
        self.file_uploader = FileUploadWidget(description="CONFIG file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]

        # AiiDA database
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData, StructureData],
        )

        self.tabs = ipw.Tab()
        self.tabs.children = [
            self.file_input_widget,
            self.database_widget,
        ]
        for i, title in enumerate(["Upload File", "AiiDA Database"]):
            self.tabs.set_title(i, title)

        self.viewer = ipw.HTML("<p>No structure found...</p>")

        self.children = [self.tabs, ipw.HTML("<h2>Viewer:</h2>"), self.viewer]

        self.file_uploader.observe(self._on_file_upload, "file")
        self.database_widget.observe(self._on_database_search, "data_object")

        ipw.dlink((self.file_uploader, "file"), (self, "structure_file"))

        return

    def _on_file_upload(self, change: dict) -> None:
        """When file upload button is pressed."""
        if change["new"] != change["old"]:
            self.viewer = StructureViewWidget()
            self.viewer.assign_structure_from_file(
                self.file_uploader.filename(),
                self.file_uploader.get_file_contents().getvalue(),
            )
            self._update_children()
        return

    def _on_database_search(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], SinglefileData):
            if self.structure_data:
                self.structure_data = None
            self.structure_file = change["new"]
            self.viewer = StructureViewWidget(change["new"])
            self._update_children()
        elif isinstance(change["new"], StructureData):
            if self.structure_file:
                self.structure_file = None
            self.structure_data = change["new"]
            self._create_viewer(change["new"].get_ase())
        else:
            self._create_viewer(None)
        return

    def _create_viewer(self, structure: Atoms | None) -> None:
        """Create a viewer widget with the loaded ase.Atoms structure object."""
        if structure:
            self.viewer = StructureViewWidget()
            self.viewer.assign_structure_from_ase(structure)
        else:
            self.viewer = ipw.HTML("<p>Could not visualise structure ...</p>")
        self._update_children()
        return

    def _update_children(self) -> None:
        self.children = [
            self.tabs,
            self.viewer,
        ]
        return

    def disable(self, val: bool = True) -> None:
        """Disable the widget and all children."""
        for child in self.tabs.children:
            try:
                child.disable(val)
            except AttributeError:
                pass  # Not all tab widgets expose a disable() method.
        return

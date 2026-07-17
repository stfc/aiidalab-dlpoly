"""Defines the model and view components for the structure setup stage."""

import ipywidgets as ipw
from aiidalab_widgets_base import WizardAppWidgetStep

from aiidalab_dlpoly.common.structure_uploader import StructureSelectionWidget
from aiidalab_dlpoly.models.structure import StructureInputModel


class StructureWizardStep(ipw.VBox, WizardAppWidgetStep):
    """
    Wizard for structure selection and manipulation.

    A step in a wizard based process widget which allows a user to
    configure a chemical structure to be used in their workflow.
    """

    def __init__(self, model: StructureInputModel, **kwargs):
        """
        StructureWizardStep constructor.

        Parameters
        ----------
        model : StructureInputModel
            A model controlling the data required for the structure step.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.rendered = False
        self.model = model
        self.state = self.State.READY

        self.info = ipw.HTML(
            """
                <p>
                    Load in a structure to start the workflow.
                </p>
            """
        )

        self.structure_uploader = StructureSelectionWidget()

        ipw.dlink(
            (self.structure_uploader, "structure_file"),
            (self.model, "structure_file"),
        )
        ipw.dlink(
            (self.structure_uploader, "structure_data"),
            (self.model, "structure"),
        )

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return

        self.submit_btn = ipw.Button(
            description="Submit Structure",
            disabled=False,
            button_style="success",
            tooltip="Submit the structure to the workflow",
            icon="check",
            layout={"margin": "auto", "width": "60%"},
        )
        self.submit_btn.on_click(self.submit_structure)

        self._update_children()
        self.rendered = True
        return

    def _update_children(self) -> None:
        self.children = [
            self.info,
            self.structure_uploader,
            self.submit_btn,
        ]
        return

    def submit_structure(self, _):
        """Submit the structure step."""
        if self.model.has_file or self.model.has_structure:
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            self.structure_uploader.disable(True)
            self.model.submitted = True
            self.state = self.State.SUCCESS
        else:
            self.model.submitted = False
        return

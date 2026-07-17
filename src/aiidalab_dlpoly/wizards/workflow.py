"""Defines the model and view components for the workflow setup stage."""

import ipywidgets as ipw
from aiidalab_widgets_base import WizardAppWidgetStep
from alc_aiidalab_widgets.widgets import FileUploadWidget

from aiidalab_dlpoly.models.workflow import WorkflowInputModel


class WorkflowWizardStep(ipw.VBox, WizardAppWidgetStep):
    """
    Wizard step for configuring the DL_POLY workflow.

    Provides a required force field file upload and a control input which can
    either be a pre-formatted DL_POLY ``CONTROL`` file or, when the detailed
    control checkbox is ticked, a set of key control parameters.
    """

    # Detailed control fields: (model trait, label, unit, integer?).
    CONTROL_FIELDS = (
        ("temperature", "Temperature", "K", False),
        ("timestep", "Timestep", "ps", False),
        ("time_run", "Run time", "steps", True),
        ("time_equilibration", "Equilibration time", "steps", True),
        ("cutoff", "Cutoff", "ang", False),
        ("padding", "Padding", "ang", False),
        ("stats_frequency", "Stats frequency", "steps", True),
    )

    def __init__(self, model: WorkflowInputModel, **kwargs):
        """
        WorkflowWizardStep constructor.

        Parameters
        ----------
        model : WorkflowInputModel
            A model controlling the data required for the workflow step.
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
                    Provide the force field and simulation control inputs for
                    the DL_POLY calculation.
                </p>
            """
        )

        # Force field file upload (required).
        self.field_uploader = FileUploadWidget(description="Force field file: ")
        ipw.dlink((self.field_uploader, "file"), (self.model, "force_field"))

        # Control file upload (used when detailed control is disabled).
        self.control_uploader = FileUploadWidget(description="Control file: ")
        ipw.dlink((self.control_uploader, "file"), (self.model, "control_file"))

        # Toggle between a control file and the detailed parameter inputs.
        self.detailed_checkbox = ipw.Checkbox(
            value=self.model.use_detailed_control,
            description="Specify control parameters manually",
            indent=False,
        )
        ipw.link(
            (self.detailed_checkbox, "value"),
            (self.model, "use_detailed_control"),
        )
        self.detailed_checkbox.observe(self._on_toggle_detailed, "value")

        # Detailed control parameter inputs.
        self.control_inputs = self._build_control_inputs()

    def _build_control_inputs(self) -> dict:
        """Create the detailed control parameter widgets, dlinked to the model."""
        widgets = {}
        for trait, label, unit, is_int in self.CONTROL_FIELDS:
            widget_cls = ipw.IntText if is_int else ipw.FloatText
            # Seed the widget from the model default before linking so the
            # bidirectional link does not overwrite the model with the widget's
            # zero default.
            widget = widget_cls(
                value=getattr(self.model, trait),
                description=f"{label} ({unit})",
                style={"description_width": "180px"},
                layout={"width": "320px"},
            )
            ipw.link((widget, "value"), (self.model, trait))
            widgets[trait] = widget
        return widgets

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return

        self.field_section = ipw.VBox(
            children=[
                ipw.HTML("<b>Force field</b> (required)"),
                self.field_uploader,
            ]
        )

        self.control_file_section = ipw.VBox(
            children=[self.control_uploader],
        )

        self.detailed_section = ipw.VBox(
            children=list(self.control_inputs.values()),
        )

        self.control_container = ipw.VBox()

        self.submit_btn = ipw.Button(
            description="Submit Workflow",
            disabled=False,
            button_style="success",
            tooltip="Submit the workflow configuration",
            icon="check",
            layout={"margin": "auto", "width": "60%"},
        )
        self.submit_btn.on_click(self.submit_workflow)

        self._update_control_container()
        self._update_children()
        self.rendered = True
        return

    def _on_toggle_detailed(self, _) -> None:
        """Swap the control input section when the checkbox is toggled."""
        if self.rendered:
            self._update_control_container()
        return

    def _update_control_container(self) -> None:
        """Show either the detailed parameters or the control file uploader."""
        if self.model.use_detailed_control:
            self.control_container.children = [
                ipw.HTML("<b>Control parameters</b>"),
                self.detailed_section,
            ]
        else:
            self.control_container.children = [
                ipw.HTML("<b>Control file</b> (required)"),
                self.control_file_section,
            ]
        return

    def _update_children(self) -> None:
        self.children = [
            self.info,
            self.field_section,
            self.detailed_checkbox,
            self.control_container,
            self.submit_btn,
        ]
        return

    def submit_workflow(self, _):
        """Submit the workflow step."""
        if self.model.is_valid:
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            self.field_uploader.disable(True)
            self.control_uploader.disable(True)
            self.model.submitted = True
            self.state = self.State.SUCCESS
        else:
            self.model.submitted = False
        return

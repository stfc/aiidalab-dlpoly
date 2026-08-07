"""Tests for the wizard step widgets and the overall wizard container."""

from aiidalab_widgets_base import WizardAppWidgetStep

from aiidalab_dlpoly.models.resources import ComputationalResourcesModel
from aiidalab_dlpoly.models.results import ResultsModel
from aiidalab_dlpoly.models.structure import StructureInputModel
from aiidalab_dlpoly.models.workflow import WorkflowInputModel
from aiidalab_dlpoly.process import MainAppModel
from aiidalab_dlpoly.wizards.main_app import MainAppWizardWidget
from aiidalab_dlpoly.wizards.resources import (
    ComputationalResourcesWizardStep,
    ResourceSetupBox,
)
from aiidalab_dlpoly.wizards.results import ResultsWizardStep
from aiidalab_dlpoly.wizards.structure import StructureWizardStep
from aiidalab_dlpoly.wizards.workflow import WorkflowWizardStep


class TestStructureWizardStep:
    """Tests for the structure selection wizard step."""

    def test_initial_state(self):
        """A new step starts unrendered and in the READY state."""
        step = StructureWizardStep(StructureInputModel())
        assert step.rendered is False
        assert step.state == step.State.READY
        assert step.children == ()

    def test_render_populates_children(self):
        """Rendering builds the info, uploader and submit button."""
        step = StructureWizardStep(StructureInputModel())
        step.render()
        assert step.rendered is True
        assert len(step.children) == 3
        assert step.submit_btn.description == "Submit Structure"

    def test_render_is_idempotent(self):
        """Calling render twice does not rebuild the children."""
        step = StructureWizardStep(StructureInputModel())
        step.render()
        first = step.submit_btn
        step.render()
        assert step.submit_btn is first

    def test_uploader_dlinks_structure_to_model(self, water_structure):
        """The uploader selection propagates to the model via dlink."""
        model = StructureInputModel()
        step = StructureWizardStep(model)
        step.structure_uploader.structure_data = water_structure
        assert model.structure is water_structure

    def test_uploader_dlinks_file_to_model(self, xyz_singlefile):
        """The uploader file selection propagates to the model via dlink."""
        model = StructureInputModel()
        step = StructureWizardStep(model)
        step.structure_uploader.structure_file = xyz_singlefile
        assert model.structure_file is xyz_singlefile

    def test_submit_with_structure(self, water_structure):
        """Submitting with a structure marks the step successful."""
        model = StructureInputModel()
        step = StructureWizardStep(model)
        step.render()
        # Select a structure as a user would; the dlink propagates it.
        step.structure_uploader.structure_data = water_structure

        step.submit_structure(None)

        assert model.submitted is True
        assert step.state == step.State.SUCCESS
        assert step.submit_btn.disabled is True
        assert step.submit_btn.description == "Submitted"

    def test_submit_with_file(self, xyz_singlefile):
        """Submitting with a file (no structure) also succeeds."""
        model = StructureInputModel()
        step = StructureWizardStep(model)
        step.render()
        # Select a file as a user would; the dlink propagates it.
        step.structure_uploader.structure_file = xyz_singlefile

        step.submit_structure(None)

        assert model.submitted is True
        assert step.state == step.State.SUCCESS

    def test_submit_without_structure(self):
        """Submitting with nothing selected does not advance the step."""
        model = StructureInputModel()
        step = StructureWizardStep(model)
        step.render()

        step.submit_structure(None)

        assert model.submitted is False
        assert step.state == step.State.READY
        assert step.submit_btn.disabled is False


class TestWorkflowWizardStep:
    """Tests for the workflow configuration wizard step."""

    def test_initial_state(self):
        """A new step starts unrendered and in the READY state."""
        step = WorkflowWizardStep(WorkflowInputModel())
        assert step.rendered is False
        assert step.state == step.State.READY
        assert step.children == ()

    def test_render_populates_children(self):
        """Rendering builds the info, field, checkbox, control and submit."""
        step = WorkflowWizardStep(WorkflowInputModel())
        step.render()
        assert step.rendered is True
        assert len(step.children) == 5
        assert step.submit_btn.description == "Submit Workflow"

    def test_render_is_idempotent(self):
        """Calling render twice does not rebuild the submit button."""
        step = WorkflowWizardStep(WorkflowInputModel())
        step.render()
        first = step.submit_btn
        step.render()
        assert step.submit_btn is first

    def test_field_uploader_dlinks_to_model(self, field_singlefile):
        """The force field upload propagates to the model via dlink."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.field_uploader.file = field_singlefile
        assert model.force_field is field_singlefile

    def test_control_uploader_dlinks_to_model(self, control_singlefile):
        """The control file upload propagates to the model via dlink."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.control_uploader.file = control_singlefile
        assert model.control_file is control_singlefile

    def test_control_inputs_dlink_to_model(self):
        """Editing a detailed control widget updates the model."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.control_inputs["temperature"].value = 85.0
        assert model.temperature == 85.0

    def test_control_inputs_seeded_from_model_defaults(self):
        """The detailed control widgets show the model defaults."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        assert step.control_inputs["temperature"].value == 300.0
        assert step.control_inputs["time_run"].value == 10000

    def test_default_shows_control_file_section(self):
        """By default the control file uploader is shown."""
        step = WorkflowWizardStep(WorkflowInputModel())
        step.render()
        assert step.control_file_section in step.control_container.children

    def test_checkbox_toggles_detailed_section(self):
        """Ticking the checkbox swaps to the detailed parameter section."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.detailed_checkbox.value = True

        assert model.use_detailed_control is True
        assert step.detailed_section in step.control_container.children
        assert step.control_file_section not in step.control_container.children

    def test_submit_requires_force_field(self, control_singlefile):
        """Submission fails without a force field."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.control_uploader.file = control_singlefile

        step.submit_workflow(None)

        assert model.submitted is False
        assert step.state == step.State.READY

    def test_submit_with_field_and_control_file(
        self, field_singlefile, control_singlefile
    ):
        """Submission succeeds with a force field and a control file."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.field_uploader.file = field_singlefile
        step.control_uploader.file = control_singlefile

        step.submit_workflow(None)

        assert model.submitted is True
        assert step.state == step.State.SUCCESS
        assert step.submit_btn.disabled is True

    def test_submit_with_field_and_detailed(self, field_singlefile):
        """Submission succeeds with a force field and detailed control."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.field_uploader.file = field_singlefile
        step.detailed_checkbox.value = True

        step.submit_workflow(None)

        assert model.submitted is True
        assert step.state == step.State.SUCCESS

    def test_submit_detailed_without_control_file_fails_without_field(self):
        """Detailed control still requires a force field."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.detailed_checkbox.value = True

        step.submit_workflow(None)

        assert model.submitted is False

    def test_ensemble_dropdown_dlinks_to_model(self):
        """Selecting an ensemble propagates to the model."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.ensemble_inputs["ensemble"].value = "NPT"
        assert model.ensemble == "NPT"

    def test_default_ensemble_hides_method_dpd_and_coupling(self):
        """The NVE default hides the method, DPD order and coupling widgets."""
        step = WorkflowWizardStep(WorkflowInputModel())
        step.render()
        assert step.ensemble_inputs["ensemble_method"].layout.display == "none"
        assert step.ensemble_inputs["ensemble_dpd_order"].layout.display == "none"
        coupling = step.ensemble_inputs["ensemble_thermostat_coupling"]
        assert coupling.layout.display == "none"

    def test_thermostat_coupling_dlinks_to_model(self):
        """Editing the thermostat coupling widget updates the model."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()
        step.ensemble_inputs["ensemble_thermostat_coupling"].value = 0.25
        assert model.ensemble_thermostat_coupling == 0.25

    def test_selecting_nvt_shows_coupling(self):
        """Selecting NVT reveals the thermostat coupling and hides DPD order."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"

        assert (
            step.ensemble_inputs["ensemble_thermostat_coupling"].layout.display == ""
        )
        assert step.ensemble_inputs["ensemble_dpd_order"].layout.display == "none"

    def test_dpd_hides_coupling_shows_order(self):
        """The dpd method swaps the coupling widget for the DPD order."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"
        step.ensemble_inputs["ensemble_method"].value = "dpd"

        coupling = step.ensemble_inputs["ensemble_thermostat_coupling"]
        assert coupling.layout.display == "none"
        assert step.ensemble_inputs["ensemble_dpd_order"].layout.display == ""

    def test_selecting_nvt_populates_and_shows_method(self):
        """Selecting NVT reveals the method dropdown and its options."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"

        method_widget = step.ensemble_inputs["ensemble_method"]
        assert method_widget.layout.display == ""
        assert method_widget.options == model.ENSEMBLE_METHODS["NVT"]
        # The model is seeded with the first valid method.
        assert model.ensemble_method == "Evans"

    def test_selecting_dpd_shows_order(self):
        """Selecting the dpd method reveals the DPD order dropdown."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"
        step.ensemble_inputs["ensemble_method"].value = "dpd"

        assert model.ensemble_method == "dpd"
        assert step.ensemble_inputs["ensemble_dpd_order"].layout.display == ""

    def test_switching_ensemble_resets_invalid_method(self):
        """Switching to an ensemble without the current method reselects one."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"
        step.ensemble_inputs["ensemble_method"].value = "Evans"
        # Evans is not valid for NPT, so the method should reset.
        step.ensemble_inputs["ensemble"].value = "NPT"

        assert model.ensemble_method in model.ENSEMBLE_METHODS["NPT"]
        assert step.ensemble_inputs["ensemble_dpd_order"].layout.display == "none"

    def test_switching_to_nve_clears_method(self):
        """Switching back to NVE clears and hides the method dropdown."""
        model = WorkflowInputModel()
        step = WorkflowWizardStep(model)
        step.render()

        step.ensemble_inputs["ensemble"].value = "NVT"
        step.ensemble_inputs["ensemble"].value = "NVE"

        assert model.ensemble_method == ""
        assert step.ensemble_inputs["ensemble_method"].layout.display == "none"


class TestComputationalResourcesWizardStep:
    """Tests for the computational resources wizard step."""

    def test_construction(self):
        """A new step attaches the model and builds its children."""
        model = ComputationalResourcesModel()
        step = ComputationalResourcesWizardStep(model)
        assert step.model is model
        assert step.rendered is False
        assert len(step.children) == 4

    def test_render_enables_submit_when_plugin_installed(self):
        """Rendering enables the submit button when the plugin is available."""
        step = ComputationalResourcesWizardStep(ComputationalResourcesModel())
        step.render()
        assert step.rendered is True
        assert step.submit_btn.disabled is False

    def test_render_is_idempotent(self):
        """Calling render twice is a no-op after the first call."""
        step = ComputationalResourcesWizardStep(ComputationalResourcesModel())
        step.render()
        step.render()
        assert step.rendered is True

    def test_render_warns_when_plugin_missing(self, monkeypatch):
        """A missing plugin disables submit and shows a warning."""
        import aiidalab_dlpoly.wizards.resources as res

        monkeypatch.setattr(res, "test_aiida_dlpoly_import", lambda: False)
        step = res.ComputationalResourcesWizardStep(ComputationalResourcesModel())
        step.render()
        assert step.submit_btn.disabled is True
        assert "not installed" in step.dlpoly_warning.value

    def test_code_dropdown_populated(self):
        """The code dropdown is populated with the registered DL_POLY code."""
        model = ComputationalResourcesModel()
        ComputationalResourcesWizardStep(model)
        assert model.code_label == "dlpoly@localhost"

    def test_submit_valid(self):
        """Submitting with a selected code marks the step submitted."""
        model = ComputationalResourcesModel()
        step = ComputationalResourcesWizardStep(model)
        step.render()

        step._submit()

        assert model.submitted is True
        assert step.submit_btn.disabled is True
        assert step.submit_btn.description == "Submitted"

    def test_submit_invalid(self, monkeypatch):
        """Submission does nothing when the model is invalid."""
        model = ComputationalResourcesModel()
        step = ComputationalResourcesWizardStep(model)
        step.render()
        monkeypatch.setattr(model, "validate", lambda: False)

        step._submit()

        assert model.submitted is False
        assert step.submit_btn.description == "Submit"


class TestResourceSetupBox:
    """Tests for the resource setup input box."""

    def test_inputs_link_to_model(self):
        """The ncpus, label and description inputs propagate to the model."""
        model = ComputationalResourcesModel()
        box = ResourceSetupBox(model=model)

        box.ncpus_input.value = 16
        box.label.value = "my run"
        box.description.value = "my description"

        assert model.ncpus == 16
        assert model.process_label == "my run"
        assert model.process_description == "my description"

    def test_empty_dropdown_maps_to_empty_code_label(self):
        """An empty code dropdown (value None) maps to an empty string.

        Regression test: linking a ``None`` dropdown value directly to the
        ``Unicode`` code_label trait previously raised a TraitError.
        """
        model = ComputationalResourcesModel()
        box = ResourceSetupBox(model=model)

        box.code.options = []

        assert box.code.value is None
        assert model.code_label == ""


class TestResultsWizardStep:
    """Tests for the results wizard step."""

    def test_construction(self):
        """A new step attaches the model and starts unrendered."""
        model = ResultsModel()
        step = ResultsWizardStep(model)
        assert step.model is model
        assert step.rendered is False

    def test_render_blocked_shows_message(self):
        """A blocked model renders a placeholder message and stays unrendered."""
        step = ResultsWizardStep(ResultsModel())
        step.render()
        assert len(step.children) == 1
        # Deliberately not marked rendered so it re-renders once unblocked.
        assert step.rendered is False

    def test_render_unblocked_builds_tree_and_view(self):
        """An unblocked model renders the node tree and viewer."""
        model = ResultsModel()
        model.blocked = False
        step = ResultsWizardStep(model)
        step.render()
        assert step.rendered is True
        assert len(step.children) == 4
        assert hasattr(step, "node_tree")
        assert hasattr(step, "node_view")

    def test_process_uuid_dlinks_to_tree(self, finished_process_node):
        """The model process uuid is dlinked to the node tree value."""
        model = ResultsModel()
        model.blocked = False
        step = ResultsWizardStep(model)
        step.render()
        model.process_uuid = finished_process_node.uuid
        assert step.node_tree.value == finished_process_node.uuid

    def test_refresh_info(self):
        """Refreshing an unblocked step updates the node tree without error."""
        model = ResultsModel()
        model.blocked = False
        step = ResultsWizardStep(model)
        step.render()
        step._refresh_info(None)  # should not raise

    def test_render_is_idempotent(self):
        """Rendering an unblocked step twice does not rebuild the tree."""
        model = ResultsModel()
        model.blocked = False
        step = ResultsWizardStep(model)
        step.render()
        tree = step.node_tree
        step.render()
        assert step.node_tree is tree


class TestMainAppWizardWidget:
    """Tests for the top-level wizard container."""

    def test_construction_registers_steps(self):
        """The wizard is built from all four steps."""
        wizard = MainAppWizardWidget(MainAppModel())
        assert isinstance(wizard.structureStep, StructureWizardStep)
        assert isinstance(wizard.workflowStep, WorkflowWizardStep)
        assert isinstance(wizard.compResourceStep, ComputationalResourcesWizardStep)
        assert isinstance(wizard.results_step, ResultsWizardStep)
        assert isinstance(wizard.workflowStep, WizardAppWidgetStep)

    def test_steps_registered(self):
        """All wizard steps are registered with the expected labels."""
        wizard = MainAppWizardWidget(MainAppModel())
        labels = [label for label, _ in wizard.steps]
        assert labels == [
            "Select Structure",
            "Configure Workflow",
            "Configure Computational Resources",
            "Results",
        ]

    def test_results_step_starts_disabled(self):
        """The results step is disabled until a process is submitted."""
        wizard = MainAppWizardWidget(MainAppModel())
        assert wizard.results_step.disabled is True

    def test_on_step_change_renders_selected_step(self):
        """Selecting a step triggers its render()."""
        wizard = MainAppWizardWidget(MainAppModel())
        assert wizard.compResourceStep.rendered is False

        wizard.on_step_change({"new": 2})

        assert wizard.compResourceStep.rendered is True

    def test_on_step_change_ignores_none(self):
        """A None selection is a no-op."""
        wizard = MainAppWizardWidget(MainAppModel())
        wizard.on_step_change({"new": None})
        assert wizard.structureStep.rendered is False

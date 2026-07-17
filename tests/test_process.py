"""Tests for the top-level MainAppModel and DLPOLYProcess."""

from types import SimpleNamespace

from aiida.orm import Dict

import aiidalab_dlpoly.process as process_module
from aiidalab_dlpoly.models.resources import ComputationalResourcesModel
from aiidalab_dlpoly.models.results import ResultsModel
from aiidalab_dlpoly.models.structure import StructureInputModel
from aiidalab_dlpoly.models.workflow import WorkflowInputModel
from aiidalab_dlpoly.process import DLPOLYProcess, MainAppModel


def _fake_node():
    """Return a stand-in process node with settable label/description."""
    return SimpleNamespace(uuid="uuid-1234", label=None, description=None)


def _capture_submit(monkeypatch):
    """Patch process submission to capture the builder instead of launching."""
    captured = {}

    def fake_submit(builder):
        captured["builder"] = builder
        return _fake_node()

    monkeypatch.setattr(process_module, "submit", fake_submit)
    return captured


def _ready_model(dlpoly_code, *, detailed=True, control_file=None, use_file=False):
    """Build a fully-populated, submittable MainAppModel."""
    from aiida.orm import SinglefileData, StructureData
    from ase.build import molecule

    model = MainAppModel()
    if use_file:
        model.structure_model.structure_file = SinglefileData.from_string(
            "CONFIG", filename="CONFIG"
        )
    else:
        model.structure_model.structure = StructureData(ase=molecule("H2O"))
    model.workflow_model.force_field = SinglefileData.from_string(
        "FIELD", filename="FIELD"
    )
    model.workflow_model.use_detailed_control = detailed
    if control_file is not None:
        model.workflow_model.control_file = control_file
    model.resource_model.code_label = dlpoly_code.full_label
    model.resource_model.ncpus = 8
    model.resource_model.process_label = "test run"
    model.resource_model.process_description = "a test description"
    return model


class TestMainAppModel:
    """Tests for the top-level application model."""

    def test_construction(self):
        """The main model wires up its per-step sub-models."""
        model = MainAppModel()
        assert isinstance(model.structure_model, StructureInputModel)
        assert isinstance(model.workflow_model, WorkflowInputModel)
        assert isinstance(model.resource_model, ComputationalResourcesModel)
        assert isinstance(model.results_model, ResultsModel)
        assert model.process is None

    def test_results_blocked_by_default(self):
        """Results are blocked until a process is submitted."""
        model = MainAppModel()
        assert model.block_results is True
        assert model.results_model.blocked is True

    def test_block_results_dlinks_to_results_model(self):
        """Unblocking the app unblocks the results model via dlink."""
        model = MainAppModel()
        model.block_results = False
        assert model.results_model.blocked is False

    def test_reset_clears_submitted(self):
        """reset() returns every step to an unsubmitted state."""
        model = MainAppModel()
        model.structure_model.submitted = True
        model.workflow_model.submitted = True
        model.resource_model.submitted = True

        model.reset()

        assert model.structure_model.submitted is False
        assert model.workflow_model.submitted is False
        assert model.resource_model.submitted is False

    def test_resource_submit_triggers_process(self, monkeypatch, dlpoly_code):
        """Marking resources submitted builds and submits a process."""
        captured = _capture_submit(monkeypatch)
        model = _ready_model(dlpoly_code)

        model.resource_model.submitted = True

        assert model.process is not None
        assert "builder" in captured

    def test_submit_unblocks_results(self, monkeypatch, dlpoly_code):
        """A successful submission unblocks and wires up the results model."""
        _capture_submit(monkeypatch)
        model = _ready_model(dlpoly_code)

        model.resource_model.submitted = True

        assert model.block_results is False
        assert model.results_model.blocked is False
        assert model.results_model.process_uuid == model.process.node.uuid

    def test_invalid_submit_creates_no_process(self, monkeypatch):
        """An invalid model does not submit a process."""
        captured = _capture_submit(monkeypatch)
        model = MainAppModel()  # nothing configured

        model.resource_model.submitted = True

        assert model.process is None
        assert "builder" not in captured


class TestValidateModel:
    """Tests for DLPOLYProcess.validate_model."""

    def test_no_structure(self, field_singlefile):
        model = MainAppModel()
        model.workflow_model.force_field = field_singlefile
        model.workflow_model.use_detailed_control = True
        assert DLPOLYProcess.validate_model(model) is False

    def test_no_force_field(self, water_structure):
        model = MainAppModel()
        model.structure_model.structure = water_structure
        assert DLPOLYProcess.validate_model(model) is False

    def test_no_control(self, water_structure, field_singlefile):
        model = MainAppModel()
        model.structure_model.structure = water_structure
        model.workflow_model.force_field = field_singlefile
        assert DLPOLYProcess.validate_model(model) is False

    def test_valid_detailed(self, water_structure, field_singlefile):
        model = MainAppModel()
        model.structure_model.structure = water_structure
        model.workflow_model.force_field = field_singlefile
        model.workflow_model.use_detailed_control = True
        assert DLPOLYProcess.validate_model(model) is True

    def test_valid_control_file(
        self, water_structure, field_singlefile, control_singlefile
    ):
        model = MainAppModel()
        model.structure_model.structure = water_structure
        model.workflow_model.force_field = field_singlefile
        model.workflow_model.control_file = control_singlefile
        assert DLPOLYProcess.validate_model(model) is True

    def test_valid_with_structure_file(
        self, xyz_singlefile, field_singlefile, control_singlefile
    ):
        model = MainAppModel()
        model.structure_model.structure_file = xyz_singlefile
        model.workflow_model.force_field = field_singlefile
        model.workflow_model.control_file = control_singlefile
        assert DLPOLYProcess.validate_model(model) is True


class TestSubmitProcess:
    """Tests for DLPOLYProcess.submit_process builder assembly."""

    def test_detailed_control_builder(self, monkeypatch, dlpoly_code):
        """A detailed-control submission assembles the expected builder."""
        captured = _capture_submit(monkeypatch)
        model = _ready_model(dlpoly_code, detailed=True)

        proc = DLPOLYProcess(model)
        proc.submit_process()
        builder = captured["builder"]

        assert builder.configuration is model.structure_model.structure
        assert builder.field is model.workflow_model.force_field
        assert isinstance(builder.control, Dict)
        assert builder.control.get_dict()["temperature"] == (300.0, "K")
        assert builder.metadata.options.resources["num_mpiprocs_per_machine"] == 8
        assert builder.metadata.options.resources["num_machines"] == 1
        assert proc.node.label == "test run"
        assert proc.node.description == "a test description"

    def test_control_file_builder(self, monkeypatch, dlpoly_code, control_singlefile):
        """A control-file submission passes the file through to the builder."""
        captured = _capture_submit(monkeypatch)
        model = _ready_model(
            dlpoly_code, detailed=False, control_file=control_singlefile
        )

        DLPOLYProcess(model).submit_process()
        builder = captured["builder"]

        assert builder.control is control_singlefile

    def test_structure_file_builder(self, monkeypatch, dlpoly_code):
        """A file-based configuration is passed through to the builder."""
        captured = _capture_submit(monkeypatch)
        model = _ready_model(dlpoly_code, detailed=True, use_file=True)

        DLPOLYProcess(model).submit_process()
        builder = captured["builder"]

        assert builder.configuration is model.structure_model.structure_file

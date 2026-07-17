"""Tests for the ProcessModel and ResultsModel."""

from aiidalab_dlpoly.models.process import ProcessModel
from aiidalab_dlpoly.models.results import ResultsModel


class TestProcessModel:
    """Tests for the base process model."""

    def test_defaults(self):
        """A fresh model has no process attached."""
        model = ProcessModel()
        assert model.process_uuid is None
        assert model.process is None
        assert model.has_process is False
        assert model.inputs == []
        assert model.outputs == []

    def test_invalid_uuid_returns_none(self):
        """A uuid with no matching node resolves to no process."""
        model = ProcessModel()
        model.process_uuid = "00000000-0000-0000-0000-000000000000"
        assert model.process is None
        assert model.has_process is False

    def test_valid_process(self, finished_process_node):
        """A valid uuid resolves to the stored process node."""
        model = ProcessModel()
        model.process_uuid = finished_process_node.uuid
        assert model.has_process is True
        assert model.process.uuid == finished_process_node.uuid

    def test_inputs_outputs_for_process(self, finished_process_node):
        """Inputs and outputs are exposed for a valid process."""
        model = ProcessModel()
        model.process_uuid = finished_process_node.uuid
        # A bare WorkChainNode has no links, but the managers are returned.
        assert list(model.inputs) == []
        assert list(model.outputs) == []


class TestResultsModel:
    """Tests for the results model."""

    def test_blocked_by_default(self):
        """Results are blocked until a process has been submitted."""
        assert ResultsModel().blocked is True

    def test_is_process_model(self):
        """The results model extends the process model."""
        assert isinstance(ResultsModel(), ProcessModel)

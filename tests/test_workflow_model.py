"""Tests for the WorkflowInputModel MVC model."""

from aiidalab_dlpoly.models.workflow import WorkflowInputModel


def test_defaults():
    """A fresh model has no inputs, is not detailed and is not submitted."""
    model = WorkflowInputModel()
    assert model.force_field is None
    assert model.control_file is None
    assert model.use_detailed_control is False
    assert model.submitted is False
    assert model.has_force_field is False
    assert model.has_control_file is False


def test_default_control_values():
    """The default control parameters match the documented defaults."""
    model = WorkflowInputModel()
    assert model.temperature == 300.0
    assert model.timestep == 0.001
    assert model.time_run == 10000
    assert model.time_equilibration == 1000
    assert model.cutoff == 10.0
    assert model.padding == 1.0
    assert model.stats_frequency == 100


def test_has_force_field(field_singlefile):
    """has_force_field reflects an attached FIELD node."""
    model = WorkflowInputModel()
    model.force_field = field_singlefile
    assert model.has_force_field is True


def test_has_control_file(control_singlefile):
    """has_control_file reflects an attached CONTROL node."""
    model = WorkflowInputModel()
    model.control_file = control_singlefile
    assert model.has_control_file is True


def test_control_parameters_format():
    """control_parameters returns (value, unit) pairs with plugin units."""
    model = WorkflowInputModel()
    params = model.control_parameters
    assert params["temperature"] == (300.0, "K")
    assert params["timestep"] == (0.001, "ps")
    assert params["time_run"] == (10000, "steps")
    assert params["time_equilibration"] == (1000, "steps")
    assert params["cutoff"] == (10.0, "ang")
    assert params["padding"] == (1.0, "ang")
    assert params["stats_frequency"] == (100, "steps")


def test_control_parameters_reflect_edits():
    """control_parameters reflects updated trait values."""
    model = WorkflowInputModel()
    model.temperature = 85.0
    model.time_run = 2000
    assert model.control_parameters["temperature"] == (85.0, "K")
    assert model.control_parameters["time_run"] == (2000, "steps")


def test_control_units_cover_all_parameters():
    """Every control parameter has a documented unit."""
    model = WorkflowInputModel()
    assert set(model.CONTROL_UNITS) == set(model.control_parameters)


class TestIsValid:
    """Tests for the is_valid submission gate."""

    def test_invalid_without_force_field(self):
        """No force field means invalid."""
        assert WorkflowInputModel().is_valid is False

    def test_invalid_with_field_but_no_control(self, field_singlefile):
        """Force field but no control file (and not detailed) is invalid."""
        model = WorkflowInputModel()
        model.force_field = field_singlefile
        assert model.is_valid is False

    def test_valid_with_field_and_control_file(
        self, field_singlefile, control_singlefile
    ):
        """Force field plus a control file is valid."""
        model = WorkflowInputModel()
        model.force_field = field_singlefile
        model.control_file = control_singlefile
        assert model.is_valid is True

    def test_valid_with_field_and_detailed_control(self, field_singlefile):
        """Force field plus detailed control (defaults) is valid."""
        model = WorkflowInputModel()
        model.force_field = field_singlefile
        model.use_detailed_control = True
        assert model.is_valid is True

    def test_invalid_detailed_without_field(self):
        """Detailed control without a force field is still invalid."""
        model = WorkflowInputModel()
        model.use_detailed_control = True
        assert model.is_valid is False

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


def test_control_units_cover_all_numeric_parameters():
    """Every numeric control parameter has a documented unit."""
    model = WorkflowInputModel()
    # The ensemble parameters are strings/integers and carry no unit, so they
    # are excluded from CONTROL_UNITS.
    assert set(model.CONTROL_UNITS) <= set(model.control_parameters)
    numeric_params = set(model.control_parameters) - {
        "ensemble",
        "ensemble_method",
        "ensemble_dpd_order",
    }
    assert set(model.CONTROL_UNITS) == numeric_params


class TestEnsemble:
    """Tests for the ensemble control parameters."""

    def test_defaults(self):
        """A fresh model defaults to the NVE ensemble with no method."""
        model = WorkflowInputModel()
        assert model.ensemble == "NVE"
        assert model.ensemble_method == ""
        assert model.ensemble_dpd_order == 0

    def test_nve_requires_no_method(self):
        """NVE does not require an ensemble method."""
        model = WorkflowInputModel()
        model.ensemble = "NVE"
        assert model.available_ensemble_methods == ()
        assert model.requires_ensemble_method is False
        assert model.requires_dpd_order is False

    def test_pmf_requires_no_method(self):
        """PMF does not require an ensemble method."""
        model = WorkflowInputModel()
        model.ensemble = "PMF"
        assert model.requires_ensemble_method is False

    def test_nvt_methods(self):
        """NVT exposes its full set of methods."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        assert model.requires_ensemble_method is True
        assert model.available_ensemble_methods == (
            "Evans",
            "Langevin",
            "Anderson",
            "Berendsen",
            "Hoover",
            "gentle",
            "ttm",
            "dpd",
        )

    def test_npt_and_nst_methods(self):
        """NPT and NST share the same set of methods."""
        model = WorkflowInputModel()
        expected = ("Langevin", "Berendsen", "Hoover", "MTK")
        model.ensemble = "NPT"
        assert model.available_ensemble_methods == expected
        model.ensemble = "NST"
        assert model.available_ensemble_methods == expected

    def test_dpd_requires_order(self):
        """The dpd method (NVT only) requires a DPD order."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "dpd"
        assert model.requires_dpd_order is True
        model.ensemble_method = "Hoover"
        assert model.requires_dpd_order is False


class TestEnsembleControlParameters:
    """Tests for how ensemble parameters appear in the control dictionary."""

    def test_ensemble_always_included(self):
        """The ensemble is always part of the control parameters."""
        model = WorkflowInputModel()
        assert model.control_parameters["ensemble"] == "NVE"

    def test_method_omitted_when_not_required(self):
        """No ensemble method is emitted for ensembles that do not take one."""
        model = WorkflowInputModel()
        model.ensemble = "NVE"
        params = model.control_parameters
        assert "ensemble_method" not in params
        assert "ensemble_dpd_order" not in params

    def test_method_included_when_required(self):
        """The ensemble method is emitted for ensembles that require one."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "Hoover"
        params = model.control_parameters
        assert params["ensemble_method"] == "Hoover"
        assert "ensemble_dpd_order" not in params

    def test_dpd_order_included_for_dpd(self):
        """The DPD order is emitted only for the dpd method."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "dpd"
        model.ensemble_dpd_order = 2
        params = model.control_parameters
        assert params["ensemble_method"] == "dpd"
        assert params["ensemble_dpd_order"] == 2


class TestHasValidEnsemble:
    """Tests for the ensemble validation gate."""

    def test_nve_is_valid(self):
        """NVE needs no method and is valid by default."""
        model = WorkflowInputModel()
        model.ensemble = "NVE"
        assert model.has_valid_ensemble is True

    def test_unknown_ensemble_invalid(self):
        """An unrecognised ensemble is invalid."""
        model = WorkflowInputModel()
        model.ensemble = "XYZ"
        assert model.has_valid_ensemble is False

    def test_method_required_but_missing(self):
        """An ensemble requiring a method is invalid without one."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = ""
        assert model.has_valid_ensemble is False

    def test_method_not_valid_for_ensemble(self):
        """A method that is not valid for the ensemble is invalid."""
        model = WorkflowInputModel()
        model.ensemble = "NPT"
        model.ensemble_method = "Evans"  # NVT-only method
        assert model.has_valid_ensemble is False

    def test_valid_with_method(self):
        """A valid method for the ensemble passes validation."""
        model = WorkflowInputModel()
        model.ensemble = "NPT"
        model.ensemble_method = "MTK"
        assert model.has_valid_ensemble is True

    def test_dpd_order_bounds(self):
        """The dpd method accepts only orders 0, 1 and 2."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "dpd"
        for order in (0, 1, 2):
            model.ensemble_dpd_order = order
            assert model.has_valid_ensemble is True
        model.ensemble_dpd_order = 3
        assert model.has_valid_ensemble is False


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

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
    # Use an ensemble configuration that exposes both the thermostat and barostat
    # couplings so every numeric parameter is present in the control dictionary.
    model.ensemble = "NPT"
    model.ensemble_method = "Hoover"
    # Enable RDF and trajectory writing with explicit intervals so
    # ``rdf_frequency`` and ``traj_interval`` are present.
    model.rdf_frequency = 20
    model.history_frequency = 50
    # The ensemble type/method and traj_key are strings, the DPD order is an
    # integer and the RDF/trajectory flags are booleans, so they carry no unit
    # and are excluded from CONTROL_UNITS.
    assert set(model.CONTROL_UNITS) <= set(model.control_parameters)
    numeric_params = set(model.control_parameters) - {
        "ensemble",
        "ensemble_method",
        "ensemble_dpd_order",
        "print_frequency",
        "rdf_calculate",
        "rdf_print",
        "traj_calculate",
        "traj_key",
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
        assert model.ensemble_thermostat_coupling == 0.1

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

    def test_thermostat_coupling_not_required_for_nve(self):
        """NVE/PMF ensembles do not use a thermostat coupling."""
        model = WorkflowInputModel()
        model.ensemble = "NVE"
        assert model.requires_thermostat_coupling is False
        model.ensemble = "PMF"
        assert model.requires_thermostat_coupling is False

    def test_thermostat_coupling_required_for_method_ensembles(self):
        """NVT/NPT/NST ensembles use a thermostat coupling by default."""
        model = WorkflowInputModel()
        for ensemble in ("NVT", "NPT", "NST"):
            model.ensemble = ensemble
            assert model.requires_thermostat_coupling is True

    def test_thermostat_coupling_not_required_for_dpd(self):
        """The dpd method uses the DPD order instead of a thermostat coupling."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "dpd"
        assert model.requires_thermostat_coupling is False
        assert model.requires_dpd_order is True

    def test_barostat_coupling_default(self):
        """The barostat coupling defaults to 1.0 ps."""
        model = WorkflowInputModel()
        assert model.ensemble_barostat_coupling == 1.0

    def test_barostat_coupling_not_required_for_nve_nvt(self):
        """Ensembles that do not control pressure need no barostat coupling."""
        model = WorkflowInputModel()
        for ensemble in ("NVE", "NVT", "PMF"):
            model.ensemble = ensemble
            assert model.requires_barostat_coupling is False

    def test_barostat_coupling_required_for_npt_nst(self):
        """The pressure-controlling NPT/NST ensembles need a barostat coupling."""
        model = WorkflowInputModel()
        for ensemble in ("NPT", "NST"):
            model.ensemble = ensemble
            assert model.requires_barostat_coupling is True


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
        assert "ensemble_thermostat_coupling" not in params

    def test_thermostat_coupling_omitted_for_nve(self):
        """No thermostat coupling is emitted for method-less ensembles."""
        model = WorkflowInputModel()
        model.ensemble = "NVE"
        assert "ensemble_thermostat_coupling" not in model.control_parameters

    def test_thermostat_coupling_included_with_unit(self):
        """The thermostat coupling is emitted as a ``(value, unit)`` pair."""
        model = WorkflowInputModel()
        model.ensemble = "NPT"
        model.ensemble_method = "Hoover"
        model.ensemble_thermostat_coupling = 0.5
        assert model.control_parameters["ensemble_thermostat_coupling"] == (
            0.5,
            "ps",
        )

    def test_barostat_coupling_omitted_for_non_pressure_ensembles(self):
        """No barostat coupling is emitted for NVE/NVT/PMF ensembles."""
        model = WorkflowInputModel()
        model.ensemble = "NVT"
        model.ensemble_method = "Hoover"
        assert "ensemble_barostat_coupling" not in model.control_parameters

    def test_barostat_coupling_included_with_unit(self):
        """The barostat coupling is emitted as a ``(value, unit)`` pair."""
        model = WorkflowInputModel()
        model.ensemble = "NST"
        model.ensemble_method = "MTK"
        model.ensemble_barostat_coupling = 0.5
        assert model.control_parameters["ensemble_barostat_coupling"] == (
            0.5,
            "ps",
        )


class TestUnitsScheme:
    """Tests for the units scheme control parameter."""

    def test_default_scheme(self):
        """The units scheme defaults to ``default``."""
        model = WorkflowInputModel()
        assert model.units_scheme == "default"

    def test_default_scheme_uses_physical_units(self):
        """The default scheme returns the physical units unchanged."""
        model = WorkflowInputModel()
        assert model.control_unit("temperature") == "K"
        assert model.control_unit("timestep") == "ps"
        assert model.control_unit("cutoff") == "ang"
        assert model.control_unit("time_run") == "steps"

    def test_dpd_scheme_maps_units(self):
        """The dpd scheme maps physical units to their reduced equivalents."""
        model = WorkflowInputModel()
        model.units_scheme = "dpd"
        assert model.control_unit("temperature") == "dpd_temp"
        assert model.control_unit("timestep") == "dpd_t"
        assert model.control_unit("cutoff") == "dpd_l"
        assert model.control_unit("padding") == "dpd_l"
        # Units without a DPD mapping are left unchanged.
        assert model.control_unit("time_run") == "steps"

    def test_io_units_scheme_omitted_for_default(self):
        """No io_units_scheme key is emitted for the default scheme."""
        model = WorkflowInputModel()
        assert "io_units_scheme" not in model.control_parameters

    def test_io_units_scheme_set_for_dpd(self):
        """The dpd scheme adds io_units_scheme to the control dictionary."""
        model = WorkflowInputModel()
        model.units_scheme = "dpd"
        assert model.control_parameters["io_units_scheme"] == "dpd"

    def test_dpd_scheme_applies_to_control_parameters(self):
        """The dpd scheme changes the units of the emitted parameters."""
        model = WorkflowInputModel()
        model.units_scheme = "dpd"
        params = model.control_parameters
        assert params["temperature"] == (300.0, "dpd_temp")
        assert params["timestep"] == (0.001, "dpd_t")
        assert params["cutoff"] == (10.0, "dpd_l")
        assert params["padding"] == (1.0, "dpd_l")
        assert params["time_run"] == (10000, "steps")

    def test_dpd_scheme_applies_to_couplings(self):
        """The dpd scheme maps the thermostat/barostat coupling units too."""
        model = WorkflowInputModel()
        model.units_scheme = "dpd"
        model.ensemble = "NPT"
        model.ensemble_method = "Hoover"
        params = model.control_parameters
        assert params["ensemble_thermostat_coupling"][1] == "dpd_t"
        assert params["ensemble_barostat_coupling"][1] == "dpd_t"


class TestRDF:
    """Tests for the RDF control parameters, driven by ``rdf_frequency``."""

    def test_default_disabled(self):
        """RDF collection is disabled by default (frequency 0)."""
        model = WorkflowInputModel()
        assert model.rdf_frequency == 0

    def test_omitted_when_zero(self):
        """A zero frequency emits no RDF keys."""
        model = WorkflowInputModel()
        model.rdf_frequency = 0
        params = model.control_parameters
        assert "rdf_calculate" not in params
        assert "rdf_print" not in params
        assert "rdf_frequency" not in params

    def test_positive_frequency_enables_collection(self):
        """A positive frequency emits the calculate and print flags."""
        model = WorkflowInputModel()
        model.rdf_frequency = 20
        params = model.control_parameters
        assert params["rdf_calculate"] is True
        assert params["rdf_print"] is True

    def test_frequency_included_with_unit(self):
        """A positive frequency is emitted as a ``(value, unit)`` pair."""
        model = WorkflowInputModel()
        model.rdf_frequency = 20
        assert model.control_parameters["rdf_frequency"] == (20, "steps")


class TestHistory:
    """Tests for the trajectory (HISTORY file) control parameters."""

    def test_default_disabled(self):
        """Trajectory writing is disabled by default (frequency 0)."""
        model = WorkflowInputModel()
        assert model.history_frequency == 0

    def test_omitted_when_zero(self):
        """A zero frequency emits no trajectory keys."""
        model = WorkflowInputModel()
        model.history_frequency = 0
        params = model.control_parameters
        assert "traj_calculate" not in params
        assert "traj_key" not in params
        assert "traj_interval" not in params

    def test_positive_frequency_enables_writing(self):
        """A positive frequency turns on trajectory writing at that interval."""
        model = WorkflowInputModel()
        model.history_frequency = 50
        params = model.control_parameters
        assert params["traj_calculate"] is True
        assert params["traj_interval"] == (50, "steps")

    def test_traj_key_defaults_to_pos_vel(self):
        """The trajectory detail level defaults to positions and velocities."""
        model = WorkflowInputModel()
        model.history_frequency = 50
        assert model.control_parameters["traj_key"] == "pos-vel"


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

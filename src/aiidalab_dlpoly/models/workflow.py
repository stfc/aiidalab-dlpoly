"""The workflow input model for DL_POLY input configuration."""

import traitlets as tl
from aiida.orm import SinglefileData


class WorkflowInputModel(tl.HasTraits):
    """
    Model for the DL_POLY workflow configuration step.

    Stores the force field definition and the simulation control input. The
    control input can be supplied either as a pre-formatted DL_POLY ``CONTROL``
    file or, when ``use_detailed_control`` is set, as a set of key control
    parameters that are assembled into a control dictionary for the
    ``aiida-dlpoly`` plugin.
    """

    # Units expected by the aiida-dlpoly plugin for each numeric control
    # parameter. The ensemble parameters are strings/integers and carry no unit.
    CONTROL_UNITS = {
        "temperature": "K",
        "timestep": "ps",
        "time_run": "steps",
        "time_equilibration": "steps",
        "cutoff": "ang",
        "padding": "ang",
        "stats_frequency": "steps",
    }

    # Valid ensemble types accepted by DL_POLY.
    ENSEMBLES = ("NVE", "NVT", "NPT", "NST", "PMF")

    # Ensemble methods valid for each ensemble that requires one. Ensembles not
    # listed here (NVE, PMF) do not take an ensemble method.
    ENSEMBLE_METHODS = {
        "NVT": (
            "Evans",
            "Langevin",
            "Anderson",
            "Berendsen",
            "Hoover",
            "gentle",
            "ttm",
            "dpd",
        ),
        "NPT": ("Langevin", "Berendsen", "Hoover", "MTK"),
        "NST": ("Langevin", "Berendsen", "Hoover", "MTK"),
    }

    # Valid DPD orders, required when the ensemble method is ``dpd``.
    DPD_ORDERS = (0, 1, 2)

    force_field = tl.Instance(SinglefileData, allow_none=True)

    use_detailed_control = tl.Bool(False).tag(sync=True)
    control_file = tl.Instance(SinglefileData, allow_none=True)

    # Key DL_POLY control parameters (used when use_detailed_control is True).
    temperature = tl.Float(300.0).tag(sync=True)
    timestep = tl.Float(0.001).tag(sync=True)
    time_run = tl.Int(10000).tag(sync=True)
    time_equilibration = tl.Int(1000).tag(sync=True)
    cutoff = tl.Float(10.0).tag(sync=True)
    padding = tl.Float(1.0).tag(sync=True)
    stats_frequency = tl.Int(100).tag(sync=True)

    # Ensemble control parameters. ``ensemble_method`` is only meaningful for the
    # NVT/NPT/NST ensembles and ``ensemble_dpd_order`` only when the method is
    # ``dpd``.
    ensemble = tl.Unicode("NVE").tag(sync=True)
    ensemble_method = tl.Unicode("").tag(sync=True)
    ensemble_dpd_order = tl.Int(0).tag(sync=True)

    submitted = tl.Bool(False).tag(sync=True)

    @property
    def has_force_field(self) -> bool:
        """True if a force field file has been attached to the model."""
        return self.force_field is not None

    @property
    def has_control_file(self) -> bool:
        """True if a control file has been attached to the model."""
        return self.control_file is not None

    @property
    def available_ensemble_methods(self) -> tuple:
        """The ensemble methods valid for the currently selected ensemble.

        Returns an empty tuple for ensembles (NVE, PMF) that do not take a
        method.
        """
        return self.ENSEMBLE_METHODS.get(self.ensemble, ())

    @property
    def requires_ensemble_method(self) -> bool:
        """True if the selected ensemble requires an ensemble method."""
        return bool(self.available_ensemble_methods)

    @property
    def requires_dpd_order(self) -> bool:
        """True if the selected ensemble method requires a DPD order."""
        return self.requires_ensemble_method and self.ensemble_method == "dpd"

    @property
    def control_parameters(self) -> dict:
        """Return the detailed control parameters as a control dictionary.

        The format matches the control dictionary consumed by the
        ``aiida-dlpoly`` plugin, where every numeric input is a
        ``(value, unit)`` pair. The ensemble parameters are added as plain
        values, with ``ensemble_method`` only included when the ensemble
        requires one and ``ensemble_dpd_order`` only when the method is ``dpd``.
        """
        parameters = {
            "temperature": (self.temperature, self.CONTROL_UNITS["temperature"]),
            "timestep": (self.timestep, self.CONTROL_UNITS["timestep"]),
            "time_run": (self.time_run, self.CONTROL_UNITS["time_run"]),
            "time_equilibration": (
                self.time_equilibration,
                self.CONTROL_UNITS["time_equilibration"],
            ),
            "cutoff": (self.cutoff, self.CONTROL_UNITS["cutoff"]),
            "padding": (self.padding, self.CONTROL_UNITS["padding"]),
            "stats_frequency": (
                self.stats_frequency,
                self.CONTROL_UNITS["stats_frequency"],
            ),
            "ensemble": self.ensemble,
        }
        if self.requires_ensemble_method:
            parameters["ensemble_method"] = self.ensemble_method
        if self.requires_dpd_order:
            parameters["ensemble_dpd_order"] = self.ensemble_dpd_order
        return parameters

    @property
    def has_valid_ensemble(self) -> bool:
        """True if the ensemble configuration is complete and self-consistent.

        The ensemble must be a recognised type; when it requires a method the
        method must be one of the valid options for that ensemble; and when the
        method is ``dpd`` a valid DPD order must be selected.
        """
        if self.ensemble not in self.ENSEMBLES:
            return False
        if self.requires_ensemble_method:
            if self.ensemble_method not in self.available_ensemble_methods:
                return False
            if (
                self.requires_dpd_order
                and self.ensemble_dpd_order not in self.DPD_ORDERS
            ):
                return False
        return True

    @property
    def is_valid(self) -> bool:
        """True if the model holds a complete, submittable configuration.

        A force field is always required. When detailed control is disabled a
        control file must be supplied; when enabled a valid ensemble
        configuration is required.
        """
        if not self.has_force_field:
            return False
        if not self.use_detailed_control:
            return self.has_control_file
        return self.has_valid_ensemble

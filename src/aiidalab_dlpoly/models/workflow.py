"""The workflow input model for DL_POLY input configuration."""

from aiida.orm import SinglefileData
from traitlets import Bool, Float, HasTraits, Instance, Int


class WorkflowInputModel(HasTraits):
    """
    Model for the DL_POLY workflow configuration step.

    Stores the force field definition and the simulation control input. The
    control input can be supplied either as a pre-formatted DL_POLY ``CONTROL``
    file or, when ``use_detailed_control`` is set, as a set of key control
    parameters that are assembled into a control dictionary for the
    ``aiida-dlpoly`` plugin.
    """

    # Units expected by the aiida-dlpoly plugin for each control parameter.
    CONTROL_UNITS = {
        "temperature": "K",
        "timestep": "ps",
        "time_run": "steps",
        "time_equilibration": "steps",
        "cutoff": "ang",
        "padding": "ang",
        "stats_frequency": "steps",
    }

    force_field = Instance(SinglefileData, allow_none=True)

    use_detailed_control = Bool(False).tag(sync=True)
    control_file = Instance(SinglefileData, allow_none=True)

    # Key DL_POLY control parameters (used when use_detailed_control is True).
    temperature = Float(300.0).tag(sync=True)
    timestep = Float(0.001).tag(sync=True)
    time_run = Int(10000).tag(sync=True)
    time_equilibration = Int(1000).tag(sync=True)
    cutoff = Float(10.0).tag(sync=True)
    padding = Float(1.0).tag(sync=True)
    stats_frequency = Int(100).tag(sync=True)

    submitted = Bool(False).tag(sync=True)

    @property
    def has_force_field(self) -> bool:
        """True if a force field file has been attached to the model."""
        return self.force_field is not None

    @property
    def has_control_file(self) -> bool:
        """True if a control file has been attached to the model."""
        return self.control_file is not None

    @property
    def control_parameters(self) -> dict:
        """Return the detailed control parameters as a ``(value, unit)`` dict.

        The format matches the control dictionary consumed by the
        ``aiida-dlpoly`` plugin, where every numeric input is a
        ``(value, unit)`` pair.
        """
        return {
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
        }

    @property
    def is_valid(self) -> bool:
        """True if the model holds a complete, submittable configuration.

        A force field is always required. When detailed control is disabled a
        control file must be supplied; when enabled the parameter defaults are
        always valid.
        """
        if not self.has_force_field:
            return False
        if not self.use_detailed_control and not self.has_control_file:
            return False
        return True

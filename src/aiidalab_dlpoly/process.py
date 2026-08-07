"""Module for handling the top-level application model and AiiDA processes."""

import ipywidgets as ipw
import traitlets as tl
from aiida.engine import submit
from aiida.orm import Dict, load_code

from aiidalab_dlpoly.models.resources import ComputationalResourcesModel
from aiidalab_dlpoly.models.results import ResultsModel
from aiidalab_dlpoly.models.structure import StructureInputModel
from aiidalab_dlpoly.models.workflow import WorkflowInputModel


class MainAppModel(tl.HasTraits):
    """The main AiiDAlab application MVC model.

    Aggregates the per-step models used across the configuration wizard and
    handles submission of the resulting DL_POLY process to AiiDA.
    """

    block_results = tl.Bool(True, allow_none=False)

    def __init__(self):
        """MainAppModel constructor."""
        super().__init__()
        self.structure_model = StructureInputModel()
        self.workflow_model = WorkflowInputModel()
        self.resource_model = ComputationalResourcesModel()
        self.results_model = ResultsModel()

        self.resource_model.observe(self._submit_model, "submitted")
        ipw.dlink((self, "block_results"), (self.results_model, "blocked"))

        self.process = None

        return

    def _submit_model(self, _) -> None:
        """Handle the submission of the AiiDA process."""
        if DLPOLYProcess.validate_model(self):
            self.process = DLPOLYProcess(self)
            self.process.submit_process()
            self.block_results = False
            self.results_model.process_uuid = self.process.node.uuid
        else:
            print("ERROR: Input Validation Failed")
        return

    def reset(self) -> None:
        """Reset the state of the model."""
        self.structure_model.submitted = False
        self.workflow_model.submitted = False
        self.resource_model.submitted = False
        return


class DLPOLYProcess:
    """Class to handle a DL_POLY AiiDA process."""

    def __init__(self, model: MainAppModel):
        """
        DLPOLYProcess constructor.

        Parameters
        ----------
        model : MainAppModel
            The main application model containing all necessary data.
        """
        self.model = model
        self.node = None
        return

    @classmethod
    def validate_model(cls, model: MainAppModel) -> bool:
        """
        Validate the main application model.

        Parameters
        ----------
        model : MainAppModel
            The main application model to validate.

        Returns
        -------
        bool
            True if the model is valid, False otherwise.
        """
        if not model.structure_model.has_structure:
            if not model.structure_model.has_file:
                print("No structure provided.")
                return False
        if not model.workflow_model.has_force_field:
            print("No force field provided.")
            return False
        if not model.workflow_model.use_detailed_control:
            if not model.workflow_model.has_control_file:
                print("No control input provided.")
                return False
        return True

    def submit_process(self) -> None:
        """Submit the AiiDA process."""
        self._submit_calcjob()
        return

    def _submit_calcjob(self) -> None:
        # Get the DL_POLY code instance and its builder.
        builder = load_code(self.model.resource_model.code_label).get_builder()
        # Configure the structure/configuration input.
        if self.model.structure_model.has_file:
            builder.configuration = self.model.structure_model.structure_file
        else:
            builder.configuration = self.model.structure_model.structure
        # Configure the force field input.
        builder.field = self.model.workflow_model.force_field
        # Configure the control input, either a file or detailed parameters.
        if self.model.workflow_model.use_detailed_control:
            builder.control = Dict(dict(self.model.workflow_model.control_parameters))
        else:
            builder.control = self.model.workflow_model.control_file
        # Setup metadata and resource parameters.
        builder.metadata.options.resources = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        # Submit and apply the label/description to the CalcJob.
        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

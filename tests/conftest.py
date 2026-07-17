"""Shared pytest fixtures for the aiidalab-dlpoly test suite."""

import io

import pytest
from aiida.orm import SinglefileData, StructureData
from ase.build import bulk, molecule

# Register the AiiDA-provided pytest fixtures (aiida_profile, etc.). These
# spin up a temporary, throw-away AiiDA profile (SQLite storage, no external
# PostgreSQL required) for the test session so that Node creation and
# QueryBuilder queries work.
pytest_plugins = ["aiida.tools.pytest_fixtures"]


@pytest.fixture(scope="session", autouse=True)
def _load_profile(aiida_profile):
    """Ensure a temporary AiiDA profile is loaded for every test."""
    yield aiida_profile


@pytest.fixture(scope="session", autouse=True)
def dlpoly_code(aiida_profile):
    """Create (once) a DL_POLY ``InstalledCode`` on a localhost computer.

    The resources wizard step populates a code dropdown on construction and
    links its value to a ``Unicode`` trait, so a code must exist for the step
    (and any wizard/view that builds it) to construct. This mirrors a real
    deployment where a DL_POLY code is always registered.
    """
    from aiida.orm import Computer, InstalledCode, load_code

    try:
        computer = Computer.collection.get(label="localhost")
    except Exception:
        computer = Computer(
            label="localhost",
            hostname="localhost",
            transport_type="core.local",
            scheduler_type="core.direct",
            workdir="/tmp/aiida_dlpoly_tests",
        ).store()
        computer.configure()

    try:
        return load_code("dlpoly@localhost")
    except Exception:
        return InstalledCode(
            computer=computer,
            filepath_executable="/bin/true",
            default_calc_job_plugin="dlpoly",
            label="dlpoly",
        ).store()


@pytest.fixture
def water_atoms():
    """Return a non-periodic water molecule as an ``ase.Atoms`` object."""
    return molecule("H2O")


@pytest.fixture
def water_structure(water_atoms):
    """Return a non-periodic water molecule as ``StructureData``."""
    return StructureData(ase=water_atoms)


@pytest.fixture
def periodic_structure():
    """Return a periodic (bulk) structure as ``StructureData``."""
    return StructureData(ase=bulk("Cu", "fcc", a=3.6))


@pytest.fixture
def xyz_bytes():
    """Return the raw bytes of a minimal XYZ water file."""
    return b"3\nWater\nO 0.0  0.000  0.000\nH 0.0  0.757  0.586\nH 0.0 -0.757  0.586\n"


@pytest.fixture
def xyz_singlefile(xyz_bytes):
    """Return a ``SinglefileData`` node wrapping a minimal XYZ water file."""
    return SinglefileData(file=io.BytesIO(xyz_bytes), filename="water.xyz")


@pytest.fixture
def field_singlefile():
    """Return a ``SinglefileData`` node standing in for a DL_POLY FIELD file."""
    return SinglefileData(file=io.BytesIO(b"FIELD placeholder\n"), filename="FIELD")


@pytest.fixture
def control_singlefile():
    """Return a ``SinglefileData`` node standing in for a DL_POLY CONTROL file."""
    return SinglefileData(
        file=io.BytesIO(b"title Test\ntemperature 300.0 K\n"), filename="CONTROL"
    )


@pytest.fixture
def finished_process_node():
    """Return a stored, sealed, finished ``WorkChainNode``."""
    from aiida.orm import WorkChainNode
    from plumpy.process_states import ProcessState

    node = WorkChainNode()
    node.set_process_state(ProcessState.FINISHED)
    node.set_exit_status(0)
    node.store()
    node.seal()
    return node

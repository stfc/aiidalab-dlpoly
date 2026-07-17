"""Defines the MVC model for holding DL_POLY results information."""

from traitlets import Bool

from aiidalab_dlpoly.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = Bool(True)

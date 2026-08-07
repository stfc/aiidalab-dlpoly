"""Defines the MVC model for holding DL_POLY results information."""

import traitlets as tl

from aiidalab_dlpoly.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = tl.Bool(True)

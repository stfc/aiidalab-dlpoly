"""Defines the main AiiDAlab application page."""

from datetime import datetime

import ipywidgets as ipw
from IPython.display import display

from aiidalab_dlpoly.common.navigation import QuickAccessButtons
from aiidalab_dlpoly.process import MainAppModel
from aiidalab_dlpoly.wizards.main_app import MainAppWizardWidget


class MainApp:
    """The main AiiDAlab application class."""

    def __init__(self):
        """MainApp constructor."""
        self.model = MainAppModel()
        self.view = MainAppView(self.model)
        display(self.view)


class MainAppView(ipw.VBox):
    """The main app view."""

    def __init__(self, model: MainAppModel, **kwargs):
        """MainAppView constructor."""
        logo = ipw.HTML(
            """
            <div class="app-container logo" style="width: 300px;">
                <img src="../images/DL_Software_logo.png"
                     alt="DL_Software AiiDAlab App Logo"
                     style="width: 100%;" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        title = ipw.HTML(
            """
            <h1 id='title'>AiiDAlab DL_POLY</h1>
            """
        )

        subtitle = ipw.HTML(
            """
            <h2 id='subtitle'>
                Configure and run DL_POLY molecular dynamics simulations
            </h2>
            """
        )

        header = ipw.VBox(
            children=[
                logo,
                title,
                subtitle,
            ],
            layout={"margin": "auto"},
        )

        nav_btns = QuickAccessButtons()

        footer = ipw.HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} STFC Daresbury Laboratory <br>
            </footer>
            """,
            layout={"align-content": "right"},
        )

        self.main = MainAppWizardWidget(model)

        super().__init__(
            layout={}, children=[header, nav_btns, self.main, footer], **kwargs
        )

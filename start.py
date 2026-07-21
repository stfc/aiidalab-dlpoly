"""Defines the main AiiDAlab app's start banner."""

import ipywidgets as ipw

from aiidalab_dlpoly.common.navigation import QuickAccessButtons


def get_start_widget(appbase, jupbase, notebase):
    """Get the AiiDAlab app's start banner."""
    logo = ipw.HTML(
        f"""
        <div class="app-container" style="width: 400px;margin: auto;">
            <a class="logo" href="{appbase}/notebooks/main.ipynb" target="_blank">
            <img src="{appbase}/images/DL_Software_logo.png"
                 alt="DL_Software AiiDAlab App Logo" />
            </a>
        </div>
        """
    )
    return ipw.VBox(
        children=[
            logo,
            QuickAccessButtons(),
        ]
    )

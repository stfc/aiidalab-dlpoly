Getting Started
===============

Installation
------------

Install the application into an AiiDAlab environment with:

.. code-block:: bash

   pip install .

Once installed, the application appears on the AiiDAlab home page. Click
**Start DL_POLY** (or **New Calculation**) to open ``main.ipynb``.

The configuration wizard
------------------------

The main application presents a wizard that walks through the steps required to
configure and submit a DL_POLY simulation:

#. **Select Structure** — upload a ``CONFIG`` file or select an existing
   structure from the AiiDA database.
#. **Configure Workflow** — provide the force field (``FIELD``) file and the
   simulation control input, either as a pre-formatted ``CONTROL`` file or via
   the key control parameters (temperature, timestep, run/equilibration time,
   cutoff, padding and statistics frequency).
#. **Configure Computational Resources** — select the DL_POLY code, the number
   of CPUs and an optional process label/description, then submit.
#. **Results** — inspect the progress, inputs, outputs and provenance of the
   submitted process.

Additional pages
----------------

The start banner and application header provide quick-access navigation to:

* **History** (``history.ipynb``) — browse and visualise past DL_POLY processes.
* **Setup Resources** (``resources.ipynb``) — create and manage computer
  connections and DL_POLY code instances.

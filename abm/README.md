# Sown biodiverse pastures agent-based model

## Usage

To run the ABM interactively run ``run.py`` in this directory. e.g.

```
    $ python run.py
```
The Jupyter Notebooks in the ``model_validation`` and ``pcf_project_assessment`` folders run instead multiple simulations with the ABM, only extracting the results wihtout the interactive visualization.

**IMPORTANT**: the model cannot be run since data on yearly adoption and on climate and soil properties could not be provided. The missing files (in the ``data`` folder) are:
* ``% yearly SBP adoption per municipality.csv``
* ``municipalities_average_climate_final.csv``
* ``municipalities_soil_final.csv``

## Folders

* ``abm``: core ABM, agent and visualization code.
* ``ml_model``: folder with the saved machine learning models and everything needed to upload them in the ABM.
* ``model_validation``: validation of the ABM.
* ``pcf_project_assessment``: assessment of the Portuguese Carbon Fund project.
* ``data``: input data for the ABM.
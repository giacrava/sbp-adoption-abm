# sbp-adoption-abm

This agent-based model (ABM) simulates the adoption of sown biodiverse pastures (SBP) in Portugal. It focuses in particular on the Portuguese Carbon Fund project, a programme of payments for ecosystems services which ran from 2009 to 2012 to incentivise SBP adoption. 
The main agents are the Portuguese municipalities, which each year estimate how much area of SBP is installed in their territory. The ABM follows a data-driven approach, where the behavioural model of the agents is composed of pre-trained machine learning models.

Repository for the paper Ravaioli, G., Domingos, T. & Teixeira, R.F.M. (2023). Data-driven agent-based modelling of incentives for carbon sequestration: The case of sown biodiverse pastures in Portugal. Journal of Environmental Management.

## Folders

* ``abm`` : main folder, with the agent-based model code.
* ``data_preparation`` : manipulation of the original databases to obtain the ones used to initialise the ABM and train the machine learning models.
* ``ml_models`` : data exploration; selection and analysis of the machine learning models.

## Installation

To install the virtual environment *sbp_adoption_abm* required for this project, open an Anaconda terminal in this directory and run
```
    $ conda env create -f environment.yml
```
Once installed, activate the environment with
```
    $ conda activate sbp_adoption_abm
```


## Note

Some datasets could not be provided for data access restrictions and therefore some Notebooks cannot be run - including the ones running the ABM. The paper specifies how some of these data might be accessed.

## References

The ABM is described in:

Ravaioli, G., Domingos, T. & Teixeira, R.F.M. (2023). Data-driven agent-based modelling of incentives for carbon sequestration: The case of sown biodiverse pastures in Portugal. Journal of Environmental Management.

This ABM follows the framework described in:

Ravaioli, G., Domingos, T., Teixeira, R.F.M., 2023. A Framework for Data-Driven Agent-Based Modelling of Agricultural Land Use. Land 12, 756. https://doi.org/10.3390/land12040756

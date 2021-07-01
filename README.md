# DSND Capstone Project
[![Udacity - Data Sciencd NanoDegree](https://img.shields.io/badge/Udacity-DSND-blue?style=plastic&logo=udacity)](https://www.udacity.com/course/data-scientist-nanodegree--nd025)


## Overview
This is the final Capstone Project submitted as part of the Udacity Data Science Nanodegree.

For it the goal is to analize the log files coming from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

The code for this project is submitted in the form of Jupyter notebooks available in the [`notebooks`](/notebooks) folder. A detailed explanation is provided in a separate [writeup](./Capstone_writeup), that documents also the results obtained.


## Requirements for local execution
In order to facilitate the execution of it  I have prepared an [`environment.yml`](./environment.yml) file to be used to install an environment with [Anaconda](https://www.anaconda.com/):

```sh
conda env create -f environment.yml
```

After the installation the environment should be visible via `conda info --envs`:

```sh
# conda environments:
#
dsnd-capstone        /usr/local/anaconda3/envs/dsnd-capstone
...

```

Further documentation on working with Anaconda environments can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html). 

## License
 <a rel="license" href="https://opensource.org/licenses/MIT"><img alt="MIT License" style="border-width:0" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic" /></a><br />This work is licensed under an <a rel="license" href="https://opensource.org/licenses/MIT">MIT License</a>.

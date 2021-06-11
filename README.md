# Recommendation Engine Project
[![Udacity - Data Sciencd NanoDegree](https://img.shields.io/badge/Udacity-DSND-blue?style=plastic&logo=udacity)](https://www.udacity.com/course/data-scientist-nanodegree--nd025)


## Overview
This Project is submitted as part of the Udacity Data Science Nanodegree.

For it the target is to analyze the interactions that users have with articles on the [IBM Watson Studio platform](https://www.ibm.com/cloud/watson-studio), and make recommendations to them about new articles we believe they will like.  
Below you can see an example of what the dashboard could look like when displaying articles on the platform:

<p align="center">
  <img src="./pictures/screenshot-watson.png">
</p>


## Requirements
The exercise is completed as a Jupyter notebook, and in order to facilitate the execution of it  I have prepared an [`environment.yml`](./environment.yml) file to be used to install an environment with [Anaconda](https://www.continuum.io/downloads):

```sh
conda env create -f environment.yml
```

After the installation the environment should be visible via `conda info --envs`:

```sh
# conda environments:
#
dsnd-proj5        /usr/local/anaconda3/envs/dsnd-proj5
...

```

Further documentation on working with Anaconda environments can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html). 

## Results
The (fairly self-explanatory) Jupyter notebook is available [here](./Recommendations_with_IBM.ipynb); for the sake of simplicity, the same notebook is also available in [HTML format](./Recommendations_with_IBM.html).  

More details on the various sections within the notebook are provided in a separated [writeup](./Recommendation_engine_writeup.md). 

## License
 <a rel="license" href="https://opensource.org/licenses/MIT"><img alt="MIT License" style="border-width:0" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic" /></a><br />This work is licensed under an <a rel="license" href="https://opensource.org/licenses/MIT">MIT License</a>.

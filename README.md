# DSND Capstone Project
[![Udacity - Data Sciencd NanoDegree](https://img.shields.io/badge/Udacity-DSND-blue?style=plastic&logo=udacity)](https://www.udacity.com/course/data-scientist-nanodegree--nd025)


## Overview
This is the final Capstone Project submitted as part of the Udacity Data Science Nanodegree.

For it the goal is to use [**Spark**](https://spark.apache.org/) to analize the log files coming from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

The code for this project is submitted in the form of Jupyter notebooks available in the [`notebooks`](/notebooks) folder.  
In there it's possible to find two Jupyter notebooks: [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb), that makes use of Spark in local mode and is intended to be used with a limited set of data on a PC, and [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) that was used to analize a broader set of data using a Spark cluster deployed on [AWS EMR](https://aws.amazon.com/emr/).  
Moreover, in the same folder it's possible to find the same notebooks saved in HTML format, for convenience.

A detailed description of the steps taken in order to solve the problem is provided in a separate [writeup](./Capstone_writeup.md), that documents also the results obtained.


## Requirements for local execution
In order to facilitate the execution of the notebook intended for local use, it I have prepared an [`environment.yml`](./environment.yml) file to be used to install an environment with [Anaconda](https://www.anaconda.com/):

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

## Notes on EMR environment
There are several ways of running a Spark cluster in a cloud platform: as mentioned, for this project I have used AWS EMR to set one up, but, for example, the Udacity team provided also guidance on how to use [IBM Watson](https://cloud.ibm.com/developer/watson/dashboard).

At any rate, in my case the cluster was composed by: **4** nodes (1 Master, 3 Workers), consisting of [m5.xlarge](https://aws.amazon.com/blogs/aws/m5-the-next-generation-of-general-purpose-ec2-instances/) EC2 VMs, running:

* EMR 5.33
* Spark 2.4.7
* Livy 0.7.0 
* Hive 2.3.7 
* JupyterEnterpriseGateway 2.1.0

In terms of documentation, the [EMR Mangement guide](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html) is a valuable resource, together with the [EMR Big Data blog](https://aws.amazon.com/blogs/big-data/).  
Personally I found particularly helpful the sections/post on:

* [Connecting to the Master node using SSH](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-connect-master-node-ssh.html)
* [Visualising the Spark web interfaces](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-web-interfaces.html)
* [Installing additional Python libraries on a Jupyter notebook](https://aws.amazon.com/blogs/big-data/install-python-libraries-on-a-running-cluster-with-emr-notebooks/)

## License
 <a rel="license" href="https://opensource.org/licenses/MIT"><img alt="MIT License" style="border-width:0" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic" /></a><br />This work is licensed under an <a rel="license" href="https://opensource.org/licenses/MIT">MIT License</a>.

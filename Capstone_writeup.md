## Capstone Project
The goal of this project is to use [**Spark**](https://spark.apache.org/) to analize the log files collected from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

---
## Data
The data for this project was provided by Udacity in JSON format, in two differen forms:

* A limited dataset (~128 MB, 280000 lines), to be used for analysis on a local machine. This is what I used in the [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb) notebook; the actual dataset can be downloaded from [here](https://drive.google.com/file/d/1gX1X-D8G4vE29AAUeQHapv5P_vNs6Jcv/view?usp=sharing).
* A complete dataset (mor than 26 Mil lines), to be loaded on a cluster. This is what i leverage in the [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) notebook: it is stored in an [AWS S3](https://aws.amazon.com/s3/) bucket available at `s3n://udacity-dsnd/sparkify/sparkify_event_data.json`.

## Capstone Project
The goal of this project is to use [**Spark**](https://spark.apache.org/) to analize the log files collected from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

---
## Data
The data for this project was provided by Udacity in JSON format, in two differen forms:

* A limited dataset (~128 MB, 280000 rows), to be used for analysis on a local machine. This is what I use in the [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb) notebook; the actual dataset can be downloaded from [here](https://drive.google.com/file/d/1gX1X-D8G4vE29AAUeQHapv5P_vNs6Jcv/view?usp=sharing).
* A complete dataset (more than 26 Mil rows), to be loaded on a cluster. This is what I explore in the [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) notebook: it is stored in an [AWS S3](https://aws.amazon.com/s3/) bucket available at `s3n://udacity-dsnd/sparkify/sparkify_event_data.json`.

---
## Content of the notebooks
Both the notebook present the same table of contents; at a high level we have the following sections:

1. Load Libraries
2. [Load and Clean Dataset](#load-and-clean-dataset)
3. [Data Exploration](#data-exploration)
4. [Modeling](#modeling)
5. [Optimization](#optimization)

In the following we'll see details on all of them (except for the first one). I will essentially make reference to the `local` notebook, clarifying commonalities and differences with the `EMR` one as I go.

Finally, a [Conclusions](#Conclusions) section will summarize the results and possible improvement strategies.

### _Load and Clean Dataset_
This part is fairly similar for both the local and EMR cases: the first operation is to load the JSON file:

```
  # Load data
  <Path defined accordingly>
  df_user_log = spark.read.json(path)
```

After that we can look at the schema of the loaded data frame:

```
  # Check schema
  df_user_log.printSchema()
```
```
root
 |-- artist: string (nullable = true)
 |-- auth: string (nullable = true)
 |-- firstName: string (nullable = true)
 |-- gender: string (nullable = true)
 |-- itemInSession: long (nullable = true)
 |-- lastName: string (nullable = true)
 |-- length: double (nullable = true)
 |-- level: string (nullable = true)
 |-- location: string (nullable = true)
 |-- method: string (nullable = true)
 |-- page: string (nullable = true)
 |-- registration: long (nullable = true)
 |-- sessionId: long (nullable = true)
 |-- song: string (nullable = true)
 |-- status: long (nullable = true)
 |-- ts: long (nullable = true)
 |-- userAgent: string (nullable = true)
 |-- userId: string (nullable = true)
```

We can check an example of the data extracting the first row:

```
  # Show the first row
  df_user_log.head()
```
```
Row(artist='Martha Tilston', auth='Logged In', firstName='Colin', gender='M', itemInSession=50, lastName='Freeman', length=277.89016, level='paid', location='Bakersfield, CA', method='PUT', page='NextSong', registration=1538173362000, sessionId=29, song='Rockpools', status=200, ts=1538352117000, userAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0', userId='30')
```

We can also check the number of rows and columns in the dataset. Here, of course, we could see the difference between the limited dataset and the full one:

```
  # Check num of rows, columns
  print('Num. of rows in the dataset: ', df_user_log.count(), '; Num. of columns: ', len(df_user_log.columns))
```

_Limited Dataset_
```
Num. of rows in the dataset:  286500 ; Num. of columns:  18
```

_Full Dataset_
```
Number of rows in the dataset:  26259199 ; Number of columns:  18
```

In terms of cleaning, what I did is I got rid of rows with:

* Any `NaN` eventually present in the `sessionId` or `userId` fields: this could have been the consequence of errors or bugs in the logging ysytem;
* Any `Nan` eventually present in the `gender` or `location` fields: I use these in part of the exploration phase, to look at demographics;
* Any emty `userId` field still remaining: this would be most likely assiciated with the very first interaction of the users with the system.

```
  # Drop NaN in userId and sessionId
  df_user_log_valid = df_user_log.dropna(how = "any", subset = ["userId", "sessionId"])

  # Drop NaN in gender and location
  df_user_log_valid = df_user_log.dropna(how = "any", subset = ["gender", "location"])

  # Drop empty users
  df_user_log_valid = df_user_log_valid.filter(df_user_log_valid["userId"] != "")
```

We can then check the number of remaining rows:

```
  # Check num of rows remaining
  print('Num. of rows in the valid dataset: ', df_user_log_valid.count())
```

_Limited Dataset_
```
  Num. of rows in the valid dataset:  278154
```

_Full Dataset_
```
  Num. of rows in the valid dataset:  25480720
```

### _Data Exploration_

### _Modeling_

### _Optimization_

---
## Conclusions 

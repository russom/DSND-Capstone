## Capstone Project
The goal of this project is to use [**Spark**](https://spark.apache.org/) to analize the log files collected from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

---
## Data
The data for this project was provided by Udacity in JSON format, in two differen sizes:

* A _limited_ dataset (~128 MB, 280000 rows), to be used for analysis on a local machine. This is what I use in the [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb) notebook; the actual dataset can be downloaded from [here](https://drive.google.com/file/d/1gX1X-D8G4vE29AAUeQHapv5P_vNs6Jcv/view?usp=sharing).
* A _complete_ dataset (more than 26 Mil rows), to be loaded on a cluster. This is what I explore in the [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) notebook: it is stored in an [AWS S3](https://aws.amazon.com/s3/) bucket available at `s3n://udacity-dsnd/sparkify/sparkify_event_data.json`.

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

_Complete Dataset_
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

_Complete Dataset_
```
  Num. of rows in the valid dataset:  25480720
```

### _Data Exploration_
Looking at the dataset schema, a column that seeming to provide quite a bit of useful information is `page`, that documents the various pages visited by the users:

```
  # Check available pages
  df_user_log_valid.select("page").dropDuplicates().sort("page").show()
```
```
+--------------------+
|                page|
+--------------------+
|               About|
|          Add Friend|
|     Add to Playlist|
|              Cancel|
|Cancellation Conf...|
|           Downgrade|
|               Error|
|                Help|
|                Home|
|              Logout|
|            NextSong|
|         Roll Advert|
|       Save Settings|
|            Settings|
|    Submit Downgrade|
|      Submit Upgrade|
|         Thumbs Down|
|           Thumbs Up|
|             Upgrade|
+--------------------+
```

Based on the type of information available in this column, we can define new variables identifying, for example, an actual churn (looking at when the users visits `Cancellation Confirmation`) or an `Upgrade`/`Downgrade`, but also events like the user giving a Thumbs Up or adding friends, or seeing a Rolling Advert.  
We can also recontruct the time spent by the users with the system, making reference to the `registration` and `ts` columns.

Starting from these ideas I decided to modify the dataset:

* Introducing a `churn` column based on whether or not the user visits the `Cancellation Confirmation` page;
* Introducing a `sub_dwg` column based on whether or not the user visits the `Submit Downgrade` page;
* Introducing a `sub_upg` column based on whether or not the user visits the `Submit Upgrade` page;
* Converting the UNIX time in `ts` and `registration` from ms to s, for simplicity;
* Introducing a `first_ts` and a `last_ts` column showing the timestamp of the first/last entry for a user;
* Introducing a `perm_days` column showing the (rounded) number of days a user has spent with the service so far;
* Introducing a `data_days` variable showing the (rounded) number of days of data available for a user;
* Introducing a `roll_adv` column based on whether or not the user visits the `Rolled Advert` page;
* Introducing a `total_rolled_advert` column showing the total of the roll advert events per user;
* Introducing an `add_friend` column based on whether or not the user visits the `Add Friend` page;
* Introducing a `total_add_friend` column showing the total of the friends added per user;
* Introducing an `thumbs_up` column based on whether or not the user visits the `Thumbs Up` page;
* Introducing a `total_thumbs_up` column showing the total of the thumbs up given per user;
* Introducing an `thumbs_dwn` column based on whether or not the user visits the `Thumbs Down` page;
* Introducing a `total_thumbs_dwn` column showing the total of the thumbs down given per user;

Once introduced all the column above we can take a look at the data:

```
  # Check columns
  df_user_log_valid.head()
```
```
Row(artist='Sleeping With Sirens', auth='Logged In', firstName='Darianna', gender='F', itemInSession=0, lastName='Carpenter', length=202.97098, level='free', location='Bridgeport-Stamford-Norwalk, CT', method='PUT', page='NextSong', registration=1538016340.0, sessionId=31, song='Captain Tyin Knots VS Mr Walkway (No Way)', status=200, ts=1539003534.0, userAgent='"Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53"', userId='100010', churn=0, sub_dwg=0, sub_upg=0, first_ts=1539003534.0, last_ts=1542823952.0, perm_days=56.0, data_days=44.0, roll_adv=0, total_roll_adv=52, add_friend=0, total_add_friend=4, thumbs_up=0, total_thumbs_up=17, thumbs_dwn=0, total_thumbs_dwn=5)
```

After that, I took few more actions on the data set:

* To gain significance in the data, I filtered away all the users with less than a week of data;
* I created a list of the churning users and a list of the users that are staying with the service. Based on those lists I divided the original data set in two: a portion for the users that leave and another for those that don't: data from these data sets will then be compared, looking for patterns;
* I also further refined the two previous datasets, extracting a subset each, containing the last week of data for every user. The idea was to look for patterns of different behaviour in the churning users, as they approach the moment they leave.



### _Modeling_

### _Optimization_

---
## Conclusions 

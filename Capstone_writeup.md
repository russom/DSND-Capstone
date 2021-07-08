## Capstone Project
The goal of this project is to use [**Spark**](https://spark.apache.org/) to analize the log files collected from a fictitious music streaming service called "Sparkify" and identify a strategy to predict "churn", i.e. the event of a user cancelling the subscription with the service.

---
## Data
The data for this project was provided by Udacity in JSON format, in two differen sizes:

* A _Limited_ dataset (~128 MB, more than 280000 rows), to be used for analysis on a local machine. This is what I use in the [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb) notebook; the actual dataset can be downloaded from [here](https://drive.google.com/file/d/1gX1X-D8G4vE29AAUeQHapv5P_vNs6Jcv/view?usp=sharing).
* A _Complete_ dataset (~12 GB, more than 26 Mil rows), to be loaded on a cluster. This is what I explore in the [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) notebook: it is stored in an [AWS S3](https://aws.amazon.com/s3/) bucket available at `s3n://udacity-dsnd/sparkify/sparkify_event_data.json`.

## Solution Strategy and Approach
The way I tried to solve this problem was to build a classifier to predict, based on the provided data, whether or not a user would churn. I used the tools provided by [Spark](https://spark.apache.org/docs/latest/ml-classification-regression.html), training the classifier on a portion of the data, and testing it on the remaining part.

Before actually introducing the classifier I went through an extensive data exploration phase that led me to the identification of a subset of significant features that could be effective in identifying users that leave.  

After that I could actually move into the modeling phase. I approached that in two steps:

* I initially trained and compared the results of a few of the classifiers available in Spark, using their default parameters, in order to identify those with the better behaviour against the analyzed dataset;
* Afterwards I moved on with an optimization phase in which I could provide a grid of options for some of the parameters and verify if/how changing them could lead to better results.

---
## Content of the notebooks
Both the notebooks provided present the same table of contents; at a high level we have the following sections:

1. Load Libraries
2. [Load and Clean Dataset](#load-and-clean-dataset)
3. [Data Exploration](#data-exploration)
4. [Feature Engineering](#feature-engineering)
5. [Modeling](#modeling)
6. [Optimization and Validation](#optimization-and-Validation)

In the following we'll see details on all of them (except for the first one). I will mostly make reference to the `local` notebook, clarifying when I show results from the `EMR` one as I go.

Finally, a [Reults and Conclusions](#Results-and-Conclusions) section will summarize the findings and introduce possible improvement strategies.

### Load and Clean Dataset
This part is fairly similar for both the local and EMR cases; the first operation is to load the JSON file:

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
>```Row(artist='Martha Tilston', auth='Logged In', firstName='Colin', gender='M', itemInSession=50, lastName='Freeman', length=277.89016, level='paid', location='Bakersfield, CA', method='PUT', page='NextSong', registration=1538173362000, sessionId=29, song='Rockpools', status=200, ts=1538352117000, userAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0', userId='30')```

It's also possible to check the number of rows and columns in the dataset. Here, of course, we could see the difference between the limited dataset and the full one:

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

* Any `NaN` eventually present in the `sessionId` or `userId` fields: this could have been the consequence of errors or bugs in the logging system;
* Any `Nan` eventually present in the `gender` or `location` fields: I use these in part of the exploration phase, to look at demographics;
* Any empty `userId` field still remaining: this would be most likely associated with events like the very first interaction of the users with the system.

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

### Data Exploration
Looking at the dataset schema, a column seeming to provide quite a bit of useful information is `page`, that documents the various pages visited by the users:

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

Based on the information available in this column, we can define new variables identifying, for example, an actual churn (looking at when the users visits `Cancellation Confirmation`) or an `Upgrade`/`Downgrade`, but also events like the user giving a Thumbs Up or adding friends, or seeing a Rolling Advert.  
It would also be possible to reconstruct the time spent by the users with the system, making reference to the `registration` and `ts` columns.

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

Once introduced all the columns above we can take a look at the data:

```
  # Check columns
  df_user_log_valid.head()
```
>```Row(artist='Sleeping With Sirens', auth='Logged In', firstName='Darianna', gender='F', itemInSession=0, lastName='Carpenter', length=202.97098, level='free', location='Bridgeport-Stamford-Norwalk, CT', method='PUT', page='NextSong', registration=1538016340.0, sessionId=31, song='Captain Tyin Knots VS Mr Walkway (No Way)', status=200, ts=1539003534.0, userAgent='"Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53"', userId='100010', churn=0, sub_dwg=0, sub_upg=0, first_ts=1539003534.0, last_ts=1542823952.0, perm_days=56.0, data_days=44.0, roll_adv=0, total_roll_adv=52, add_friend=0, total_add_friend=4, thumbs_up=0, total_thumbs_up=17, thumbs_dwn=0, total_thumbs_dwn=5)```

After that, I took few more actions on the dataset:

* To gain significance in the data, I filtered away all the users with less than a week of data;
* I created a list of the churning users and a list of the users that are staying with the service. Based on those lists I divided the original dataset in two: a portion for the users that leave and another for those that don't. Data from these datasets will then be compared, looking for patterns;
* I also further refined the two previous datasets, extracting a subset from each, containing the last week of data for every user. The idea was to look for patterns of different behaviour in the churning users, as they approach the moment they leave.

Once done all of that, it became possible to compare the dataset including the users that left and the one with the users that stay.  
Both the [`Sparkify-project-local`](./notebooks/Sparkify-project-local.ipynb) and [`Sparkify-project-EMR`](./notebooks/Sparkify-project-EMR.ipynb) notebooks show details of these comparisons for different variables: here in the follow I will show some pictures and statistics relative to some of the more interesting features. I will make reference here to the **Global** dataset (hence the `EMR` notebook). 

#### _Time spent by the Users with the Service_

<p align="center">
  <img alt="Time Spent by Users" src="./pictures/Time-Spent-by-Users.png">
</p>

```
------------------------------------------------
Time spent statistics for users that cancelled:
Mean =  69.69 ; Std. Dev. =  40.74
------------------------------------------------
Time spent statistics for users that stay:
Mean =  86.45 ; Std. Dev. =  39.59
------------------------------------------------
```

#### _Songs listened per day_

<p align="center">
  <img alt="Songs Listened per Day" src="./pictures/Songs-Listened-per-Day.png">
</p>

```
---------------------------------------------------
Songs per day statistics for users that cancelled:
Mean =  33.40 ; Std. Dev. =  26.71
---------------------------------------------------
Songs per day statistics for users that stay:
Mean =  20.21 ; Std. Dev. =  19.17
---------------------------------------------------
```

#### _Friends added per day_

<p align="center">
  <img alt="Friends Added per Day" src="./pictures/Added-Friends-per-Day.png">
</p>

```
---------------------------------------------------------
Added friend per day statistics for users that cancelled:
Mean =  0.68 ; Std. Dev. =  0.61
---------------------------------------------------------
Added friend per day statistics for users that stay:
Mean =  0.41 ; Std. Dev. =  0.44
---------------------------------------------------------
```

#### _Thumbs Down given per day_

<p align="center">
  <img alt="Thumbs Down Given per Day" src="./pictures/Thumbs-Down-per-Day.png">
</p>

```
--------------------------------------------------------------
Thumbs down given per day statistics for users that cancelled:
Mean =  0.48 ; Std. Dev. =  0.43
--------------------------------------------------------------
Thumbs down per day statistics for users that stay:
Mean =  0.27 ; Std. Dev. =  0.29
--------------------------------------------------------------
```

#### _Rolled Advert per day_

<p align="center">
  <img alt="Rolled Adverts per Day" src="./pictures/Rolled-Adverts-per-Day.png">
</p>

```
----------------------------------------------------------
Rolled adverts per day statistics for users that cancelled:
Mean =  0.92 ; Std. Dev. =  1.13
----------------------------------------------------------
Rolled adverts per day statistics for users that stay:
Mean =  0.46 ; Std. Dev. =  0.64
----------------------------------------------------------
```

Beyond the behavioural quantities I also took a look at some demographic indicators: the gender of the subscribers and their location (expressed in terms of State).

#### _Gender of the Users_

```
-----------------------------------------------------------------------------
Gender distribution for users that cancelled:
Number of male users =  2123
Number of female users =  1848
Number of male users/Total Users =  0.53
Number of female users/Total Users =  0.47
-----------------------------------------------------------------------------
Gender distribution for users that stay:
Number of male users =  10641
Number of female users =  9662
Number of male users/Total Users =  0.52
Number of female users/Total Users =  0.48
-----------------------------------------------------------------------------
```

#### _Location of the Users_

<p align="center">
  <img alt="Location distribution for Users that cancel" src="./pictures/Location-cancelling.png">
</p>

<p align="center">
  <img alt="Location distribution for Users that stay" src="./pictures/Location-staying.png">
</p>

### Feature Engineering
Based on the data analysis completed in the previous section, I decided to consider as training features to be used for the modeling phase:

* The number of rolled adverts/day
* The number of friends added/day
* The number of thumbs down given/day
* The number of songs listened/day
* The time spent with the service

The label will be the actual churning event.

I couldn't see any evidence of a significant difference in the behaviour of the users in the last week before churning vs. the behaviour before, so I resolved to consider their full history. Analogously, I couldn't see a meaningful difference between the groups in terms of gender or location, so I ended up not including demographics information.

All the features are grouped by userId. An example of the dataset format after the feature engineering phase is:

```
  # Check the data
  df_user_logs_mod.head()
```
>```Row(id='100010', rolledAdvDay=1.1818181818181819, addedFriendDay=0.09090909090909091, thumbsDwnDay=0.022727272727272728, songsDay=6.113636363636363, permanence=56.0, label=0)```

### Modeling
In this section, I compared a few of the classifiers available in [Spark](https://spark.apache.org/docs/latest/ml-classification-regression.html), considering, for all of them, their reference parameters (i.e., I did not run any grid optimization here). I chose:

* A [Logistic Regression](https://spark.apache.org/docs/latest/ml-classification-regression.html#logistic-regression) classifier;
* A [Gradient Boosted Tree](https://spark.apache.org/docs/latest/ml-classification-regression.html#gradient-boosted-tree-classifier) classifier;
* A [Random Forest](https://spark.apache.org/docs/latest/ml-classification-regression.html#random-forest-classifier) classifier;
* A [Linear Support Vector](https://spark.apache.org/docs/latest/ml-classification-regression.html#linear-support-vector-machine) classifier.

In terms of phases:

* The first thing was splitting the dataset in train and testing portions (note: fixing the seed here ensures repeatability of the experiment):

```
  # 80/20 % split
  train, test = df_user_logs_mod.randomSplit([0.8, 0.2], seed=42)
```

* Then I defined a [VectorAssembler](https://spark.apache.org/docs/latest/ml-features#vectorassembler) to combine all the features of interest in a single vector:

```
  # Define VectorAssembler
  assembler = VectorAssembler(inputCols=["rolledAdvDay",\
                                       "addedFriendDay",\
                                       "thumbsDwnDay",\
                                       "songsDay",\
                                       "permanence"], \
                            outputCol="inputFeatures")
```

* I then scaled the data using a [Min-Max Scaler](https://spark.apache.org/docs/latest/ml-features#minmaxscaler). I opted for this given that the distributions of the various features (as seen in the data exploration section) are quite skewed and far from resembling the normal one.

```
  # Define Scaler
  scaler = MinMaxScaler(inputCol="inputFeatures", outputCol="features")
```

* After that, I could introduce 4 [pipelines](https://spark.apache.org/docs/latest/ml-pipeline.html), one for each of the classifiers:

```
  # Classifiers/Pipelines

  # Logistic Regression 
  lr = LogisticRegression()
  pipeline_lr = Pipeline(stages = [assembler, scaler, lr])

  # Gradient-Boosted Tree classifier
  gbt = GBTClassifier()
  pipeline_gbt = Pipeline(stages = [assembler, scaler, gbt])

  # Random Forest classifier
  # Note: setting the seed will ensure repeatability of the results
  rf = RandomForestClassifier(seed = 42)
  pipeline_rf = Pipeline(stages = [assembler, scaler, rf])

  # Linear Support Vector Machine classifier
  lsvc = LinearSVC()
  pipeline_svc = Pipeline(stages = [assembler, scaler, lsvc])
```

* Finally, I opted for a validator using the f1-score metric, given the [imbalance in the data](https://stats.stackexchange.com/questions/210700/how-to-choose-between-roc-auc-and-f1-score) (there are quite more users that stay that users that leave):

```
  # Evaluator - will be common for all the grids
  evaluator = MulticlassClassificationEvaluator(metricName="f1")
```

After that, I proceeded in fitting and evaluating the four classifiers.  
In all cases I used a [CrossValidator](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.tuning.CrossValidator.html), folding the dataset with `k = 3`, so to verify robustness of the trained classifier with respect to the training data. As an example, for the Logistic Regression model I had:

```
# Empty parameter grid
paramgrid_lr = ParamGridBuilder()\
    .build()

# Crossvalidator 
crossval_lr = CrossValidator(estimator = pipeline_lr, \
                             estimatorParamMaps = paramgrid_lr, \
                             evaluator = evaluator, \
                             numFolds = 3, \
                             seed = 4242)
```
**NOTE:** In the above lines (like elsewhere) fixing the seed ensures repeatability of the experiment.

Looking at the results, one of the most interesting things, I believe, is the difference between the Limited and Complete dataset.

_Limited Dataset_
```
F1-score, Logistic Regression classifier:  0.8828
```
```
F1-score, Gradient-Boosted Tree classifier:  0.8190
```
```
F1-score, Random Forest classifier:  0.8095
```
```
F1-score, Linear Support Vector Machine classifier:  0.8302
```

_Complete Dataset_
```
F1-score, Logistic Regression classifier:  0.8344
```
```
F1-score, Gradient-Boosted Tree classifier:  0.8858
```
```
F1-score, Random Forest classifier:  0.8798
```
```
F1-score, Linear Support Vector Machine classifier:  0.8236
```

**NOTE:**  
In proceeding with the fitting on the EMR cluster, I often received an exception similar to this:

<p align="center">
  <img alt="Spark EMR Exception" src="./pictures/Spark-EMR-Exception.png">
</p>

This was not always predictable or repeatable: the exception would generally happen during this phase, but not necessarily always at the same cell. Also, the body of the message might change slighlty, with `KeyError` making reference to different values. At any rate, the execution of the code could proceed after that, with no other noticeable effect.  
I found [this](https://stackoverflow.com/questions/58910023/keyerror-when-training-a-model-with-pyspark-ml-on-aws-emr-with-data-from-s3-buck) post on StackOverflow, describing a similar issue and advancing th hypothesis that the exception might in fact be related just to the Spark progress bar normally shown. However, I couldn't gather any further insight.

### Optimization and Validation
Once fitted the classifiers with the default parameters, I proceeded with an optimization for the Gradient Boosted Tree and Random Forest cases (i.e. the classifiers with the better f1-score against the complete dataset).  
Looking for a compromise between what could have been influential parameters to change and computational load, I defined the following grids:

```
  # Gradient Boosted Tree 
  # Parameter grid
  paramgrid_gbt_o = ParamGridBuilder()\
      .addGrid(gbt.stepSize, [0.1, 0.25, 0.5])\
     .addGrid(gbt.maxIter, [20, 40, 60])\
     .build()
```
```
  # Random Forest
  # Parameter grid
  paramgrid_rf_o = ParamGridBuilder()\
      .addGrid(rf.impurity, ['entropy', 'gini'])\
     .addGrid(rf.maxDepth, [5, 10])\
     .addGrid(rf.numTrees, [20, 40])\
     .build()
```
**NOTE:** In the above grids the first value for each parameter is the default.

In both cases I obtained some improvement in the score:

_Limited Dataset_
```
F1-score, Gradient-Boosted Tree classifier:  0.8401
```
```
F1-score, Random Forest classifier:  0.8302
```

_Complete Dataset_
```
F1-score, Gradient-Boosted Tree classifier:  0.8858
```
```
F1-score, Random Forest classifier:  0.8850
```

It is interesting to evaluate how much the parameters were changed with respect to the default.  
Looking at the Complete dataset cases (i.e. those with better scores), we can see that the Gradient-Boosted Tree classifier, even though still the best one, actually remained with the default parameters (see the [notebook](./notebooks/sparkify-project-EMR.ipynb) for details), while for the Random Forest case we have:

```
  bestRFPipeline = cvModel_rf_o.bestModel
  bestRFModel = bestRFPipeline.stages[2]
  bestRFParams = bestRFModel.extractParamMap()
  bestRFParams
```
>```{Param(parent='RandomForestClassifier_7b20e34536a7', name='cacheNodeIds', doc='If false, the algorithm will pass trees to executors to match instances with nodes. If true, the algorithm will cache node IDs for each instance. Caching can speed up training of deeper trees.'): False, Param(parent='RandomForestClassifier_7b20e34536a7', name='checkpointInterval', doc='set checkpoint interval (>= 1) or disable checkpoint (-1). E.g. 10 means that the cache will get checkpointed every 10 iterations. Note: this setting will be ignored if the checkpoint directory is not set in the SparkContext'): 10, Param(parent='RandomForestClassifier_7b20e34536a7', name='featureSubsetStrategy', doc='The number of features to consider for splits at each tree node. Supported options: auto, all, onethird, sqrt, log2, (0.0-1.0], [1-n].'): 'auto', Param(parent='RandomForestClassifier_7b20e34536a7', name='featuresCol', doc='features column name'): 'features', Param(parent='RandomForestClassifier_7b20e34536a7', name='impurity', doc='Criterion used for information gain calculation (case-insensitive). Supported options: entropy, gini'): 'entropy', Param(parent='RandomForestClassifier_7b20e34536a7', name='labelCol', doc='label column name'): 'label', Param(parent='RandomForestClassifier_7b20e34536a7', name='maxBins', doc='Max number of bins for discretizing continuous features.  Must be at least 2 and at least number of categories for any categorical feature.'): 32, Param(parent='RandomForestClassifier_7b20e34536a7', name='maxDepth', doc='Maximum depth of the tree. (Nonnegative) E.g., depth 0 means 1 leaf node; depth 1 means 1 internal node + 2 leaf nodes.'): 10, Param(parent='RandomForestClassifier_7b20e34536a7', name='maxMemoryInMB', doc='Maximum memory in MB allocated to histogram aggregation.'): 256, Param(parent='RandomForestClassifier_7b20e34536a7', name='minInfoGain', doc='Minimum information gain for a split to be considered at a tree node.'): 0.0, Param(parent='RandomForestClassifier_7b20e34536a7', name='minInstancesPerNode', doc='Minimum number of instances each child must have after split.  If a split causes the left or right child to have fewer than minInstancesPerNode, the split will be discarded as invalid. Must be at least 1.'): 1, Param(parent='RandomForestClassifier_7b20e34536a7', name='numTrees', doc='Number of trees to train (at least 1)'): 40, Param(parent='RandomForestClassifier_7b20e34536a7', name='predictionCol', doc='prediction column name'): 'prediction', Param(parent='RandomForestClassifier_7b20e34536a7', name='probabilityCol', doc='Column name for predicted class conditional probabilities. Note: Not all models output well-calibrated probability estimates! These probabilities should be treated as confidences, not precise probabilities'): 'probability', Param(parent='RandomForestClassifier_7b20e34536a7', name='rawPredictionCol', doc='raw prediction (a.k.a. confidence) column name'): 'rawPrediction', Param(parent='RandomForestClassifier_7b20e34536a7', name='seed', doc='random seed'): 42, Param(parent='RandomForestClassifier_7b20e34536a7', name='subsamplingRate', doc='Fraction of the training data used for learning each decision tree, in range (0, 1].'): 1.0}```

Or, with a bit of better formatting:

```
name='impurity', doc='Criterion used for information gain calculation (case-insensitive). Supported options: entropy, gini'): 'entropy'
name='maxDepth', doc='Maximum depth of the tree. (Nonnegative) E.g., depth 0 means 1 leaf node; depth 1 means 1 internal node + 2 leaf nodes.'): 10
name='numTrees', doc='Number of trees to train (at least 1)'): 40
```

So we can see how the affecting parameters seem to be `maxDepth` and `numTrees`, that moved to the max provided. Of course this sort of evaluation is always a trade-off: increasing any of them even further _could_ improve the score but would for sure be more computationally onerous.

With an optimal combination of parameters identified for the best model, we can also compare how/if the f1-score changes for each folds that the `CrossValidator` has defined. As mentioned previously, stability in the metric would be an indication of robustness of the classifier with respect to the training data.

Here too we can see the difference between the datasets:

_Limited Dataset_
```
Fold:  0 ; F1-score, Gradient-Boosted Tree classifier:  0.8613
Fold:  1 ; F1-score, Gradient-Boosted Tree classifier:  0.7891
Fold:  2 ; F1-score, Gradient-Boosted Tree classifier:  0.7523
```

```
Fold:  0 ; F1-score, Random Forest classifier:  0.8571
Fold:  1 ; F1-score, Random Forest classifier:  0.7523
Fold:  2 ; F1-score, Random Forest classifier:  0.7944
```

_Complete Dataset_
```
Fold:  0 ; F1-score, Gradient-Boosted Tree classifier:  0.8854
Fold:  1 ; F1-score, Gradient-Boosted Tree classifier:  0.8847
Fold:  2 ; F1-score, Gradient-Boosted Tree classifier:  0.8834
```

```
Fold:  0 ; F1-score, Random Forest classifier:  0.8771
Fold:  1 ; F1-score, Random Forest classifier:  0.8798
Fold:  2 ; F1-score, Random Forest classifier:  0.8823
```

It is clearly noticeable how the richer dataset provides a much better training, leading to pretty much stable metrics for both the classifiers.

---
## Results and Conclusions 
With this  project I demonstrated the possibility to train a classifier to predict, based on available information, whether or not a user of the "Sparkify" service will "churn" with a level of performance measured by an **f1-score > 0.8**.

Specifically, I could compare and contrast several classifiers, both against a Limited (~128 MB, more than 280000 rows) and a Complete (~12 GB, more than 26 Mil rows) dataset.  
The reference metric was the f1-score, given an imbalance in the data that presented much more users staying that leaving, and the best scoring classifier has been the **Gradient Boosted Tree** that, against the Complete dataset could achieve a final **f1-score of ~0.886**.  
This classifiers not only outperformed the others (including, even if slightly, the Random Forest one) but also provided robust results, with a metric that didn't change much when evaluated with a k-fold cross-validator.  
Furthermore, I ran a grid optimization process on the classifier, that  didn't produce changes with respect to the default parameters. It should be noted, however, that the grid was defined as a compromise between size of the exploration space and computational burden, so it was not intended to be exhaustive.

There are a few things that I found particularly interesting in going through the experience:

* First of all, the general saying that the majority of the time in Data Science is spent doing data exploration and feature engineering is absolutely true. I would say that at least 75% of the time I spent on the project went into these two phases, and it probably could have been more.
* The actual modeling phase highlighted the differences, and added value, of the Complete data set vs. the Limited one. Indeed, while in fitting against the Limited data some classifiers (Logistic Regression and SVC) were scoring higher f1 than the others, the positions switched when evaluating against the Complete dataset. In that case, ensemble techniques like Gradient Boosted Tree and Random Forest scored better both in relative and absolute sense, as it could probably have been expected.
* The results could be improved even further through a grid optimization phase that changed, for example, the results for the Random Forest classifier against the Complete dataset, passing from an f1-score of 0.8798 to one of 0.8850. In general, exploring the parameters' space for the classifiers to get an even better score would definitely be a possible option for further improvements.
* The difference between the datasets played an even bigger role when running a k-fold cross-validation analysis: in this case the limited dataset clearly showed less stable metrics, hence the classifiers were not particularly robust with respect to the data.

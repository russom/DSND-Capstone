from pyspark.sql import SparkSession

if __name__ == "__main__":
    '''
        example progrem
    '''

    spark = SparkSession\
        .builder\
        .appName("LowerSongTitles")\
        .getOrCreate()

    log_of_songs = [
        "Despacito",
        "Eclipse of the Heart",
        "Nu Gins e Na' Magliett",
        "O'Zappator",
        "despacito",
        "Sara' perche' ti schifo",
    ]

    distributed_song_log = spark.sparkContext.parallelize(log_of_songs)

    print('*******************************')
    print(distributed_song_log.map(lambda song: song.lower()).collect() )
    print('*******************************')
    spark.stop()


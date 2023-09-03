# -*- coding: utf-8 -*-

"""
Item-based collaborative filtering is used to recommend items to users.
The method predicts ratings of items based of historical ratings of users.
"""

# Author: Sergei Usovik <usovik@bmstu.ru>

from pyspark import Row, RDD
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.window import Window


class ItemBasedRecommend:
    """
    Main class that implements the item-based collaborative filtering.

    The approach includes:
    - cosine similarity calculation between items
    - weighted sum calculation for rating prediction

    Parameters
    ----------
    top_N_similarities : int, optional (default=20)
        Number of top similarities for a given item pair that will compose
        a similarity matrix. It is used in the train phase
    top_N_ratings : int, optional (default=10)
        Number of top ratings that return as a result of prediction for a
        given user

    Attributes
    ----------
    spark : SparkSession
    top_N_similarities : int
    top_N_ratings : int
    df_train : DataFrame
        Ratings of users in the following format: [usedId, movieId, rating]
    br_similarity : Broadcast
        Dictionary of similarities of item pairs
    br_P : Broadcast
        Set of items that contains df_train
    br_U : Broadcast
        Set of users  that contains df_train

    """
    def __init__(self, spark, top_N_similarities=20, top_N_ratings=None):
        self.spark = spark
        self.top_N_similarities = int(top_N_similarities)
        self.top_N_ratings = int(top_N_ratings) if top_N_ratings else None

    def train(self, df_train, top_N=None, user_column_name="user", item_column_name="item",
              rating_column_name="rating"):
        """
        Calculate cosine similarities between all item pairs

        Parameters
        ----------
        df_train : DataFrame
            Ratings of users in the following format: [usedId, movieId, rating]
        top_N : int or None
            Number of top similarities for a given item pair that will compose
            a similarity matrix. It is used in the train phase
        rating_column_name : str
        user_column_name : str
        item_column_name : str

        Returns
        -------
        self
        """
        top_N = int(top_N) if top_N else self.top_N_similarities
        user_column_name = str(user_column_name)
        item_column_name = str(item_column_name)
        rating_column_name = str(rating_column_name)

        clmn_names = [F.col(user_column_name).alias("user"),
                      F.col(item_column_name).alias("item"),
                      F.col(rating_column_name).alias("rating")]

        df_train = df_train.select(clmn_names)

        left_clmn_names = [F.col("user").alias("u"),
                   F.col("item").alias("p1"),
                   F.col("rating").alias("v1")]

        right_clmn_names = [F.col("user").alias("u"),
                    F.col("item").alias("p2"),
                    F.col("rating").alias("v2")]
        
        # Step 1. Create dot products
        
        df_dot = df_train.select(left_clmn_names)\
            .join(df_train.select(right_clmn_names), on="u")\
            .where(F.col("p1") < F.col("p2"))\
            .groupBy([F.col("p1"), F.col("p2")])\
            .agg(F.sum(F.col("v1") * F.col("v2")).alias("dot"))

        # Step 2. Calculate norms
        
        df_norm = df_train.select(left_clmn_names)\
            .groupBy(F.col("p1"))\
            .agg(F.sqrt(F.sum(F.col("v1") * F.col("v1"))).alias("norm"))

        similarity_clmns = [F.col("p1"), F.col("p2"), (F.col("dot")/F.col("n1")/F.col("n2")).alias("sim")]
        
        # Step 3. Calculate similarities
        
        df_similarity = df_dot.join(df_norm.select(F.col("p1"), F.col("norm").alias("n1")), on="p1")\
                    .join(df_norm.select(F.col("p1").alias("p2"), F.col("norm").alias("n2")), on="p2")\
                    .select(similarity_clmns)
        
        # Step 4. Truncate similarities

        window = Window.partitionBy(df_similarity["p1"]).orderBy(df_similarity["sim"].desc())
        df_similarity_N = df_similarity.select("*", F.rank().over(window).alias("rank"))\
                    .filter(F.col("rank") <= top_N)
        
        # Step 5. Collect data (similarities, users, products) on driver
        
        df_similarity_pn = df_similarity_N.toPandas()
        dict_similarity = df_similarity_pn.set_index(["p1", "p2"]).to_dict()["sim"]
        
        P = {el["item"] for el in df_train[[F.col("item")]].distinct().collect()}
        U = {el["user"] for el in df_train[[F.col("user")]].distinct().collect()}
        
        # Step 6. Broadcast data

        self.br_similarity = self.spark.sparkContext.broadcast(dict_similarity)
        self.br_P = self.spark.sparkContext.broadcast(P)
        self.br_U = self.spark.sparkContext.broadcast(U)
        
        self.top_N_similarities = top_N

        self.df_train = df_train.persist()

        return self
        
    def predict(self, user_id, item_id):
        """Predict rating for a given user and item"""
        raise Exception("Not implemented.")
    
    def recommend(self, user_ids, top_N_ratings=None, partition_num=20, grouped=True):
        """
        Recommend top N items to given users.

        Note: Returns non-zero evaluated (predicted) ratings

        Parameters
        ----------
        user_ids : list or set
            List of users for which we want to get recommendations
        top_N_ratings : int
            Number of top ratings that return as a result of prediction for a
            given user
        partition_num : int
            Number of partitions (tasks) to use to calculate predictions
        grouped : boolean
            If True then the method returns value will be a RDD with the following
            format:
                [(used_id : [(movieId, evaluated rating),.. ]),.. ]
            Otherwise a result will be DataFrame with the following format:
                [userId, movieId, evaluated ratings]
        Returns
        -------
        RDD or DataFrame
        """

        top_N_ratings = int(top_N_ratings) if top_N_ratings else self.top_N_ratings

        if not hasattr(self, "df_train"):
            raise Exception("It seems you haven't trained the model.")

        # Remove reference to the current class instance
        _predict_per_partition = ItemBasedRecommend._predict_per_partition
        br_similarity = self.br_similarity
        br_P = self.br_P

        # Predict ratings through the chain of transformations
        rdd_ratings_pred = self.df_train.where(F.col("user").isin(user_ids))\
                .repartition(partition_num, F.col("user"))\
                .sortWithinPartitions(F.col("user")).rdd\
                .mapPartitions(_predict_per_partition(br_similarity, br_P, top_N_ratings, grouped))
        
        return rdd_ratings_pred if grouped else rdd_ratings_pred.toDF()

    @staticmethod
    def _predict_per_partition(br_similarity, br_P, top_N_ratings, grouped):
        """Wrapper for prediction of ratings per partition"""

        def _predict(p_i, PR_u):
            """Predict a rating for a given user and item"""
            wsum_num = 0.0
            wsum_den = 0.0

            for p_j_r, r_j_r in PR_u.items():
                if p_j_r > p_i and (p_i, p_j_r) in br_similarity.value:
                    sim = br_similarity.value[(p_i, p_j_r)]
                    wsum_num += sim * r_j_r
                    wsum_den += sim
                elif p_j_r < p_i and (p_j_r, p_i) in br_similarity.value:
                    sim = br_similarity.value[(p_j_r, p_i)]
                    wsum_num += sim * r_j_r
                    wsum_den += sim

            return wsum_num/wsum_den if wsum_den > 0 else 0.0
        
        def _predict_per_user(PR_u):
            """
            Predict ratings for a given user

            Parameters
            ----------
            PR_u : list or set
                List of tuple (item, rating), where items are those to which the user has set ratings

            Returns
            -------
                List of evaluated ratings

            """
            result = list()
            for p_i in br_P.value:
                if p_i not in PR_u:
                    pred = _predict(p_i, PR_u)
                    if pred > 0:
                        result.append((p_i, pred))
            return result
        
        def _predict_per_partition_inner_grouped(ratings):
            """
            Predict per partition if grouped option is enabled

            Returns
            -------
            RDD
            """
            prev_user = None
            curr_user = None
            for r in ratings:
                curr_user = r["user"]
                if prev_user == curr_user:
                    PR_u[r["item"]] = r["rating"]
                else:
                    if prev_user:
                        yield prev_user, sorted(_predict_per_user(PR_u), key=lambda x: -x[1])[:top_N_ratings]
                    PR_u = dict()
                    PR_u[r["item"]] = r["rating"]
                    prev_user = curr_user
            # Emit values of the last user in the partition
            if curr_user and curr_user == prev_user:
                yield prev_user, sorted(_predict_per_user(PR_u), key=lambda x: -x[1])[:top_N_ratings]

        def _predict_per_partition_inner(ratings):
            """
            Predict per partition if grouped option is disabled

            Returns
            -------
            DataFrame
            """
            prev_user = None
            curr_user = None
            for r in ratings:
                curr_user = r["user"]
                if prev_user == curr_user:
                    PR_u[r["item"]] = r["rating"]
                else:
                    if prev_user:
                        for el in sorted(_predict_per_user(PR_u), key=lambda x: -x[1])[:top_N_ratings]:
                            yield Row(user=prev_user, item=el[0], rating_pred=el[1])
                    PR_u = dict()
                    PR_u[r["item"]] = r["rating"]
                    prev_user = curr_user
            # Emit values of the last user in the partition
            if curr_user and curr_user == prev_user:
                for el in sorted(_predict_per_user(PR_u), key=lambda x: -x[1])[:top_N_ratings]:
                    yield Row(user=prev_user, item=el[0], rating_pred=el[1])
        
        if grouped:
            return _predict_per_partition_inner_grouped
        
        return _predict_per_partition_inner

    def save(self):
        """Save similarities or ratings in external storage"""
        raise Exception("Not implemented.")
    
    def evaluate(self):
        raise Exception("Not implemented.")

    def recommend_and_show(self, num_rows_to_display=None, **kwargs):
        """
        Launch the action operation to calculate recommendations, collect data
        on the driver and display them.
        """
        if num_rows_to_display:
            num_rows_to_display = int(num_rows_to_display)

        result = self.recommend(**kwargs)

        if isinstance(result, RDD):
            return result.take(num_rows_to_display) if num_rows_to_display else result.collect()
        elif isinstance(result, DataFrame):
            return result.show(num_rows_to_display) if num_rows_to_display else result.show()


def _test():

    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .master("local[4]") \
        .appName("itemBasedRecommendationTest") \
        .getOrCreate()

    Rating = Row("user", "item", "rating")

    data = [[1, 1, 5], [1, 2, 4], [1, 3, 2],
            [2, 1, 5], [2, 2, 5], [2, 3, 2],
            [3, 1, 2], [3, 2, 2], [3, 3, 5]]

    rdd_data = spark.sparkContext.parallelize(data, 2)
    df_rating_true = rdd_data.map(lambda x: Rating(x[0], x[1], x[2])).toDF()
    
    df_train, df_test = df_rating_true.randomSplit([0.8, 0.2], seed=7)
    df_train.persist(); df_test.persist()

    print("Loading data...")
    df_train.show()

    model = ItemBasedRecommend(spark)

    print("Training...")
    model.train(df_train)
    print("Finished")

    print("Recommending...")
    model.recommend_and_show(user_ids=model.br_U.value, grouped=False)

    spark.stop()


if __name__ == "__main__":
    _test()

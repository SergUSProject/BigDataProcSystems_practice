package edu.classes.spark;

import com.google.gson.Gson;
import org.apache.http.util.TextUtils;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.function.FlatMapFunction;

//import org.apache.spark.sql.SparkSession;
import scala.Tuple2;

import java.io.Serializable;
import java.util.*;


public class WordCountReviewDriver {

    private static final String APP_NAME = "WordCountReviewJavaApp";
    private static final String DEFAULT_MASTER = "local[1]";
    private static final String SEPARATOR = " ";


    // Convert Json to Review class using GSON

    // OPTION 2

    /**
     * Implementation of the FlatMapFunction interface for the mapPartitions() methods
     * to deserialize json records.
     *
     */
    public static final class ReviewConverterPartitionFunction implements FlatMapFunction<Iterator<String>, Review> {

        /**
         * Convert records of a partition to the Review class
         *
         * @param records   records of a partition
         * @return          records of the Review class
         * @throws Exception
         */
        @Override
        public Iterator<Review> call(Iterator<String> records) throws Exception {

            Gson gson = new Gson();
            List<Review> reviews = new ArrayList<>();

            // Iterate over records of a RDD partition
            while (records.hasNext()) {
                String record = records.next();
                Review review = gson.fromJson(record, Review.class);
                reviews.add(review);
            }

            return reviews.iterator();
        }
    }


    // OPTION 3

    /**
     * Custom serializable class for json deserialization
     *
     */
    public static final class ReviewConverterRDD implements Serializable {

        private transient Gson gson;

        /**
         * Get/create a Gson instance
         *
         * Note: If the variable is not initialized on an executor, the instance will be created.
         * Otherwise the method returns the existing Gson instance.
         *
         * @return  a Gson instance
         */
        private Gson getGsonInstance() {
            if (gson == null) gson = new Gson();
            return gson;
        }

        /**
         * Transform RDD from RDD<String> to RDD<Review>
         *
         * @param rdd   an input rdd with records of the String type
         * @return      a rdd of the Review type
         */
        public JavaRDD<Review> fromJson(JavaRDD<String> rdd) {
            return rdd.map(record -> getGsonInstance().fromJson(record, Review.class));
        }
    }


    /**
     * Extract words from text string
     *
     * @param review    a review instance
     * @return          an iterator over extracted words
     */
    private static Iterator<String> extractWords(Review review) {
        if (review == null || TextUtils.isEmpty(review.getReview())) return Collections.emptyIterator();
        return Arrays.asList(review.getReview().split(SEPARATOR)).iterator();
    }

    public static void main(String[] args) {

        /*
        Create Spark Context

        1) JavaSparkContext (spark-core)
        2) Using SparkSession (spark-sql)

        Note: To run an application in IDE:

            1) add the local master configuration. Don't forget to remove this
            setting when package to jar, otherwise spark-submit will run the
            application using the local mode even if you set the master option
            to yarn;

            Examples,
                1) SparkConf conf = new SparkConf().setMaster(CONF_MASTER).setAppName(APP_NAME);
                2) SparkSession spark = SparkSession.builder()
                                            .master(CONF_MASTER)
                                            .appName(APP_NAME)
                                            .getOrCreate();

            2) comment/remove the provided scope of Spark dependencies in your
            pom file.

            Command to run the jar file:

                SPARK_MASTER=local[2] spark-submit JAR_FILE_NAME.jar INPUT_FILE OUTPUT_DIR

         */

        // Get a spark master config from the environment variable
        String sparkMaster = System.getenv().getOrDefault("SPARK_MASTER", DEFAULT_MASTER);

        // TODO: support YARN deployment mode

        // OPTION 1

        // Configuration for a Spark application
        SparkConf conf = new SparkConf()
                .setMaster(sparkMaster)
                .setAppName(APP_NAME);

        // Create a JavaSparkContext that loads settings from system properties
        JavaSparkContext sc = new JavaSparkContext(conf);

        // OPTION 2

        /*SparkSession spark = SparkSession
                .builder()
                .master(sparkMaster)
                .appName(APP_NAME)
                .getOrCreate();

        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());*/

        // Read a text file from HDFS, a local file system
        JavaRDD<String> textFileRDD = sc.textFile(args[0]);

        // Convert text records to Review objects using GSON

        // OPTION 1

        JavaRDD<Review> reviewsRDD = textFileRDD.mapPartitions(records -> {

            Gson gson = new Gson();
            List<Review> reviews = new ArrayList<>();

            // Iterate over records of a RDD partition
            while (records.hasNext()) {
                String item = records.next();
                Review review = gson.fromJson(item, Review.class);
                reviews.add(review);
            }

            return reviews.iterator();
        });

        // OPTION 2

        // JavaRDD<Review> reviewsRDD = textFileRDD.mapPartitions(new ReviewConverterPartitionFunction());

        // OPTION 3

        /*ReviewConverterRDD converter = new ReviewConverterRDD();
        JavaRDD<Review> reviewsRDD = converter.fromJson(textFileRDD);*/

        // Count words
        JavaPairRDD<String, Integer> wordCount = reviewsRDD
                .flatMap(WordCountReviewDriver::extractWords)
                .mapToPair(word -> new Tuple2<>(word, 1))
                .reduceByKey(Integer::sum);

        // Save this RDD as a text file
        wordCount.saveAsTextFile(args[1]);

        // All operations in single code line
        /*sc.textFile(args[0])
                .mapPartitions(new ReviewConverterPartitionFunction())
                .flatMap(review -> Arrays.asList(review.getReview().split(SEPARATOR)).iterator())
                .mapToPair(word -> new Tuple2<>(word, 1))
                .reduceByKey((x, y) -> x + y)
                .saveAsTextFile(args[1]);
         */
    }

}

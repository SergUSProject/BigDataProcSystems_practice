package edu.classes.mr;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;


import java.io.IOException;

public class SortedRatingMapper extends Mapper<Object, Text, RatingKeyWritable, IntWritable> {

    private final static String RATING_INTERVAL_COUNTER_GROUP = "RATING INTERVALS";

    private RatingKeyWritable outputKey = new RatingKeyWritable();
    private IntWritable one = new IntWritable(1);
    private Gson gson = new Gson();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {

        // Review variable
        Review review;

        try {
            // Assign a review instance to the variable
            review = gson.fromJson(value.toString(), Review.class);
        }
        catch (JsonParseException e) {
            // Increment counter for bad malformed json
            context.getCounter(ReviewState.WRONG_JSON).increment(1);
            return;
        }

        if (review.getProductId() == null || review.getRating() == null) {
            // Increment counter for review json with missing values
            context.getCounter(ReviewState.MISSING_VALUE).increment(1);
            return;
        }

        // Set output key
        outputKey.set(review.getProductId(), review.getRating());

        // Emit the key-value pair
        context.write(outputKey, one);

        // Increment counter for correct review json
        context.getCounter(ReviewState.CORRECT).increment(1);

    }
}

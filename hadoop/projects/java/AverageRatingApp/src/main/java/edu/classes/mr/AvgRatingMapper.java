package edu.classes.mr;


import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.io.Text;

import java.io.IOException;

public class AvgRatingMapper extends Mapper<Object, Text, Text, StatsTupleWritable> {

    private final static String RATING_INTERVAL_COUNTER_GROUP = "RATING INTERVALS";

    private Text productId = new Text();
    private StatsTupleWritable ratingTuple = new StatsTupleWritable();
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
            context.getCounter(ReviewState.INVALID_JSON).increment(1);
            return;
        }

        if (review.getProductId() == null || review.getRating() == null) {
            // Increment counter for review json with missing values
            context.getCounter(ReviewState.MISSING_VALUE).increment(1);
            return;
        }

        // Set the key of output
        productId.set(review.getProductId());

        // Set the value of output
        ratingTuple.set(review.getRating(), 1);

        // Emit the key-value pair
        context.write(productId, ratingTuple);

        // Increment counter for correct review json
        context.getCounter(ReviewState.CORRECT).increment(1);

        // Rating interval counter
        if (review.getRating() > 4.0) {
            context.getCounter(RATING_INTERVAL_COUNTER_GROUP, "5").increment(1);
        } else if (review.getRating() > 3.0 && review.getRating() <= 4.0) {
            context.getCounter(RATING_INTERVAL_COUNTER_GROUP, "3").increment(1);
        } else if (review.getRating() > 2.0 && review.getRating() <= 3.0) {
            context.getCounter(RATING_INTERVAL_COUNTER_GROUP, "3").increment(1);
        } else if (review.getRating() > 1.0 && review.getRating() <= 2.0) {
            context.getCounter(RATING_INTERVAL_COUNTER_GROUP, "2").increment(1);
        } else {
            context.getCounter(RATING_INTERVAL_COUNTER_GROUP, "1").increment(1);
        }

    }
}
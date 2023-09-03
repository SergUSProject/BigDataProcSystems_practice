package edu.classes.mr;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class SortedRatingReducer extends Reducer<RatingKeyWritable, IntWritable, RatingKeyWritable, IntWritable> {

    private String separator;
    private IntWritable outputValue = new IntWritable(0);

    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        super.setup(context);
        Configuration conf = context.getConfiguration();
        // Assign to the variable a separator of the text output format
        separator = conf.get("mapreduce.output.textoutputformat.separator");
    }

    public void reduce(RatingKeyWritable key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {

        // Set separator for composite key. It should be the same as for the text output format
        key.setSeparator(separator);

        // Set initial value that is equal to 0
        outputValue.set(0);

        /* Iterate over all values to count a number of occurrences of :
           1) sorted pair <productId, rating> : without GroupComparator
           2) <productId> : with GroupComparator
         */
        for (IntWritable v : values) {
            outputValue.set(outputValue.get() + v.get());
        }

        /*
           Emit final values
           For TextOutputFormat result.toString() will be used to write to a filesystem
         */
        context.write(key, outputValue);
    }
}
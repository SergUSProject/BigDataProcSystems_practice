package edu.classes.mr;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class AvgRatingReducer extends Reducer<Text, StatsTupleWritable, Text, StatsTupleWritable> {

    private StatsTupleWritable result = new StatsTupleWritable();

    public void reduce(Text key, Iterable<StatsTupleWritable> values, Context context)
            throws IOException, InterruptedException {

        // Accumulative sum  of ratings of the given product
        double sum = 0.0;

        // Number of ratings
        int count = 0;

        // Iterate over all tuples from all maps
        for (StatsTupleWritable val : values) {
            sum += val.getSum();
            count += val.getCount();
        }

        // Set result values
        result.set(sum, count);

        /*
           Emit final values
           For TextOutputFormat result.toString() will be used to write to a filesystem
         */
        context.write(key, result);
    }
}
package edu.classes.mr;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;


/**
 * The WordCount class provides word count example
 *
 * The Tool interface supports handling of generic command-line options.
 * For example, the number of reduces as shown below.
 *
 * To run in terminal:
 * yarn jar word-count-app.jar \
 *      -D mapreduce.job.reduces=2 \
 *      /data/yarn/reviews_Electronics_5.json \
 *      /data/yarn/output
 *.
 */
public class WordCount extends Configured implements Tool {


    /**
     * Mapper class
     *
     */
    public static class TokenizerMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

        private final static IntWritable one = new IntWritable(1);
        private Text word = new Text();

        /**
         * Called once for each key/value pair in the input split.
         *
         * @param key       a document offset
         * @param value     a text string
         * @param context   a application context
         * @throws IOException
         * @throws InterruptedException
         */
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            // Split a string to words
            StringTokenizer itr = new StringTokenizer(value.toString());

            // Iterate over the words
            while (itr.hasMoreTokens()) {
                // Set the word to serializable class
                word.set(itr.nextToken());
                // Emmit the key-value pair: (word, 1)
                context.write(word, one);
            }
        }
    }


    /**
     * Combiner/Reducer class
     *
     */
    public static class IntSumReducer extends Reducer<Text,IntWritable,Text,IntWritable> {

        private IntWritable result = new IntWritable();

        public void reduce(Text key, Iterable<IntWritable> values, Context context)
                throws IOException, InterruptedException {

            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }
            result.set(sum);
            context.write(key, result);
        }
    }

    public int run(String[] args) throws Exception {

        // Create a new MapReduce job
        Job job = Job.getInstance(getConf(), "WordCountApp");

        //  Set the Jar by finding where a given class came from
        job.setJarByClass(WordCount.class);

        // Set the Mapper for the job
        job.setMapperClass(TokenizerMapper.class);

        // Set the combiner class for the job
        job.setCombinerClass(IntSumReducer.class);

        // Set the Reducer for the job
        job.setReducerClass(IntSumReducer.class);

        // Set the key class for the job output data
        job.setOutputKeyClass(Text.class);

        // Set the value class for job outputs
        job.setOutputValueClass(IntWritable.class);

        // Add a Path to the list of inputs for the map-reduce job
        FileInputFormat.addInputPath(job, new Path(args[0]));

        // Set the Path of the output directory for the map-reduce job.
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // Submit the job to the cluster and wait for it to finish
        return job.waitForCompletion(true) ? 0 : 1;
    }

    /**
     * The application's entry point
     *
     * @param args an array of command-line arguments for the application
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();

        /*
          Runs the given Tool by Tool.run(String[]), after
          parsing with the given generic arguments. Uses the given
          Configuration, or builds one if null.
         */
        System.exit(ToolRunner.run(conf, new WordCount(), args));
    }
}
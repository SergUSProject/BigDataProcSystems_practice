package edu.classes.mr;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

public class SortedRatingDriver extends Configured implements Tool {

    public int run(String[] args) throws Exception {

        Job job = Job.getInstance(getConf(), "SortedRatingApp");

        // Input
        FileInputFormat.addInputPath(job, new Path(args[0]));
        job.setInputFormatClass(TextInputFormat.class);

        // Set the Jar by finding where a given class came from
        job.setJarByClass(SortedRatingDriver.class);

        // Mapper
        job.setMapperClass(SortedRatingMapper.class);

        // Shuffling and sorting
        job.setPartitionerClass(RatingKeyWritable.KeyPartitioner.class);
        job.setSortComparatorClass(RatingKeyWritable.SortComparator.class);
        // job.setGroupingComparatorClass(RatingKeyWritable.GroupComparator.class);

        // Combiner/Reducer
        job.setCombinerClass(SortedRatingReducer.class);
        job.setReducerClass(SortedRatingReducer.class);

        // Output
        job.setOutputKeyClass(RatingKeyWritable.class);
        job.setOutputValueClass(IntWritable.class);

        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        job.setOutputFormatClass(TextOutputFormat.class);

        // Run the job
        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        conf.setStrings("mapreduce.output.textoutputformat.separator", "\t");
        System.exit(ToolRunner.run(conf, new SortedRatingDriver(), args));
    }
}
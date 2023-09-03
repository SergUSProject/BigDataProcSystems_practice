package edu.classes.mr;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mrunit.mapreduce.MapDriver;
import org.apache.hadoop.mrunit.mapreduce.MapReduceDriver;
import org.apache.hadoop.mrunit.mapreduce.ReduceDriver;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class WordCountTest {

    private MapDriver<LongWritable, Text, Text, IntWritable> mapDriver;
    private ReduceDriver<Text, IntWritable, Text, IntWritable> reduceDriver;
    private MapReduceDriver<LongWritable, Text, Text, IntWritable, Text, IntWritable> mapReduceDriver;

    @Before
    public void setUp() {
        WordCount.TokenizerMapper mapper = new WordCount.TokenizerMapper();
        WordCount.IntSumReducer reducer = new WordCount.IntSumReducer();
        mapDriver = MapDriver.newMapDriver(mapper);
        reduceDriver = ReduceDriver.newReduceDriver(reducer);
        mapReduceDriver = MapReduceDriver.newMapReduceDriver(mapper, reducer);
    }

    @Test
    public void testMapper() throws IOException {
        mapDriver.withInput(new LongWritable(), new Text("a a b c d"));
        mapDriver.withOutput(new Text("a"), new IntWritable(1));
        mapDriver.withOutput(new Text("a"), new IntWritable(1));
        mapDriver.withOutput(new Text("b"), new IntWritable(1));
        mapDriver.withOutput(new Text("c"), new IntWritable(1));
        mapDriver.withOutput(new Text("d"), new IntWritable(1));
        mapDriver.runTest();
    }

    @Test
    public void testReducer() throws IOException {
        List<IntWritable> values = new ArrayList<>();
        values.add(new IntWritable(1));
        values.add(new IntWritable(1));
        reduceDriver.withInput(new Text("a"), values);
        reduceDriver.withOutput(new Text("a"), new IntWritable(2));
        reduceDriver.runTest();
    }

    @Test
    public void testMapReduce() throws IOException {
        mapReduceDriver.withInput(new LongWritable(), new Text("a a b c d"));
        mapReduceDriver.withOutput(new Text("a"), new IntWritable(2));
        mapReduceDriver.withOutput(new Text("b"), new IntWritable(1));
        mapReduceDriver.withOutput(new Text("c"), new IntWritable(1));
        mapReduceDriver.withOutput(new Text("d"), new IntWritable(1));
        mapReduceDriver.runTest();
    }
}


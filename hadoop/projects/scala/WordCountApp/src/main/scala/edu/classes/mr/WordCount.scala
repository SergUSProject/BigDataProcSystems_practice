package edu.classes.mr

import java.io.IOException
import java.lang.Iterable
import java.util.StringTokenizer

import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.Path
import org.apache.hadoop.io.{IntWritable, LongWritable, Text}
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat
import org.apache.hadoop.mapreduce.{Job, Mapper, Reducer}

import scala.collection.JavaConverters._

class TokenizerMapper extends Mapper[LongWritable, Text, Text, IntWritable] {

  val word = new Text

  @throws[IOException]
  @throws[InterruptedException]
  override def map(key: LongWritable, value: Text, context: Mapper[LongWritable, Text, Text, IntWritable]#Context): Unit = {
    // Split a string to words
    val itr = new StringTokenizer(value.toString)
    // Iterate over the words
    while (itr.hasMoreTokens) {
      // Set the word to serializable class
      word.set(itr.nextToken)
      // Emmit the key-value pair: (word, 1)
      context.write(word, TokenizerMapper.one)
    }
  }
}

object TokenizerMapper {
  final val one = new IntWritable(1)
}

class IntSumReducer extends Reducer[Text, IntWritable, Text, IntWritable] {

  private val result = new IntWritable

  @throws[IOException]
  @throws[InterruptedException]
  override def reduce(key: Text, values: Iterable[IntWritable], context: Reducer[Text, IntWritable, Text, IntWritable]#Context): Unit = {
    val sum = values.asScala.foldLeft(0)((acc, value) => acc + value.get())
    result.set(sum)
    context.write(key, result)
  }
}

object WordCount {

  def main(args: Array[String]): Unit = {

    val conf = new Configuration()

    // Create a new MapReduce job
    val job = Job.getInstance(conf, "WordCountScalaApp")

    //  Set the Jar by finding where a given class came from
    job.setJarByClass(this.getClass)

    // Set the Mapper for the job
    job.setMapperClass(classOf[TokenizerMapper])

    // Set the combiner class for the job
    job.setCombinerClass(classOf[IntSumReducer])

    // Set the Reducer for the job
    job.setReducerClass(classOf[IntSumReducer])

    // Set the key class for the job output data
    job.setOutputKeyClass(classOf[Text])

    // Set the value class for job outputs
    job.setOutputValueClass(classOf[IntWritable])

    // Add a Path to the list of inputs for the map-reduce job
    FileInputFormat.addInputPath(job, new Path(args(0)))

    // Set the Path of the output directory for the map-reduce job.
    FileOutputFormat.setOutputPath(job, new Path(args(1)))

    // Submit the job to the cluster and wait for it to finish
    System.exit(if(job.waitForCompletion(true))  0 else 1)
  }
}

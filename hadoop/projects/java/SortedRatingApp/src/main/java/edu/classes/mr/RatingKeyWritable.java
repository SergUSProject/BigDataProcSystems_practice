package edu.classes.mr;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Partitioner;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.Objects;

public class RatingKeyWritable implements WritableComparable<RatingKeyWritable> {

    private String productId;
    private Float rating;

    private String separator = "\t";

    public RatingKeyWritable() {
        productId = "";
        rating = 0.0f;
    }

    public RatingKeyWritable(String productId, Float rating){
        this.productId = productId;
        this.rating = rating;
    }

    public void set(String productId, Float rating) {
        this.productId = productId;
        this.rating = rating;
    }

    public String getProductId() {
        return productId.toString();
    }

    public void setSeparator(String separator) {
        this.separator = separator;
    }

    /**
     * Serialization
     *
     * @param out   output byte stream
     * @throws IOException
     */

    @Override
    public void write(DataOutput out) throws IOException {
        WritableUtils.writeString(out, productId);
        out.writeFloat(rating);
    }

    /**
     * Deserialization
     *
     * @param in    input byte stream
     * @throws IOException
     */
    @Override
    public void readFields(DataInput in) throws IOException {
        productId = WritableUtils.readString(in);
        rating = in.readFloat();
    }
    
    /**
     * Output for TextOutputFormat
     *
     * Average rating per product
     *
     */
    @Override
    public String toString() {
        return String.valueOf(productId.toString() + separator + String.valueOf(rating));
    }

    @Override
    public int compareTo(RatingKeyWritable ratingKeyWritable) {
        int cmp = productId.compareTo(ratingKeyWritable.productId);
        if (cmp != 0) return cmp;
        return rating.compareTo(ratingKeyWritable.rating);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RatingKeyWritable that = (RatingKeyWritable) o;
        return Objects.equals(productId, that.productId) &&
                Objects.equals(rating, that.rating);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productId, rating);
    }


    /**
     * Define the comparator that controls how the keys are sorted before they
     * are passed to the Reducer.
     *
     * Sorting by product ids and then by ratings
     *
     */
    public static class SortComparator extends WritableComparator {

        protected SortComparator() {
            super(RatingKeyWritable.class, true);
        }

    }

    /**
     * The total number of partitions is the same as the number of reduce tasks for the job. Hence this controls
     * which of the reduce tasks the intermediate key (and hence the record) is sent for reduction.
     *
     * In this case the Partitioner class is used to shuffle map outputs to reducers by product ids.
     * That means all products with the same id will be passed to an identical reducer
     *
     * Note: A Partitioner is created only when there are multiple reducers.
     *
     */
    public static class KeyPartitioner extends Partitioner<RatingKeyWritable, IntWritable> {

        @Override
        public int getPartition(RatingKeyWritable ratingKeyWritable, IntWritable intWritable, int numPartitions) {
            return Math.abs(ratingKeyWritable.getProductId().hashCode() % numPartitions);
        }
    }

    /**
     * Grouping class defines the comparator that controls which keys are grouped together
     *
     */
    public static class GroupComparator extends WritableComparator {

        protected GroupComparator() {
            super(RatingKeyWritable.class, true);
        }

        @Override
        public int compare(WritableComparable a, WritableComparable b) {
            RatingKeyWritable r1 = (RatingKeyWritable) a;
            RatingKeyWritable r2 = (RatingKeyWritable) b;
            return r1.getProductId().compareTo(r2.getProductId());
        }

    }


}

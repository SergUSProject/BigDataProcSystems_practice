package edu.classes.mr;

import org.apache.hadoop.io.Writable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class StatsTupleWritable implements Writable {

    // Sum of ratings of the given product
    private double sum;

    // Number of ratings
    private int count;

    public StatsTupleWritable() {
        sum = 0d;
        count = 0;
    }

    public StatsTupleWritable(double sum, int count){
        this.sum = sum;
        this.count = count;
    }

    public void set(double sum, int count) {
        this.sum = sum;
        this.count = count;
    }

    public double getSum() {
        return sum;
    }

    public int getCount() {
        return count;
    }


    /**
     * Serialization
     *
     * @param out   output byte stream
     * @throws IOException
     */

    @Override
    public void write(DataOutput out) throws IOException {
        out.writeDouble(sum);
        out.writeInt(count);
    }

    /**
     * Deserialization
     *
     * @param in    input byte stream
     * @throws IOException
     */
    @Override
    public void readFields(DataInput in) throws IOException {
        sum = in.readDouble();
        count = in.readInt();
    }
    
    /**
     * Output for TextOutputFormat
     *
     * Average rating per product
     *
     */
    @Override
    public String toString() {
        return String.valueOf(this.sum / this.count);
    }


}

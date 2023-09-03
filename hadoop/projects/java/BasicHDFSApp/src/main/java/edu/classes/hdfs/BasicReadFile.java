package edu.classes.hdfs;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;

import java.io.InputStream;
import java.net.URI;


/**
 * The BasicReadFile class provides basic functionality for reading
 * files from HDFS and display their content in terminal
 *
 * To run in terminal:
 * hadoop jar code_java/BasicHDFSApp/out/artifacts/ReadFileApp/ReadFileApp.jar \
 *              edu.classes.hdfs.BasicReadFile \
 *              hdfs://localhost:9000/examples/hadoop/basicwritefile/sample_100_copy.json
 *
 */
public class BasicReadFile {

    /**
     * The application's entry point
     *
     * @param args an array of command-line arguments for the application
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {

        // HDFS file path argument
        String uri = args[0];

        // Initialize configuration instance
        Configuration conf = new Configuration();

        // Set system as destination
        conf.setStrings("fs.default.name", "hdfs://localhost:9000");

        // Receive a filesystem instance
        FileSystem fs = FileSystem.get(URI.create(uri), conf);

        InputStream in = null;  /* input stream from HDFS */

        try {
            // Open a HDFS file
            in = fs.open(new Path(uri));

            // Redirect the input stream to the user console
            IOUtils.copyBytes(in, System.out, 4096, false);

        } finally {
            // Close the input stream
            IOUtils.closeStream(in);
        }
    }
}


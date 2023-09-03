package edu.classes.hdfs;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;
import org.apache.hadoop.util.Progressable;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;


/**
 * The BasicWriteFile provides functionality for copying local files
 * to HDFS.
 */
public class BasicWriteFile {

    /**
     * Setup HDFS configuration
     *
     * @return  configuration instance
     */
    static Configuration setupHDFSConfiguration() {

        // Initialize configuration instance
        Configuration conf = new Configuration();

        // conf.addResource(new Path("file:///usr/lib/hadoop/etc/hadoop/hdfs-site.xml"));

        // Set system system as destination
        conf.set("fs.defaultFS", "hdfs://localhost:9000");

        // Set block size
        conf.setInt("dfs.block.size",16777216); /* 16MB */

        // conf.setInt("dfs.replication", 1);

        return conf;
    }

    /**
     * The application's entry point
     *
     * @param args an array of command-line arguments for the application
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {

        String localPath = args[0]; /* path of local file */
        String hdfsPath = args[1];  /* HDFS path */

        // Create input stream for local file
        InputStream in = new BufferedInputStream(new FileInputStream(localPath));

        // Get configuration instance
        Configuration conf = setupHDFSConfiguration();

        // Get file system instance
        FileSystem fs = FileSystem.get(URI.create(hdfsPath), conf);

        // fs.copyFromLocalFile();

        System.out.println("Start copying:");

        // Create output stream to write the local file into HDFS
        OutputStream out = fs.create(new Path(hdfsPath), new Progressable() {
            @Override
            public void progress() {
                System.out.print(".");
            }
        });

        // Write the the local file
        IOUtils.copyBytes(in, out, 4096, true);

        System.out.println("\nCopying completed.");

    }

}


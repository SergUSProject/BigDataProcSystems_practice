package edu.classes.hdfs;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.net.URI;

import static org.junit.jupiter.api.Assertions.*;


class BasicReadFileTest {

    private static final String LOCAL_FILE = "/media/sf_Hadoop/data/samples_100.json";
    private static final String HDFS_FILE = "/examples/tests/hadoop/basicwritefile/sample_100_copy.json";

    private static Configuration conf;
    private static FileSystem fs;
    private static Path filePath;

    @BeforeAll
    static void setUp() throws IOException {

        // Get configuration instance
        conf = BasicWriteFile.setupHDFSConfiguration();

        Path localPath = new Path(LOCAL_FILE);
        filePath = new Path(HDFS_FILE);

        // Get file system instance
        fs = FileSystem.get(URI.create(HDFS_FILE), conf);
        fs.copyFromLocalFile(localPath, filePath);

    }

    @Test
    void copyLocalFileToHDFS_Success() throws Exception {

        ByteArrayOutputStream output = new ByteArrayOutputStream();

        System.setOut(new PrintStream(output));

        String startsWithText = "{\"reviewerID\": \"AO94DHGC771SJ\", \"asin\": \"0528881469\",";

        BasicReadFile.main(new String[]{HDFS_FILE});

        assertTrue(output.toString().startsWith(startsWithText));

    }

    @AfterAll
    static void tearDown() throws IOException {
        fs.delete(filePath, true);
        fs.close();
    }

}

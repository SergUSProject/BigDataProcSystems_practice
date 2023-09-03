package edu.classes.hdfs;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.net.URI;

class BasicWriteFileTest {

    private static final  String TEST_DIR = "/examples/tests/hadoop/basicwritefile";
    private static Configuration conf;

    @BeforeAll
    static void setUp() {
        // Get configuration instance
        conf = BasicWriteFile.setupHDFSConfiguration();
    }

    @Test
    void copyLocalFileToHDFS_Success() throws Exception {

        final String local = "/media/sf_Hadoop/data/samples_100.json";
        final String hdfs = TEST_DIR + "/sample_100_copy.json";

        Path hdfsPath = new Path(hdfs);

        // Get file system instance
        FileSystem fs = FileSystem.get(URI.create(hdfs), conf);

        // Check existence
        assertFalse(fs.exists(hdfsPath));

        BasicWriteFile.main(new String[]{local, hdfs});

        // Check existence
        assertTrue(fs.exists(hdfsPath));

        assertEquals(fs.getReplication(hdfsPath), 1);

        // Remove directory
        fs.delete(hdfsPath, true);

        // Check existence
        assertFalse(fs.exists(hdfsPath));

    }

    @AfterAll
    static void tearDown() throws IOException {

        final String hdfs = TEST_DIR;

        Path hdfsPath = new Path(hdfs);

        // Get file system instance
        FileSystem fs = FileSystem.get(URI.create(hdfs), conf);

        if (fs.exists(hdfsPath)) fs.delete(hdfsPath, true);
    }



}

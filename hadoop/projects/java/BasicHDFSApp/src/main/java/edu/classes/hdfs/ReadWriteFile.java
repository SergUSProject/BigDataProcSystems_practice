package edu.classes.hdfs;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import java.util.logging.Logger;


/* Note: Hadoop Java API https://hadoop.apache.org/docs/r3.1.2/api/org/apache/hadoop/fs/FileSystem.html */
public class ReadWriteFile {

    private final static Logger LOGGER = Logger.getGlobal();

    private FileSystem fs;

    public ReadWriteFile(FileSystem fs) {
        this.fs = fs;
    }

    public void displayFileContent(Path filePath) {

        // TODO: check file existence

        // TODO: write file content output to the console

    }

    public void copyFromLocalToHDFS(Path srcFilePath, Path dstFilePath) {

        // TODO: write local file to HDFS

    }

}
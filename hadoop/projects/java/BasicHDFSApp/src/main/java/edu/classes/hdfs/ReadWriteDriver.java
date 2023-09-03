package edu.classes.hdfs;

import java.io.IOException;
import java.util.logging.FileHandler;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

public class ReadWriteDriver {

    private static Logger LOGGER = Logger.getGlobal();

    private static void setupLogger() {

        try {

            FileHandler fileHandler = new FileHandler("./readwrite.log", true); //file
            SimpleFormatter simple = new SimpleFormatter();
            fileHandler.setFormatter(simple);

            LOGGER.addHandler(fileHandler);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void setupFSConfiguration() {
        // TODO: set configuration
    }

    public static void main(String[] args) throws Exception {

        setupLogger();

        LOGGER.info("Started.");

        String srcFile = args[0];
        String dstFile = args[1];

        // TODO: Process args

        ReadWriteFile rwf = new ReadWriteFile(null);

        rwf.copyFromLocalToHDFS(null, null);
        rwf.displayFileContent(null);

        LOGGER.info("Completed.");

    }
}

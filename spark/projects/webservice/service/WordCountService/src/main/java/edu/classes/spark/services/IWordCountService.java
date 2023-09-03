package edu.classes.spark.services;

import edu.classes.spark.models.Message;
import edu.classes.spark.models.WordCountPair;

import java.util.List;

public interface IWordCountService {
    void submitMessage(Message message);
    List<WordCountPair> getTop10Words();
    List<WordCountPair> getWordCount();
}

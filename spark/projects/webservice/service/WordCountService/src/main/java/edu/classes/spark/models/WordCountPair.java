package edu.classes.spark.models;

public class WordCountPair {

    private String word;
    private Integer count;

    public WordCountPair(String word, Integer count) {
        this.word = word;
        this.count = count;
    }

    public String getWord() {
        return word;
    }

    public Integer getCount() {
        return count;
    }
}

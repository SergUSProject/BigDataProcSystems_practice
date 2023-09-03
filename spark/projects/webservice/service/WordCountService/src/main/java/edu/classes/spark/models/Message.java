package edu.classes.spark.models;

public class Message {

    private String uuid;
    private String content;

    public Message() {
    }

    public Message(String uuid, String content) {
        this.uuid = uuid;
        this.content = content;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getUuid() {
        return uuid;
    }

    public String getContent() {
        return content;
    }
}

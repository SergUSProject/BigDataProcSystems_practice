package edu.classes.spark.services;

import edu.classes.spark.models.Message;
import edu.classes.spark.models.WordCountPair;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ZSetOperations;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

@Service
public class WordCountService implements IWordCountService {

    @Autowired
    private KafkaTemplate<String, Message> kafkaTemplate;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Value("${app.topic.wordcount}")
    private String topic;

    @Value("${app.data_keys.word_counts}")
    private String key_word_counts;

    @Value("${app.data_keys.top_10_words}")
    private String key_top_10_words;

    @Override
    public void submitMessage(Message message) {
        kafkaTemplate.send(topic, message);
    }

    @Override
    public List<WordCountPair> getTop10Words() {

        List<WordCountPair> result = new ArrayList<>();

        Set<ZSetOperations.TypedTuple<String>> topWordsSet = redisTemplate.opsForZSet().rangeByScoreWithScores(key_top_10_words, Long.MIN_VALUE, 0);

        for (ZSetOperations.TypedTuple<String> item : topWordsSet) {
            WordCountPair pair = new WordCountPair(item.getValue(),
                    item.getScore() != null ? (int) Math.round(Math.abs(item.getScore())) : 0);
            result.add(pair);
        }

        return result;
    }

    @Override
    public List<WordCountPair> getWordCount() {

        List<WordCountPair> result = new ArrayList<>();

        Set<ZSetOperations.TypedTuple<String>> wordsSet = redisTemplate.opsForZSet().rangeByScoreWithScores(key_word_counts, Long.MIN_VALUE, 0);

        // System.out.println(wordsSet.toString());


        for (ZSetOperations.TypedTuple<String> item : wordsSet) {
            WordCountPair pair = new WordCountPair(item.getValue(),
                    item.getScore() != null ? (int) Math.round(Math.abs(item.getScore())) : 0);
            result.add(pair);
        }

        return result;
    }

}

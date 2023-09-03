package edu.classes.spark.controllers;

import edu.classes.spark.models.Message;
import edu.classes.spark.models.WordCountPair;
import edu.classes.spark.services.WordCountService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.List;

@RestController
public class WordCountAPIServiceController {

    @Autowired
    WordCountService service;

    @PostMapping(value = "api/v1/messages")
    public ResponseEntity<String> submitMessage(@RequestBody Message message, HttpServletRequest request) {
        service.submitMessage(message);
        return new ResponseEntity<>("Submitted successfully", HttpStatus.OK);
    }

    @GetMapping(value = "api/v1/top-words")
    public ResponseEntity<List<WordCountPair>> getTopWords() {
        return new ResponseEntity<>(service.getTop10Words(), HttpStatus.OK);
    }

    @GetMapping(value = "api/v1/word-counts")
    public ResponseEntity<List<WordCountPair>> getWordCount() {
        return new ResponseEntity<>(service.getWordCount(), HttpStatus.OK);
    }
}

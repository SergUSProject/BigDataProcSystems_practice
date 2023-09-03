package edu.classes.spark.controllers;

import edu.classes.spark.models.WordCountPair;
import edu.classes.spark.services.WordCountService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
public class WordCountWebServiceController {

    @Autowired
    WordCountService service;

    @GetMapping("/")
    public String main(Model model) {
        return "index";
    }

    @GetMapping("/word-counts")
    public String getWordCounts(Model model) {
        List<WordCountPair> words = service.getWordCount();
        model.addAttribute("words", words);
        return "word_counts";
    }

    @GetMapping("/top-words")
    public String getTop10Words(Model model) {
        List<WordCountPair> words = service.getTop10Words();
        model.addAttribute("words", words);
        return "top_words";
    }
}

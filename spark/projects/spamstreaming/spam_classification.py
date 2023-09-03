#!/usr/bin/python3
# -*- coding: utf-8 -*-

import click
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split

RANDOM_STATE = 123
INPUT_DATASET_PATH = "data/smstrain"

OUTPUT_MODEL_PATH = "models"
OUTPUT_VECTORIZER_FILENAME = "vecmodel.pickle"
OUTPUT_CLASSIFIER_FILENAME = "classmodel.pickle"

TFIDF_NGRAM = 1

LOGREG_REGUL = 1400
LOGREG_MAX_ITER = 100
LOGREG_SOLVER = "lbfgs"

BERNOULLI_ALPHA = 0.01


def load_data(file_path=INPUT_DATASET_PATH):

    def convert2bool(el):
        return int(el == "spam")

    columns = ["class", "message"]
    converters = {"class": convert2bool}
    return pd.read_csv(file_path,
                       sep="\t",
                       converters=converters,
                       names=columns)


def fit(model, train):
    tf_model = TfidfVectorizer(binary=True,
                               min_df=1,
                               lowercase=True,
                               ngram_range=(1,TFIDF_NGRAM),
                               norm=None,
                               use_idf=None)

    tf_train = tf_model.fit_transform(train["message"])

    return tf_model, model.fit(tf_train, train["class"])


def fit_and_score(models, train, test):

    bin_model = TfidfVectorizer(binary=True,
                               min_df=1,
                               lowercase=True,
                               ngram_range=(1,TFIDF_NGRAM),
                               norm=None,
                               use_idf=None)

    tf_train = bin_model.fit_transform(train["message"])
    tf_test = bin_model.transform(test["message"])

    for model in models:
        model.fit(tf_train, train["class"])
        model_accuracy = model.score(tf_test, test["class"])
        yield model, model_accuracy


def find_best_model(models, train, test):
    return max(fit_and_score(models, train, test), key=lambda x: x[1])


def save_models(output_dir, tf_model, model):

    import pathlib
    import pickle

    path = pathlib.Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    with open(path / OUTPUT_VECTORIZER_FILENAME, "wb") as f:
        pickle.dump(tf_model, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(path / OUTPUT_CLASSIFIER_FILENAME, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)


@click.command()
@click.option("-i", "--input", default=INPUT_DATASET_PATH, help="Input dataset path.")
@click.option("-o", "--output", default=OUTPUT_MODEL_PATH, help="Output model directory.")
def main(input, output):

    models = [
        LogisticRegression(penalty="l2",
                           fit_intercept=True,
                           max_iter=LOGREG_MAX_ITER,
                           C=LOGREG_REGUL,
                           solver=LOGREG_SOLVER,
                           random_state=RANDOM_STATE),
        BernoulliNB(alpha=BERNOULLI_ALPHA)]

    print("Loading dataset...")
    data = load_data(input)

    print("Splitting data onto train and test subsets...")
    train, test = train_test_split(data, test_size=0.2, random_state=RANDOM_STATE)

    print("Finding the best model...")
    best_model, best_model_accuracy = find_best_model(models, train, test)

    print("Best model: {}::{}".format(best_model.__class__.__name__, best_model_accuracy))

    print("Fitting the best model on the entire dataset...")
    final_vectorizer_model, final_model = fit(best_model, data)

    print("Serializing models...")
    save_models(output, final_vectorizer_model, final_model)

    print("Done.")


if __name__ == "__main__":
    main()
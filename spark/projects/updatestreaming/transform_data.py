import click
import time
import pickle
from custom_model import CustomModel


MODEL_INPUT_PATH = "models/model-current.pickle"


def load_model(model_path):
    with open(model_path, "rb") as f:
        return pickle.load(f)


@click.command()
@click.option("-i", "--input", "input_", default=MODEL_INPUT_PATH,
              help="Path where a model for transformation is placed.")
def main(input_):

    print("To exit press CTRL+C.")
    while True:
        model = load_model(input_)
        for i in range(20):
            print(model.transform(i))
        time.sleep(5)


if __name__ == "__main__":
    main()

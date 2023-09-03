import click
from pathlib import Path
from custom_model import CustomModel


MODEL_FILENAME = "model-{}.pickle"
MODEL_OUTPUT_DIR = "models"

STATE_FILE = ".cloned"


def get_base_path(custom_path):
    """
    Add a script dir as a base to files

    Note: This is primarily needed to run the script as a cron job
    """
    path = Path(custom_path)
    if path.is_absolute():
        return path
    base_dir = Path(__file__).resolve().parent
    return base_dir / path


def is_cloned():
    state_file = get_base_path(STATE_FILE)
    if state_file.is_file():
        state_file.unlink()
        return False
    state_file.touch()
    return True


def save_model(model, output_dir):

    import pickle
    import time

    timestamp = time.strftime("%Y%m%d%H%M%S")

    path = get_base_path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    model_path = path / MODEL_FILENAME.format(timestamp)

    with open(model_path, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

    symlink_path = path / MODEL_FILENAME.format("current")

    if symlink_path.is_symlink():
        symlink_path.unlink()

    symlink_path.symlink_to(Path(model_path).absolute())


@click.command()
@click.option("-o", "--output", default=MODEL_OUTPUT_DIR, help="Output model directory.")
def main(output):

    model = CustomModel()
    model.fit(is_cloned())
    save_model(model, output)


if __name__ == "__main__":
    main()


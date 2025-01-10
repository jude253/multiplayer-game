from importlib.resources import as_file, files
from pathlib import Path
from game_assets import data, img


def get_data() -> str:
    data_dir_files = files(data)
    with as_file(data_dir_files) as data_dir:
        data_txt_filepath = data_dir.joinpath("data.txt")
        return data_txt_filepath.read_text()


def get_intro_image_path() -> Path:
    img_dir_files = files(img)
    with as_file(img_dir_files) as img_dir:
        data_txt_filepath = img_dir.joinpath("intro_ball.gif")
        return data_txt_filepath

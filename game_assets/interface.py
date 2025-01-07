from importlib.resources import as_file, files
from game_assets import data


def get_data():
    data_dir_files = files(data)
    with as_file(data_dir_files) as data_dir:
        data_txt_filepath = data_dir.joinpath("data.txt")
        return data_txt_filepath.read_text()

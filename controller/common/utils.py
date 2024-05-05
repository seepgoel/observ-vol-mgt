import pandas as pd


def is_dataframe(input_data):
    return isinstance(input_data, pd.DataFrame)


def remove_dictionary_keys(dictionary, keys_to_remove):
    for key in list(dictionary.keys()):
        if key in keys_to_remove:
            del dictionary[key]


def add_slash_to_dir(directory):
    if directory and not directory.endswith('/'):
        directory += '/'
    return directory

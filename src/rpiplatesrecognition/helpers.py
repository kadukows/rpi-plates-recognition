import os

def files_in_dir(path: str):
    return (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))

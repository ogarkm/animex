import os

def absoluteFilePaths(directory, remove_prefix):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            abs_path = os.path.abspath(os.path.join(dirpath, f))
            abs_path = abs_path.replace("\\", "/")
            prefix = remove_prefix.replace("\\", "/")
            if abs_path.startswith(prefix):
                print(abs_path[len(prefix):])
            else:
                print(abs_path)

remove_prefix = r"D:\Projects\Animex\Web"
absoluteFilePaths(os.getcwd(), remove_prefix)
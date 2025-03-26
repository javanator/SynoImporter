import os

def traverse_directory(directory: str, file_lambda, dir_lambda):
    try:
        entries = os.listdir(directory)
        for entry in entries:
            # Join the current directory path with the entry name
            full_path = directory + "/" + entry

            # Check if the entry is a directory or a file
            if os.path.isdir(full_path):
                dir_lambda(full_path)
                traverse_directory(full_path, file_lambda,dir_lambda)
            else:
                file_lambda(full_path)
    except Exception as e:
        print(f"Error reading directory {directory}: {e}")
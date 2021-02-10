import os


def get_general_address(local_address):
    path = os.getcwd()[:os.getcwd().find("source")] + local_address
    return path

def get_library_address(local_address):
    path = "D:\\!pyProject\\personal_library\\data\\" + local_address
    return path


def get_anthology_elements(address):
    with open(address, "r", encoding='utf-8', errors='ignore') as file:
        text = file.read().upper()
        elements = text.split("\n")
    return elements


def clear_directory(directory):
    full_dir_address = get_general_address(directory)
    for file_name in os.listdir(full_dir_address):
        with open(full_dir_address + "//" + file_name, "w", encoding='utf-8', errors='ignore') as file:
            pass

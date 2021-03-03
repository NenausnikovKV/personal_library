import json
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

def read_directory(directory_address):
    file_names = os.listdir(directory_address)
    file_texts = []
    for file_name in file_names:
        file_address = "{0}\\{1}".format(directory_address, file_name)
        with open(file_address, "r", encoding="utf-8") as file:
            file_text = file.read()
            file_texts.append(file_text)
    return file_texts

def write_directory(directory_address, file_names, data_list):
    for file_name, data in zip(file_names, data_list):
        file_address = "{0}\\{1}".format(directory_address, file_name)
        with open(file_address, "w", encoding="utf-8") as file:
            file.write(data)
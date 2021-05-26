import os
from collections import defaultdict

from NLP.external_analizer.sentence_analizer import SentenceAnalyzer
from NLP.sentence_stage.sentence import Sentence

from file_processing.file_processing import get_general_address


def _extract_text_check_blocks(file_text):
    lines = file_text.split("\n")
    name = lines.pop(0)
    text_num = int(name[len("text "):])
    blocks = defaultdict(list)
    for line in lines:
        separator = line.find(" - ")
        block_name = line[:separator]
        block_value = line[separator + 3:]
        block_sentences = SentenceAnalyzer.divide_text_to_sentence_plan_texts(block_value)
        for block_sentence in block_sentences:
            blocks[block_name].append(Sentence.initial_from_sentence_text(block_sentence))
    return text_num, blocks


def read_check_blocks(directory):
    directory = get_general_address(directory)
    file_names = os.listdir(directory)
    text_blocks = []
    for file_name in file_names:
        file_full_address = directory + "/" + file_name
        with open(file_full_address, "r", encoding="utf-8") as file:
            file_text = file.read()
            text_num, blocks = _extract_text_check_blocks(file_text)
            text_blocks.append(blocks)
    return text_blocks


if __name__ == "__main__":
    text_blocks = read_check_blocks("out/test_components")

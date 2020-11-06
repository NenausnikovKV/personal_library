from datetime import datetime
from random import random
import re
import natasha


def get_agreements(file_text):
    agrement_start_sample = r"\wогласие\b\s+\d+"
    agreement_texts = re.split(agrement_start_sample, file_text)
    i = 0
    for text in agreement_texts:
        if text == "":
            agreement_texts.pop(i)
        i += 1
    return agreement_texts


if __name__ == "__main__":
    file_name = "../in/texts/agreements.txt"

    with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
        file_text = file.read()

    texts = get_agreements(file_text)


    addresses = []
    names = []
    locations = []


    start_time = datetime.now()



    def rewrite_matches(matches, signature, text):
        if matches.__len__() == 0:
            return text
        bias = 0
        substring = ""
        for match in matches:
            start = match.span.start - bias
            stop = match.span.stop - bias
            substring = text[start:stop]
            if substring == "":
                raise Exception
            bias += (stop-start) - signature.__len__()
            first_part = text[:start]
            second_part = text[stop:]
            text = first_part + signature + second_part
            # text = re.sub(substring, signature, text)
        if substring != "":
            return text
        else:
            raise Exception


    num = 0
    name_extractor = natasha.NamesExtractor()
    address_extractor = natasha.AddressExtractor()
    location_extractor = natasha.LocationExtractor()
    result_text =""
    for text in texts:
        print(num)
        # if num <18:
        #     continue
        # adress
        matches = address_extractor(text)
        addresses.extend(matches)
        print("address " + str(datetime.now() - start_time))
        text = rewrite_matches(matches, '<address>', text)
        start_time = datetime.now()

        # locations
        matches = location_extractor(text)
        locations.extend(matches)
        print("locations " + str(datetime.now() - start_time))
        text = rewrite_matches(matches, '<location>', text)
        start_time = datetime.now()

        # personal names
        matches = name_extractor(text)
        names.extend(matches)
        print("names " + str(datetime.now() - start_time))
        text = rewrite_matches(matches, '<name>', text)

        result_text += text
        num += 1
    file_address = "../out/preprocessing_agreements"
    with open(file_address, "w", encoding="utf-8") as write_file:
        write_file.write(result_text)
    b = 0

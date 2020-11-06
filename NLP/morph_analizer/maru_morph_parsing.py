import maru
analyzer = maru.get_analyzer(tagger='crf', lemmatizer='pymorphy')
analyzed = analyzer.analyze(['Согласие', 'на', 'обработку', 'персональных', 'данных'])
for morph in analyzed:
    print(morph)

from rnnmorph.predictor import RNNMorphPredictor
predictor = RNNMorphPredictor(language="ru")
forms = predictor.predict(['Согласие', 'на', 'обработку', 'персональных', 'данных'])
print(forms[0].pos)
print(forms[0].tag)
print(forms[0].normal_form)
print(forms[0].vector)
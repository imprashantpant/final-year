import re


def calculate_accuracy(original, generated):
    sentencesInUserSummary= sorted(set(re.split(r' *[\.\?!][\'"\)\]]* *', original)))
    sentencesInTfidsSummary = sorted(set(re.split(r' *[\.\?!][\'"\)\]]* *', generated)))

    new_user = set()
    new_gen = set()

    for val in sentencesInUserSummary:
        if val=="" or val ==" ":
            pass
        else:
            new_user.add(val)

    for val in sentencesInTfidsSummary:
        if val=="" or val ==" ":
            pass
        else:
            new_gen.add(val)

    new = new_user.intersection(new_gen)
    acc = (len(new) / len(new_gen)) * 100

    return acc

from nlp import FooNLP
import pandas as pd

test_inputs = [
    "The life  of π",
    "My fiancée is  > 30",
    "(I) love being happy",
    "5 + 8 = 12 does that mean anything",
    "I don't wanna go on with u like that",
    "Fractions 3/4 75% is meaningful",
]

clean_outputs = [
    "the life of p",
    "my fiancee is",
    "love be happy",
    "does that mean anyth",  # note the tricky part of stemming
    "do not wanna go on with u like that",
    "fraction is meaningful",
]


def test_clean():
    nlp = FooNLP()
    assert nlp.clean("The life of π") == "the life of p"
    assert nlp.clean("my fiancée is >  30") == "my fiancee is"


def test_destop():
    nlp = FooNLP()
    assert nlp.destop('what a world') == 'what world'


def test_tokenize():
    nlp = FooNLP()
    assert " ".join(nlp.tokenize('what a   world')) == 'what a world'


def test_lemmitize():
    nlp = FooNLP()
    assert nlp.lemmitize('worked at happening places') == 'work at happen place'


def test_bag_of_words():
    nlp = FooNLP()
    sentences = ['The indian life of the indian pi', 'The life and pain of the french fiancée', 'my life my death my pain']
    (h, m) = nlp.bag_of_words(sentences)
    df = pd.DataFrame(m, columns=h)
    print(sentences)
    print(df)
    assert df['indian'].sum() == 2
    assert df['death'].sum() == 1
    assert df['the'].sum() == 4
    assert df['life'].sum() == 3
    assert df['the indian'].sum() == 2
    assert df['the indian pi'].sum() == 1


def test_tfidf():
    nlp = FooNLP()
    sentences = ['The indian life of the indian pi', 'The life and pain of the french fiancée', 'my life my death my pain']
    (h, m) = nlp.tfidf(sentences)
    df = pd.DataFrame(m, columns=h)
    print(sentences)
    print(df)
    assert round(df['indian'].sum(),2) == 0.70
    assert round(df['death'].sum(),2) == 0.30
    assert round(df['the'].sum(),2) == 1.11
    assert round(df['life'].sum(),2) == 0.61


def test_all():
    for input, output in zip(test_inputs, clean_outputs):
        nlp = FooNLP(input)
        assert nlp.cleaned_txt == output
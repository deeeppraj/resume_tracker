import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

import nltk
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
stop = stopwords.words('english')
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
lematizer = WordNetLemmatizer()



data = pd.read_csv('processed_courses.csv')
df = data['Description']
df = np.array(df)

corpus = []
for sent in df:
    sentance = sent.lower()
    lemmas = [lematizer.lemmatize(word) for word  in word_tokenize(sentance) if word.isalpha() and word not in stop]
    filtered = ' '.join(lemmas)
    corpus.append(filtered)

desc_tfidf = TfidfVectorizer(ngram_range=(1,2))
desc_vectors = desc_tfidf.fit_transform(corpus)





def vectors(inp):
    return desc_tfidf.transform(inp)

def get_course_recomend(missing_skills):
    missing_skills  = [', '.join(missing_skills)]
    text_vect = vectors(missing_skills)
    similar = cosine_similarity(desc_vectors,text_vect).flatten()
    top5 = similar.argsort()[::-1][:5]
    return top5

## will return indices corresponding to courses from the dataframe:

course_data = pd.read_csv('processed_courses.csv')
course_data = course_data.drop(columns=['Unnamed: 0.1','Unnamed: 0'],axis=1)   

def get_course_data(indices):
    details= []
    for i in range(len(indices)):
        data = course_data.iloc[indices[i],:].to_dict()
        details.append(data)
    return details

## will return a list of dictionaries

    
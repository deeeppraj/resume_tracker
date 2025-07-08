import pickle
import os
import re
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from pypdf import PdfReader
import  nltk

nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus  import stopwords
stop = stopwords.words('english')




MODEL_PATH = r'Artifacts\model.pkl'
PREPROCESSOR_PATH = r'Artifacts\preprocessor.pkl'
DECODEER_PATH = r'Artifacts\decoder.pkl'

lematizer = WordNetLemmatizer()


def save_file(file_path,obj):
    with open(file_path,'wb') as file:
        pickle.dump(obj=obj,file=file)


def cleantext(txt):
    cleanText = re.sub('http\S+\s', ' ', txt)
    cleanText = re.sub('RT|cc', ' ', cleanText)
    cleanText = re.sub('#\S+\s', ' ', cleanText)
    cleanText = re.sub('@\S+', '  ', cleanText)  
    cleanText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText) 
    cleanText = re.sub('\s+', ' ', cleanText)
    return cleanText

def get_processed_corpus(inp):
    corpus = []
    for sentence in inp:
        cleaned_sent = cleantext(sentence[0].lower())
        filtered = [lematizer.lemmatize(word) for word in word_tokenize(cleaned_sent) if word.isalpha() and word not in stop]
        filtered_sent = ' '.join(filtered)
        corpus.append(filtered_sent)
    return corpus

def resume_data(file):
    reader = PdfReader(file)
    data = []
    is_valid = True
    for page  in reader.pages:
        text = page.extract_text()
        if text:
            data.append(text)
        else:
            is_valid = False

    return ['\n'.join(data),is_valid]





def load_obj(file):
    with open(file, 'rb') as obj:
        object = pickle.load(obj)
    return  object


def output_predict(data):
    processed_data = get_processed_corpus(data)
    tfidf = load_obj(PREPROCESSOR_PATH)
    data_tfidf = tfidf.transform(processed_data)

    model = load_obj(MODEL_PATH)
    decoder = load_obj(DECODEER_PATH)

    probs = model.predict_proba(data_tfidf)[0]  # get probabilities for the first resume
    top_indices = probs.argsort()[-5:][::-1]  # top 3 indices sorted descending
    top_labels = decoder.inverse_transform(top_indices)
    top_scores = probs[top_indices]

    return list(zip(top_labels, top_scores))



        
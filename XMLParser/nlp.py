import re, nltk, pprint
from nltk.corpus import stopwords
import string
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer


def tokenize(text):
  porter = nltk.PorterStemmer()
  s = set(stopwords.words('english'))
  punctuations = set(string.punctuation)
  tokens = word_tokenize(text)
  cleanList = []
  for t in tokens:
    t = t.lower()
    if t not in s and t not in punctuations:
      nd = re.sub('\d', '', t)
      if nd:
        cleanList.append(t)
  stemmedTokens = [porter.stem(t) for t in cleanList]
  return stemmedTokens
  
def lemmaTokenize(text):
  wordnet_lemmatizer = WordNetLemmatizer()
  s = set(stopwords.words('english'))
  punctuations = set(string.punctuation)
  tokens = word_tokenize(text)
  cleanList = []
  for t in tokens:
    t = t.lower()
    if t not in s and t not in punctuations:
      nd = re.sub('\d', '', t)
      if nd:
        cleanList.append(t)
  lemmatizedTokens = [wordnet_lemmatizer.lemmatize(t) for t in cleanList]
  return lemmatizedTokens
  

def chunkText(tokens):
  # words = [word[0] for word in nltk.ne_chunk(nltk.pos_tag(tokens)) if len(word) > 1 and 'NN' == word[1]]
  words = [word[0] for word in nltk.ne_chunk(nltk.pos_tag(tokens)) if len(word) > 1 and 'NN' == word[1]]
  # words =(nltk.pos_tag(tokens)
  print(set(words))
  # return words

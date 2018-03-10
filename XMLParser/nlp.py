import re, nltk, pprint
from nltk.corpus import stopwords
import string
from nltk import word_tokenize
  
def tokenize(text):
  porter = nltk.PorterStemmer()
  s = set(stopwords.words('english'))
  punctuations = set(string.punctuation)
  numbers = ['1','2','3','4','5','6','7','8','9']
  tokens = word_tokenize(text)
  cleanList = []
  for t in tokens:
    if t not in s and t not in punctuations:
      nd = re.sub('\d', '', t)
      if nd:
        cleanList.append(t)
  stemmedTokens = [porter.stem(t) for t in cleanList]
  return stemmedTokens
  
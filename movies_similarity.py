# -*- coding: utf-8 -*-
"""movies similarity

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/abigailsleek/TEAM-B.-TASK-5/blob/master/movies_similarity.ipynb
"""
import re
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage, dendrogram
nltk.download('punkt')

#load my dataset to pandas
MOVIESDT = pd.read_csv('dataset/movies - movies.csv')
MOVIESDT.head()

MOVIESDT.drop(['Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8',
               'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12'], axis=1, inplace=True)
MOVIESDT.head()

#here, i'm going to merge the wiki_plot and the imdb_plot since
#they have slightly different summaries of the same movie,
#so i want to combine and form a single plot for easy computation.

MOVIESDT['plot'] = MOVIESDT['wiki_plot'].astype(str) + "\n" + \
                 MOVIESDT['imdb_plot'].astype(str)
MOVIESDT.head()

# statistics of my MOVIESDT
MOVIESDT.describe()


"""# Pre-processing my data in Natural Languge
> this includes:

1.   Tokenization
2.   Stemming

next, i'm going to tokenize my data.
Tokenization is the act of breaking up a sequence of strings into pieces such as
words, keywords, phrases, symbols and other elements called tokens.Tokens can be
individual words, phrases or even whole sentences. In the process of tokenization,
some characters like punctuation marks are dicarded.So i'm going to use the NLTK
method of tokenization."""


# Tokenize a paragraph from the wizard of oz into sentences and
#store in  a variable 'sent_tokenized'
SENT_TOKENIZED = [sent for sent in nltk.sent_tokenize("""
                         Dorothy and her friends are hindered and menaced by the Wicked Witch of the West.
                         She incites trees to throw apples at them, then tries to set the scarecrow on fire.
                        """)]

# Word Tokenize first sentence from sent_tokenized, save the result in a variable 'words_tokenized'
WORD_TOKENIZED = [word for word in nltk.word_tokenize(SENT_TOKENIZED[0])]

#I'm going to need to import a library that helps remove tokens
#that do not contain any letters from words_tokenized

FILTERED = [word for word in WORD_TOKENIZED if re.search('[a-zA-Z]', word)]

#Next, i'm going to stem my already filtered data. Stemming is a process
#where words are reduced to a root by removing inflection through
#dropping unnecessary characters, usually a suffix. There are several
#stemming models, including Porter and Snowball."""

# I want to create a SnowballStemmer object in english
STEMMER = SnowballStemmer("english")

# let's observe words without stemming
print("Without stemming: ", FILTERED)

#  I want to Stem the words from filtered data above and store in a variable'stemmed_words'
STEMMED_WORDS = [STEMMER.stem(word) for word in FILTERED]
# now let's check out after stemming
print("After stemming:   ", STEMMED_WORDS)


"""**clubbing**
so i want to wrap the tokenized and stemmed text together so that i can create a TF-IDF vector of
the text.Basically clubbing just makes the work easier by merging the filtered and stem text
together as one instead of creating a TF-IDF vector simultaneously for the stem and filtered text,
it's done just once on the clubbed data."""
#I am going to define a function to perform both stemming and tokenization
def tokenize_plus_stem(text):
    tokens = [y for x in nltk.sent_tokenize(text) for y in nltk.word_tokenize(x)]
    # Filter out raw tokens to remove noise
    filtered_tokens = [token for token in tokens if re.search('[a-zA-Z]', token)]
    # Stem the filtered_tokens
    stems = [STEMMER.stem(word) for word in filtered_tokens]
    return stems
WORDS_STEMMED = tokenize_plus_stem
("Dorothy and her friends are hindered and menaced by the Wicked Witch of the West.")
print(WORDS_STEMMED)

"""#Section 3
> this icludes the use of algorithms like:

*  ** TF-TDF VECTORIZER**
You know computers are not naturally smart except we make to and they don't
understand texts only 0's and 1's.So we are going to need to transform the texts to numbers
for it to be meaningful to the computer.TF-IDF (term frequency-inverse document frequency)is a
metric that represents how 'important'a word is to a document in the document set."""

#Instantiate TfidfVectorizer object with stopwords and tokenizer
TFIDF_MYOBJECT = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_plus_stem,
                                 ngram_range=(1, 3))

"""So right now, let's fit the text and then transform the text to produce the corresponding
numeric form of the data which the computer will be able to understand and derive meaning from.
To do this, use the fit_transform() method of the TfidfVectorizer object."""

#Fit and transform the tfidf_myobject using the "plot" of each movie
TFIDF_MATRIX = TFIDF_MYOBJECT.fit_transform([x for x in MOVIESDT["plot"]])
print(TFIDF_MATRIX.shape)

"""# clustering

Clustering is the process of dividing the entire data into groups (also known as clusters)
based on the patterns in the data.
k-means clustering aims to partition n observations into k clusters in which each observation
belongs to the cluster with the nearest mean, serving as a prototype of the cluster.
K-means is an algorithm which helps us to implement clustering in Python."""
#Let's create a KMeans object with 5 clusters and store as km
KM = KMeans(n_clusters=5)
KM.fit(TFIDF_MATRIX)
CLUSTERS = KM.labels_.tolist()
#Create a column cluster to denote the generated cluster for each movie
MOVIESDT["CLUSTER"] = CLUSTERS
MOVIESDT['CLUSTER'].value_counts()

SIMILARITY_DISTANCE = 1 - cosine_similarity(TFIDF_MATRIX)
"""**let's go ahead and create the dendrogram**
A dendrogram is a diagram that shows the hierarchical relationship between objects.
It is most commonly created as an output from hierarchical clustering."""

# Create mergings matrix
MERGINGS = linkage(SIMILARITY_DISTANCE, method='complete')
MOVIES_DENDROGRAM = dendrogram(MERGINGS,
                               labels=[x for x in MOVIESDT["title"]],
                               leaf_rotation=90,
                               leaf_font_size=16,)

FIG = plt.gcf()
_ = [lbl.set_color('r') for lbl in plt.gca().get_xmajorticklabels()]
FIG.set_size_inches(108, 21)
plt.show()


"""# OBSERVATION

from the dendrogram above, you will notice that based on the distance calculation gotten
from cosine _similarity, we have been able to cluster similar movies.Therefore, supposing i am
searching for a similar movie after Fargo, it definately will be Northwest."""

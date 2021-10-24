import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
import seaborn as sns

import spacy
from spacy.tokens import Doc, Span, Token # for creating global objects 
from spacy.matcher import Matcher # for rule-based matching
from spacy.matcher import DependencyMatcher
from spacy.language import Language # for building custom pipeline components
from spacy.pipeline import EntityRuler 

from copy import deepcopy

from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from gensim.matutils import corpus2dense
from gensim.models import Phrases
from gensim.models.coherencemodel import CoherenceModel
from gensim.similarities import MatrixSimilarity

# initializes the spacy Language model
nlp = spacy.load('en_core_web_lg') # loads our NLP model
nlp.Defaults.stop_words |= {"hint", "Hint", "hints", "touch", "touches", "Touch", "note", "Note", "notes", "Notes", "little", "end", "thing", "palate", "Palate", "nose", "Nose", "whisper", "whispers"}
ruler = nlp.add_pipe("entity_ruler")
pattern_csk = [{"LEMMA": {"IN": ["cask", "octave", "pipe", "puncheon", "butt", "barrel", "hogshead"]} } ]
patterns = [ {"label": "CSK", "pattern": pattern_csk }]

ruler.add_patterns(patterns)



class Scotch_Recommender:

    def __init__(self, corpus = None, dictionary = None, phrase_model = None, full_data = None, lda_mod = None, index_sim = None):

        if dictionary == None:
            # load pickled dictionary. the default will be the reduced dictionary stored in the dictionary folder.
            dictionary_path = "dictionaries\\reduced_gemsimdict_unified.pkl"
            self.dictionary = pickle.load(open(dictionary_path, 'rb'))

        if phrase_model == None:
            # load phrase model
            phraser_path = "models\\phrase_mod.pkl"
            self.phrase_model = pickle.load(open(phraser_path, 'rb'))
        
        if corpus == None:
            #load gensim BoW corpus
            corpus_path = "data\\final\\descriptor_corpus.pkl"
            self.corpus = pickle.load(open(corpus_path, 'rb'))

        if lda_mod == None:
            lda_path = "models\\Scotch_LDA.pkl"
            self.scotch_topic_model = pickle.load(open(lda_path, 'rb'))
 
        if index_sim == None:
            index_sim_path = "data\\final\\index_sim.pkl"
            self.index_sim = pickle.load(open(index_sim_path, 'rb'))

        # breakdown of scotch by topic
        self.scotch_lda_decomp = self.scotch_topic_model[self.corpus]


        if full_data == None:
            whisk_token_path = "data\\interim\\whisk_unified_tokenized.csv"
            self.full_data = pd.read_csv(whisk_token_path).drop(columns=["Unnamed: 0"])

    def get_recommendations(self, name, num_rec = 10):

        doc_num = self.full_data[self.full_data['name'] == name].index[0]
        sims = self.index_sim[self.scotch_lda_decomp[doc_num]]

        sorted_val_df = pd.Series(sims).sort_values(ascending = False).drop(index=doc_num).to_frame(name = "similarity")

        sorted_val_df['name'] = self.full_data.iloc[sorted_val_df.index].name.values
    
        # drop whiskies that have the same name and age expression.
        sorted_val_df.drop(index = sorted_val_df[sorted_val_df['name'].str.contains(name, flags=re.IGNORECASE, regex=True)].index, inplace = True)


        return sorted_val_df.name[0: num_rec]

    #------the rest of this class is for taking in a custom whisky desciption and getting recommendations -------------

    # now we tokenize the incoming text
    def tokenize_text(self, text, *args):

        unique_token_set = set(self.dictionary.itervalues())

        # construct doc
        doc = nlp(text)
        # generate token list removing verbs, punctuation, prepositions, stop words, and initial lemmatizing
        token_list = [token.lemma_.lower() for token in doc if ( (not token.is_stop) & (not token.is_punct) & (token.pos_ != 'VERB') & (token.dep_ != 'prep') & (token.is_alpha)) ]

        # MANUAL LEMMATIZATION
        # ----------------------- 
        doc_str = " ".join(token_list)

        #all of these go to -y endings
        regex_search_pattern1 = [r'iness\b', r'ied\b', r'iful\b', r'ifull\b', r'ifully\b']
        doc_str = re.sub("|".join(regex_search_pattern1) , 'y', doc_str)

        # all tokens ending with "-ness" or "-ful" should just have this ending chopped off.
        regex_search_pattern2 = [r'ness\b', r'ful\b', r'full\b']
        doc_str = re.sub("|".join(regex_search_pattern2) , '', doc_str)
        
        #specific word replacement rule
        regex_search_pattern3 = r'tannic'
        doc_str = re.sub(regex_search_pattern3 , 'tannin', doc_str)

        # this is where we deal with -y endings
        doc_list = doc_str.split()
        regex_search_pattern4 = r"y\b"
        regex_search_pattern5 = r"\w+[^aeiou][aeiou][^aeiou]\b"
        
        spac_doc_list = []
        for token in doc_list:

            stemmed_tok = re.sub(regex_search_pattern4, "", token)
            # check against the gensim dictionary
            if stemmed_tok in unique_token_set:
                spac_doc_list.append(stemmed_tok)
            # if not in dictionary and stem ends with vowel and consonant after stripping y, then add -e to end (smok -> smoke)   
            elif (stemmed_tok not in unique_token_set) & (not not re.findall(regex_search_pattern5, stemmed_tok)):
                stemmed_tok = stemmed_tok + 'e'
                spac_doc_list.append(stemmed_tok)
        
            else:
                spac_doc_list.append(token)
        #----FINISH OF MANUAL LEMMATIZATION-----------------------------
        # apply trained gensim phrase object on token list
        bigram_tokenized = self.phrase_model[spac_doc_list]

        return bigram_tokenized

    def recommend_from_text(self, text, num_rec = 10):

        tokenized = self.tokenize_text(text)
        bow_vec = self.dictionary.doc2bow(tokenized)
        sims = self.index_sim[self.scotch_topic_model[bow_vec]]

        sorted_val_df = pd.Series(sims).sort_values(ascending = False).to_frame(name = "similarity")

        sorted_val_df['name'] = self.full_data.iloc[sorted_val_df.index].name.values

        return sorted_val_df.name[0: num_rec]
        

        
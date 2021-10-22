"""
This file is used for preprocessing the scotch whisky sensory descriptions into a lemmatized/stemmed token set with all stop words removed

"""
import numpy as np
import pandas as pd
import re
import itertools


import spacy
from spacy.tokens import Doc, Span, Token # for creating global objects 
from spacy.matcher import Matcher # for rule-based matching
from spacy.matcher import DependencyMatcher
from spacy.language import Language # for building custom pipeline components
from spacy.pipeline import EntityRuler 

from gensim.corpora.dictionary import Dictionary
from gensim.matutils import corpus2dense
from gensim.models import Phrases
from hunspell import Hunspell


# load spacy's large english language model
nlp = spacy.load('en_core_web_lg') 
# custom stop words for this corpus
nlp.Defaults.stop_words |= {"hint", "Hint", "hints", "touch", "touches", "Touch", "note", "Note", "notes", "Notes", "little", "end", "thing", "palate", "Palate", "nose", "Nose", "whisper", "whispers"}
ruler = nlp.add_pipe("entity_ruler")

pattern_csk = [{"LEMMA": {"IN": ["cask", "octave", "pipe", "puncheon", "butt", "barrel", "hogshead"]} } ]

patterns = [ {"label": "CSK", "pattern": pattern_csk }]

# adds rules that will be used to parse and create entities
ruler.add_patterns(patterns)

#-------------------------------------------------------------------------------------------------------------------------
# passing context metadata into attributes via pipeline requires the data to be in a specific form. We'll create a function to do transform the data into the right form.
# then the data will be used to create a Doc object generator based off of the text and context metadata.

def doc_context_tupling(data, textcolname, *args):

    col_list = [textcolname]
    attr_list = list(args)
    
    col_list.extend(attr_list)

    # data is in dataframe w/ form of whisky_df
    subset_dict_list = list(data[col_list].T.to_dict().values())

    # now let's form a (text, context_dictionary) tuple which is what the spacy pipeline requires. 

    data_context_list = [ (subset_dict.pop(textcolname), subset_dict) for subset_dict in subset_dict_list]

    # for each key-value pair in args, we'll need to create a Doc extension attribute.
    

    for doc, context in nlp.pipe(data_context_list, as_tuples = True):
        Doc.set_extension('context', force = True, default = context)
        yield doc

#--------------------------------------------------------------------------------------------------------------------


# the manual stemmer is going to take the list of tokenized documents and manually stem/lemmatize before gensim dictionary creation.
# this is due to the fact that SpaCy's lemmatizer still keeps a lot of tokens distinct that should actually be rolled into the same token (smokiness, smoky, smoke)
#NOTE: this stemmer relies on a large enough corpus that variants + the stemmed word exist in the corpus
def manual_stemmer(tokenized_list):

    word_checker = Hunspell() # we'll use this for checking whether the stemmed word is in the hunspell english dictionary

    # we also want to establish the set of unique tokens in tokenized_list (the entire corpus)
    unique_token_set = set(itertools.chain(*tokenized_list))

    final_token_list = []
    for doc in tokenized_list:
        doc_str = " ".join(doc)
        
         # on first pass, all tokens that end with "-iness" and "-ied" should be contracted to "-y"
        regex_search_pattern1 = [r'iness\b', r'ied\b', r'iful\b', r'ifull\b', r'ifully\b']
        doc_str = re.sub("|".join(regex_search_pattern1) , 'y', doc_str)

        # all tokens ending with "-ness" or "-ful" should just have this ending chopped off.
        regex_search_pattern2 = [r'ness\b', r'ful\b', r'full\b']
        doc_str = re.sub("|".join(regex_search_pattern2) , '', doc_str)
        
        #specific word replacement rule
        regex_search_pattern3 = r'tannic'
        doc_str = re.sub(regex_search_pattern3 , 'tannin', doc_str)

        

        """
        Stemming words with -y endings can be tricky. We are going to construct a rule that depends on the existing tokens in the dataset.
        It's important to have removed stop words, etc from the corpus and have a large enough corpus before running this stemmer.   
        
        First stem. In some cases, we wont have a complete word (e.g. smoky --> smok). After stemming, we will check whether the ending follows a pattern
        like consonant-vowel-consonant after stemming. Append -e. This rule converts smok to smoke. It also converts pepper to peppere. For other cases, the 
        stemmed word doesnt match this consonant-vowel-consonant pattern. 

        At the end we check whether the stemmed/converted word is in the original corpus. If not, then do not stem the word at all and return the 
        original token. This will mess up rare words that occur only once in the corpus, but that wont matter down the line.
        
        """

        doc_list = doc_str.split()
        regex_search_pattern4 = r"y\b"
        regex_search_pattern5 = r"\w+[^aeiou][aeiou][^aeiou]\b"
        
        spac_doc_list = []
        for token in doc_list:

            stemmed_tok = re.sub(regex_search_pattern4, "", token)

            if stemmed_tok in unique_token_set:
                spac_doc_list.append(stemmed_tok)
                
            elif (stemmed_tok not in unique_token_set) & (not not re.findall(regex_search_pattern5, stemmed_tok)):
                stemmed_tok = stemmed_tok + 'e'
        
            else:
                spac_doc_list.append(token)

        final_token_list.append(spac_doc_list)
        
    return final_token_list     

    
#---------------------------------------------------------------------------------------------------------------------------
# function that converts a set of documents into a tokenized document list with relevant bigrams. also creates a gensim dictionary object

def create_gensim_data_bigrams(data, col_to_tokenize):

    doc_contextor = doc_context_tupling(data, col_to_tokenize, 'name')
    name_list = []
    doc_list = []
    doc_generator = doc_contextor

    for current_doc in doc_generator:
        # lower case lemmatized alphabetic words with common stop words, puncuation removed.
        # Also filter out verbs, remove prepositions

        token_list = [token.lemma_.lower() for token in current_doc if ( (not token.is_stop) & (not token.is_punct) & (token.pos_ != 'VERB') & (token.dep_ != 'prep') & (token.is_alpha)) ]
        doc_list.append(token_list)
        name_list.append(current_doc._.context['name'])

    # now let's train a phrase model that can include relevant bigrams as tokens in the tokenized docs
    phrase_mod = Phrases(doc_list)
    toks_with_bigrams = list(phrase_mod[doc_list]) # this creates the new set of tokenized documents with bigrams.

    # manual stemming:
    toks_with_bigrams = manual_stemmer(toks_with_bigrams)

    # let's create a gensim dictionary off of this.

    gens_dict_bigrams = Dictionary(toks_with_bigrams)

    #it's probably useful to return the document token lists as a Python dictionary with corresponding whisky names.
    token_bigram_dict = {'name': name_list, col_to_tokenize + '_tokenized': toks_with_bigrams}

    return pd.DataFrame.from_dict(token_bigram_dict), gens_dict_bigrams
#-------------------------------------------------------------------------------------------------------------------------------------

# this function executes the tokenization on each sense column, saves it into the dataframe and removes the corresponding free text
# also generates a python dictionary of gensim Dicionaries for each sense column corpus.

def generate_tokenized_cols(data, *args):
    descriptor_cols = list(args)

    # for loop to generate bigram-tokenized list and list of dictionaries for each tasting note type (i.e, nose, palate, finish)

    tokenized_doc_list = []
    gensimDict_dict = {}

    for descriptor in descriptor_cols:


        tokenized_doc, gensim_dictionary = create_gensim_data_bigrams(data, descriptor)
        tokenized_doc_list.append(tokenized_doc.set_index('name'))

        gensimDict_dict.update({descriptor: gensim_dictionary})

    
    tokdocs_df = pd.concat(tokenized_doc_list, axis = 1).reset_index()
    new_data = pd.concat([tokdocs_df.set_index('name'), data.set_index('name')], axis = 1).reset_index().drop(columns = descriptor_cols).drop(columns = ['description'])

    
    return new_data, gensimDict_dict

    
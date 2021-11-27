# Of digestive biscuits, old leather, and smoked ham: making sense of the language of Scotch whisky

The language of Scotch tasting notes can be colorful and arcane with the not infrequent traversal into the land of the absolutely ridiculous. One tasting note of a Scotch from an expert taster goes like this:

>Nose: This opens on big, smoky muscular peat notes. There are spices, and liquorice, as well as a big dose of salt. It appears beautifully on the nose, amidst the classic iodine/sticking plasters and cool wood smoke we love.

>Palate: Seaweed-led, with a hint of vanilla ice cream and more than a whiff of notes from the first aid box (TCP, plasters etc). The oak is big, and muscles its way into the fore as you hold this whisky over your tongue. An upsurge of spices develop – cardamom/black pepper/chilli.

>Finish: Big and drying, as the savoury, tarry notes build up with an iodine complexity.


But of course...the classic iodine/sticking plasters we love...aaahhhh there it is...a refreshing and comforting whiff of the first aid box.

<p align="center">
    <img src="reports/figures/richpaterson_expert.jpg" alt="richpaterson_expert" width="500"/>
    <em>Master blender Richard Paterson getting his nose in there.</em>
</p>


Besides the oddness of these tasting notes and general hilarity that can ensue from reading them, there is another thing worth noting. *The notes, while couched in metaphor, are often highly specific.* Scotch whisky tasting notes can have references to very specific sensory experiences and descriptors. There are many questions here:

1. Within the array of these specific descriptors, does a central set exist? By this we mean a lexicon that contains words that occur frequently enough across expert tasting notes but not too frequently as to have no descriptive power at all.
2.  Are there groupings among these descriptors? Do these groups corresponds to meaningful taste/smell types within the domain of Scotch whisky?
3. Can we more profitably understand Scotches in terms of these general groupings and use these to compare Scotches to each other?

**This project attempts to answer these questions by first constructing a tasting note dictionary from a repository of expert tasting notes. We then employ various dimensionality reduction techniques and topic modeling to discover any structure within the set of descriptors. This structure is used to get a more robust breakdown of the flavor profiles of various Scotches. We then test these groupings by building a Scotch whisky recommendation engine.**

Data Sources 
------------

Master of Malt is an online store specializing in Scotch single malts. The site is also a repository of information about Scotches that include tasting notes by expert tasters (the chaps at Master of Malt). We created a Scrapy spider to extract tasting notes and various other bottling details of ~ 8600 single malt Scotches. The start page for our spider is here: <br>
https://www.masterofmalt.com/country-style/scotch/single-malt-whisky/ <br>

A sample Scotch product page containing tasting notes and other bottling details (region, age statement, etc.) can be viewed [here](https://www.masterofmalt.com/whiskies/lagavulin/lagavulin-16-year-old-whisky/). 

The scrapy spider and associated details can be found [here](https://github.com/admveen/ScotchNLP/blob/master/whiskeyscraper/whiskeyscraper/spiders/MM_spyder.py).

Summary 
------------

An overview of text normalization/tokenization, EDA and Correspondence Analysis, model selection/tuning, and our Scotch recommendation engine can be found in the [final report](https://github.com/admveen/ScotchNLP/blob/master/reports/Cpstone3_finalreport.pdf). 

A more succinct version can be found in the [slide deck](https://github.com/admveen/ScotchNLP/blob/master/reports/cpstone3_pres.pdf). 

Further detail of the our text processing pipeline and analysis/modeling can be found in the notebooks and in certain relevant source files:

### I. Data Wrangling 

We employed a combination of spacy and gensim to construct a text preprocessing pipeline from the scraped data. Some features, such as cask maturation information and whether a whisky was chill filtered or cask strength, were extracted from the free text when they were not available in structured form. Tasting note descriptions were processed in a spacy nlp pipeline: defining and removing relevant stop words, POS filtering, NER removal (where relevant), stemming/lemmatization and tokenization to extract relevant taste/smell descriptors. We also used Gensim's phraser models to construct probable bigrams (e.g. 'maple_syrup'). We then constructed a Gensim dictionary filtered to exclude super common and very rare tokens and then used the dictionary to generate a BoW corpus. Details of all this data wrangling can be found in the notebook: <br>
[Data Wrangling Notebook](https://github.com/admveen/ScotchNLP/blob/master/DataWrangling.ipynb) <br>

### II. Exploratory Data Analysis

The trickiest question here was how best to visualize the space of descriptors and their relationships with each other. We employed a dimensionality reduction/embedding technique called Correspondence Analysis (CA) to visualize descriptors in a low dimensional space and identify regions of descriptors that had coherent taste/smell themes. We also visualized the distribution of Scotches in this embedding space conditioned on the whisky making region. This visualization was used to explore differences in taste profiles across different regions. <br>

[EDA Notebook](https://github.com/admveen/ScotchNLP/blob/master/EDA.ipynb) <br>

### III. Modeling 

Ultimately, we want to learn taste groups within the descriptor space AND break down each tasting note in a combination of these groups. Topic modeling is well suited for this and we employed Latent Dirichlet Allocation in order to obtain a set of taste/smells groups that were recognizably distinct within the domain of Scotch whisky. We tuned the number of topics/hyperparameters using intra-topic coherence ($c_v$ score) and manual human inspection via pyLDAvis. Evaluation of the topic model for various Scotches as well as a recommender engine based on the model are also in the following notebook: <br>

[Modeling Notebook](https://github.com/admveen/ScotchNLP/blob/master/Modeling.ipynb) <br>

### IV. Scotch Recommendation Engine

We created a custom class instantiating a Scotch recommendation engine object. The recommendation either takes in a Scotch name within the corpus or a free text description of Scotch tasting notes. In the latter case, the engine processes the free text using the filtered dictionary and trained gensim phraser and then uses the trained LDA model to create a taste group breakdown for the free text tasting notes. 

Top closest recommendations are produced by cosine similarity on topic (taste group) vectors. Details of the implementation can be found here: <br>

[Scotch recommender custom class](https://github.com/admveen/ScotchNLP/blob/master/src/ScotchRecommender.py) <br>

Acknowledgements 
------------

Special thanks to Max Sop for guidance throughout the course of this project and for invaluable suggestions on visualizations for topic modeling and Scotch topic vector comparisons.
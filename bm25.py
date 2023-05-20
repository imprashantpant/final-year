import math
import re
from nltk.corpus import stopwords    


import nltk
nltk.download('stopwords')

import math
import numpy as np
from multiprocessing import Pool, cpu_count



class BM25:
    def __init__(self, corpus, tokenizer=None):
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.tokenizer = tokenizer
        self.number = {}
        self.allWords = []
        # self.bmValues = {}

        if tokenizer:
            corpus = self._tokenize_corpus(corpus)

        nd = self._initialize(corpus)
        self._calc_idf(nd)

    def getAllWords(self):
        self.allWords = list(self.number.keys())




    def _initialize(self, corpus):
        nd = {}  
        num_doc = 0
        for document in corpus:
            self.doc_len.append(len(document))
            num_doc += len(document)

            frequencies = {}
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.doc_freqs.append(frequencies)

            for word, freq in frequencies.items():
                try:
                    nd[word]+=1
                except KeyError:
                    nd[word] = 1

            self.corpus_size += 1

        self.avgdl = num_doc / self.corpus_size
        
        # print(nd) 
        #in How many documents does one word comes? Total count of words in documents. 
        self.number = nd
        return nd
    def numberDocument(self):
        return self.number

    def _tokenize_corpus(self, corpus):
        pool = Pool(cpu_count())
        tokenized_corpus = pool.map(self.tokenizer, corpus)
#         print(tokenized_corpus)
        return tokenized_corpus

    def _calc_idf(self, nd):
        raise NotImplementedError()

    def get_scores(self, query):
        raise NotImplementedError()

    def get_batch_scores(self, query, doc_ids):
        raise NotImplementedError()

    def get_top_n(self, query, documents, n=5):

        assert self.corpus_size == len(documents) 
        # "The documents given don't match the index corpus!"

        scores = self.get_scores(query)
        top_n = np.argsort(scores)[::-1][:n]
        return [documents[i] for i in top_n]

class BM25Okapi(BM25):
    def __init__(self, corpus, tokenizer=None, k1=1.5, b=0.75, epsilon=0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        super().__init__(corpus, tokenizer)
        
    def frequency_matrix(self):
        #this value is the frequency of the words in one document. 
        return self.doc_freqs
  
    def idfs_values(self):
        return self.idf
    

    def _calc_idf(self, nd):
      
        # Calculates frequencies of terms in documents and in corpus.
        # This algorithm sets a floor on the idf values to eps * average_idf
        
        # collect idf sum to calculate an average idf for epsilon value
        idf_sum = 0
        # collect words with negative idf to set them a special epsilon value.
        # idf can be negative if word is contained in more than half of documents
        negative_idfs = []
        for word, freq in nd.items():
            idf = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)
        self.average_idf = idf_sum / len(self.idf)

        eps = self.epsilon * self.average_idf
#         print("negative", negative_idfs)
        for word in negative_idfs:
            self.idf[word] = eps
        
        return self.idf
            # print(word, eps)

## creating word frequency

def create_frequency_matrix(sentences):
    frequency_matrix = {}
    # stopWords = set(stopwords.words("Nepali"))

    for sent in sentences:
        freq_table = {}
        words=sent.split()
        for word in words:
            # if word in stopWords:
            #     continue

            if word in freq_table:
                freq_table[word] += 1
            elif word in words:
                freq_table[word] = 1

        frequency_matrix[sent[:10]] = freq_table

    return frequency_matrix

# """## creating term frequency matrix - BM25 Algorithm

# """

def create_tf_matrix(freq_matrix,sents, k = 1.2, b=0.75):
    tf_matrix = {}
    avgdl = sum(len(s) for s in sents) / len(sents)
    

    for sent, f_table in freq_matrix.items():
        tf_table = {}
        

        count_words_in_sentence = len(f_table)
        for word, count in f_table.items():
            tf_table[word] = ((count * (k+1))/ (count + k * (1-b+b*count_words_in_sentence)/avgdl))

        tf_matrix[sent] = tf_table

    return tf_matrix

# """## TF-IDF Matrix"""

def create_tf_idf_matrix(tf_matrix, vocabulary):
    tf_idf_matrix = {}

    for sent, f_table in tf_matrix.items():
      tf_idf_table = {}
      for word, value in f_table.items():
        idfValue = vocabulary.get(word)
        idfValue = idfValue if idfValue else 0.8
        tf_idf_table[word] = float(value * idfValue)
      tf_idf_matrix[sent] = tf_idf_table
    return tf_idf_matrix

# """## Sentence Scoring"""

def sentence_scores(tf_idf_matrix) -> dict:
    

    sentenceValue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0

        count_words_in_sentence = len(f_table)
        for word, score in f_table.items():
            total_score_per_sentence += score
        if count_words_in_sentence !=0:
            sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence
        else:
            sentenceValue[sent]=0
    return sentenceValue

# """## Finding Average Value"""

def find_average_score(sentenceValue) -> int:
    sumValues = 0
    for entry in sentenceValue:
        sumValues += sentenceValue[entry]

    # Average value of a sentence from original summary_text
    average = (sumValues / len(sentenceValue))

    return average

# """## Generate Summary"""

def generate_summary(sentences, sentenceValue, threshold):
    sentence_count = 0
    summary = []

    for sentence in sentences:
        if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] >= (threshold):
            summary.append(sentence)
            sentence_count += 1

    return summary


def start_prediction_bm25(originalText, docsList, userthresholdValue):
    text = originalText
    sents = []
   

    docs1= "प्राणायाम रोग निवारणको एक औषधि नै हो भन्दा पनि हुन्छ । दैनिक गरिने प्राणायामले मानिसको ७२ हजार नसामा रक्तप्रवाह राम्रो गराउन मद्दत गर्छ । यद्यपि प्राणायामका धेरै प्रकार छन् । तर यहाँ हामी ती प्राणायामको मात्र चर्चा गर्नेछौं । जसलाई बालबालिका, युवायुवती, वृद्धवृद्धा सबैले सहज रुपमा गर्न सक्छन् ।"
    docs2 = "उच्च रक्तचाप मूलतः जीवनशैलीसँग सम्बन्धित समस्या हो । त्यसो त वंशाणुगत रुपमा पनि कतिपयलाई उच्च रक्तचाप हुने गर्छ । यद्यपि खराब खानपान, जीवनशैली, मानसिक विकारले नै उच्च रक्तचापको मूल कारक बन्ने गरेको छ । के त्यसो भए जीवनशैली सुधार गरेर रक्तचाप सन्तुलित राख्न सकिएला ?"
    docs3 = "शारीरिक तथा मानसिक रुपमा स्वस्थ रहन योग उत्तम विकल्पमध्ये पर्छ । पछिल्लो समय योगप्रति धेरै मानिसको आकर्षण बढ्दै गएको छ ।पहिलो पटक योग गर्न जानेहरुलाई भने कसरी सुरु गर्ने भन्ने अलमल हुन सक्छ । हुन त अहिले युट्युब लगायतमा भिडियो हेरेर पनि योग गर्न सकिन्छ । भिडियो हेरेर आफैं गरे पनि वा यदि योगगुरुसँग सिक्न जाँदै हुनुहुन्छ भने केही कुरामा पक्कै ख्याल गर्नुपर्छ । सामान्य गल्ती गर्दा योगको उल्टो प्रभाव पर्न सक्छ ।१. श्वासप्रश्वासको गतिमा ध्यान दिने योगमा श्वासप्रश्वासले महत्त्वपूर्ण भूमिका खेल्छ । पहिलो पटक योग गर्ने व्यक्तिले कुनै प्रशिक्षकको निर्देशन बिना योग गरिरहेका छन् भने आसन गर्दा श्वासप्रश्वासको गतिमा ध्यान दिनुपर्छ । धेरैलाई योग गर्दा मुखबाट सास फेर्न हुँदैन भन्ने कुरामा ध्यान नहुन सक्छ । आसनमा कहिले सास लिने र कहिले छाड्ने गर्नुपर्छ भन्ने जानकारी हुनुपर्छ । त्यस्तै, शरीर फैलिंदा सास लिने र शरीर खुम्चिंदा सास छोड्ने गर्दा प्रभावकारी हुन्छ ।२. खाली पेटमा योग पहिलोपटक योग गर्न जाँदै हुनुहुन्छ भने खाली पेटमा मात्र अभ्यास गर्नुपर्छ भन्ने कुरामा ध्यान दिनुपर्छ । बिहानको खाजा वा खाना खाने बित्तिकै योग गर्नु हुँदैन । यदि बिहान योग गर्ने समय छैन तर दिनको एकपटक योग गर्ने योजना बनाउनुभएको छ भने कम्तीमा दुई घण्टा जति खानेकुरा खानु हुँदैन । योग गरेपछि तुरुन्तै खाना नखानुहोस् । बरु शरीरलाई आराम दिनुहोस् र त्यसपछि खानुहोस् ।३. कसिलो पहिरन नलगाउने योग गर्दा आरामदायी लुगा लगाउनुपर्छ । ताकि शरीरलाई तन्काउँदा सहज होस् । टाइट लुगा लगाउनाले शरीरको मांसपेशी लचिलो हुन पाउँदैन र तन्किंदा लुगा च्यातिने डर हुन्छ । अर्कोतर्फ टाइट कपडाको कारण तपाईंको एकाग्रताका साथ योगमा ध्यान दिन सक्नुहुन्न ।४. सिधै अभ्यास नगर्ने पहिलो पटक सिधै योगासनमा जानु हुँदैन । योगासन वा प्राणायाम गर्नुपूर्व शरीर र मनको तयारीको लागि हल्का व्यायाम गरेर शरीरलाई वार्मअप गर्नुपर्छ । त्यसपछि मात्र योग गर्न शरीर तयार रहन्छ ।५. कठिन योग अभ्यास नगर्ने पहिलो पटक योग गर्दै हुनहुन्छ भने सरल र आधारभूत योगासनबाट सुरु गर्नुपर्छ । कठिन योगासन गर्न खोज्दा चोटपटकको जोखिम हुन सक्छ । र, योग वियोगमा परिणत हुन सक्छ । त्यसैले कुनै पनि योगाभ्यासको लागि सही आसन कुन हो भनेर सही रूपमा जान्नुपर्छ । किनकि शरीर, मौसम, रोग र आवश्यकता अनुसार योग आसन र प्राणयाम फरक–फरक हुन सक्छन् ।त्यसैले त भनिन्छ, योगाभ्यासको लागि यसका जानकारसँग आवश्यक परामर्श गरेर मात्र सुरु गर्नुपर्छ ।"
    # len(text)
    docs = docsList

    #Listed Documents
    listedSentence = []
    count = 0
    for doc in docs:
        listedSentence.append(re.split(r' *[।?!]+[\'"\)\]]* *', doc))

    #Create a Vocabulary

    tokenized_corpus = [doc.split(" ") for doc in docs]

    bm25 = BM25Okapi(tokenized_corpus)

    vocabulary = bm25.idfs_values()
    # print(vocabulary)

    #Vocabulary Ends Here


    # print(text)

    #The Text to be Summarized

    sents = re.split(r' *[।?!]+[\'"\)\]]* *', text)
    #sents needs to be defined gloablly remember.

    # documents_size = len(sents)
    # documents_size



    #We are creating Frequency Matrix Here
    freq_matrix = create_frequency_matrix(sents)

    # print(freq_matrix)

    #Now We create TF-Matrix

    tf_matrix = create_tf_matrix(freq_matrix, sents)


    #We create Tf-IDF Matrix Here
    tf_idf_matrix = create_tf_idf_matrix(tf_matrix, vocabulary)



    # """## Sentence Scores"""
    sentence_scores_value = sentence_scores(tf_idf_matrix)



    #Calculating Threshold
    threshold = find_average_score(sentence_scores_value)


    #Take Out The Summary Here
    summary = ' । '.join(generate_summary(sents, sentence_scores_value, userthresholdValue*threshold ))
    summary += ' । '
    return summary
    # print(summary)

    # len(summary)

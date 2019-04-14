from json import load
import pickle
import numpy as np
from os.path import join
from sklearn.feature_extraction.text import TfidfVectorizer


def tokenize(text):
    tokenized_review = re.findall(r'[a-z]+', text.lower())
    return [x for x in tokenized_review if len(x)>2]

def build_vectorizer(max_features, stop_words, max_df=0.65, min_df=45, norm='l2', tokenizer=tokenize):
    """Returns a TfidfVectorizer object with the above preprocessing properties.

    Params: {max_features: Integer,
             max_df: Float,
             min_df: Float,
             norm: String,
             stop_words: String}
    Returns: TfidfVectorizer
    """
    return TfidfVectorizer(max_features=max_features, min_df=min_df, max_df=max_df, stop_words=stop_words, norm=norm, tokenizer=tokenize)
#filter by size
def filter_sizes(min_size, max_size, min_price, max_price, car_size, car_price):
    return car_size >= min_size and car_size <= max_size and car_price >= min_price and car_price <= max_price
#cosine similarity
def get_sim(car, query):
    numerator = np.dot(car, query)
    norm1 = np.linalg.norm(car)
    norm2 = np.linalg.norm(query)
    sim = numerator/(1 + norm1*norm2)
    return sim

class Searcher:
    def __init__(self, data_path="data"):

        with open(join(data_path, 'unfiltered_list.pkl'), 'rb') as unfiltered, \
            open(join(data_path, 'index_to_vocab.pkl'), 'rb') as itv, \
            open(join(data_path, 'data.json')) as all_data:
            self.all_data = load(all_data)
            self.unfiltered_list = pickle.load(unfiltered)
            self.index_to_vocab = pickle.load(itv)
            self.vocab_to_index = {self.index_to_vocab[k]:int(k) for k in self.index_to_vocab}
            self.cars_reverse_index = {car[0]: i for i, car in enumerate(self.unfiltered_list)}

        n_feats = 4000
        self.doc_by_vocab = np.empty([len(self.all_data), n_feats])

        tfidf_vec = build_vectorizer(n_feats, "english")
        doc_by_vocab = tfidf_vec.fit_transform([d['Appended Reviews'] for d in self.all_data]).toarray()

    def search(self, min_size, max_size, min_price, max_price, query):
        # print("enter method")
        truncated_list_by_size = [x[0] for x in self.unfiltered_list if filter_sizes(min_size, max_size, min_price, max_price, x[1], x[2])]

        # print("start idf_dict lookups")
        # tf_idf_query = np.zeros(len(self.keywords))
        # for t in query:
        #     print("\t" + t)
        #     tf_idf_query[self.vocab_to_index[t]] = self.idf_dict[t]
        tf_idf_query = self.tf.transform(query)

        # print("make similarity dict")
        similarity_dict = {}
        for car in truncated_list_by_size:
            car_index = self.cars_reverse_index[car]
            sim = get_sim(self.doc_by_vocab[car_index] , tf_idf_query)
            similarity_dict[car] = sim

        # print("get sorted results")
        sorted_results = sorted(similarity_dict, key=lambda x:x[0], reverse = True)

        # print(sorted_results[0:10])
        return sorted_results[0:10]

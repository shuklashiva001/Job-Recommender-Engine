import re
from nltk.corpus import stopwords
import pandas as pd
import string
import pdftotext
from settings import overall_skills_dict, education, overall_dict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import settings
import metaphone



jobs_info_data_frame = pd.DataFrame()
class Similarity_Calculator:
    def __init__(self, extractor):
        self.extractor = extractor
        self.job_list = extractor.job_list
        self.jobs_info_data_frame = extractor.jobs_info_data_frame

    def calculate_jaccard_similarity(self, x_set, y_set):
        '''
        Jaccard similarity or intersection over union measures similarity 
        between finite sample sets,  and is defined as size of intersection 
        divided by size of union of two sets. 
        Jaccard calculation is modified from 
        https://towardsdatascience.com/overview-of-text-similarity-metrics-3397c4601f50
        Input: 
            x_set (set)
            y_set (set)
        Output: 
            Jaccard similarity score
        '''         
        intersection = x_set.intersection(y_set)
        if (len(x_set) + len(y_set) - len(intersection)) != 0:
        	return float(len(intersection)) / (len(x_set) + len(y_set) - len(intersection))
        else:
        	return 0
    
    def get_cosine_sim(self,x_list,y_list):
        '''
        Cosine similarity calculates similarity by measuring the cosine of angle between two vectors.
        Cosine calculation is modified from 
        https://towardsdatascience.com/overview-of-text-similarity-metrics-3397c4601f50
        Input: 
            x_list (list)
            y_list (list)
        Output: 
            Cosine similarity score
        '''
        combined_list = x_list
        for element in y_list:
            combined_list.append(element)
        vectors = self.get_vectors(combined_list)
        x_vector = vectors[0:1]
        y_vector = vectors[1:]
        print(cosine_similarity(x_vector,y_vector))
        return cosine_similarity(x_vector,y_vector)
    
    def get_vectors(self,text):
        vectorizer = CountVectorizer(text)
        vectorizer.fit(text)
        return vectorizer.transform(text).toarray()    

    def calculate_similarity(self, resume_keywords, location=None):
        '''
        Calculate similarity between keywords from resume and job posts
        Input: 
            resume_keywords (list): resume keywords
            location (str): city to search jobs
        Output: 
            top_match (DataFrame): top job matches
        '''         
        num_jobs_return = settings.count_of_recommendations
        similarity = []
        j_info = self.jobs_info_data_frame.loc[self.jobs_info_data_frame['location']==location].copy() if len(location)>0 else self.jobs_info_data_frame.copy()
        if j_info.shape[0] < num_jobs_return:        
            num_jobs_return = j_info.shape[0]  
        for job_skills in j_info['keywords']:
            similarity.append(self.calculate_jaccard_similarity(resume_keywords, job_skills))
        j_info['similarity'] = similarity
        top_match = j_info.sort_values(by='similarity', ascending=False).head(num_jobs_return)
        return top_match
      


class Extractor:
    def __init__(self, jobs_list):
        self.job_list = jobs_list
        self.jobs_info_data_frame = pd.DataFrame(jobs_list)

    def extract_keyword_from_text(self, text):
        '''
        Tokenize webpage text and extract keywords
        Input:
            text (str): text to extract keywords from
        Output:
            keywords (list): keywords extracted and filtered by pre-defined dictionary
        '''
        text = re.sub("[^a-zA-Z+3]", " ", text)
        text = text.lower().split()
        cleared_text = []
        for punctuation in string.punctuation:
            for i in range(0, len(text)):
                text[i].replace(punctuation, ' ')
                cleared_text += text[i].split()
        text = cleared_text
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = list(set(text))
        keywords = [str(word) for word in text if (word.lower() in overall_dict)]
        keywords = []
        for word in text:
            for skill in overall_dict:
                if word.lower() == skill.lower() or metaphone.doublemetaphone(word) == metaphone.doublemetaphone(skill):
                    keywords.append(skill)
        return keywords

    def count(self, keywords, counter):
        '''
        Count frequency of keywords
        Input:
            keywords (list): list of keywords
            counter (Counter)
        Output:
            keyword_count (DataFrame index:keyword value:count)
        '''
        keyword_count = pd.DataFrame(columns=['Freq'])
        for each_word in keywords:
            keyword_count.loc[each_word] = {'Freq': counter[each_word]}
        return keyword_count
    def extract_jobs_keywords(self):
        '''
        Extract skill keywords from job descriptions and add a new column
        Input:
            None
        Output:
            None
        '''
        self.jobs_info_data_frame['keywords'] = [self.extract_keyword_from_text(job_desc) for job_desc in
                                         self.jobs_info_data_frame['desc']]

    def extract_resume_keywords(self, resume_pdf):
        '''
        Extract key skills from a resume
        Input:
            resume_pdf (str): path to resume Pdf file
        Output:
            resume_skills (DataFrame index:keyword value:count): keywords counts
        '''
        resume_file = open(resume_pdf, 'rb')
        resume_reader = pdftotext.PDF(resume_file)
        resume_content = [page for page in resume_reader]
        resume_keywords = [self.extract_keyword_from_text(page) for page in resume_content]
        resume_freq = Counter()
        f = [resume_freq.update(item) for item in resume_keywords]
        resume_skills = self.count(overall_skills_dict, resume_freq)

        return (resume_skills[resume_skills['Freq'] > 0])

class Analyzer:
    def __init__(self, extractor):
        self.extractor = extractor
        self.jobs_info_data_frame = extractor.jobs_info_data_frame

    def analyze_data_and_plot_graph(self):
        '''
        Exploratory data analysis
        Input:
            None
        Output:
            None
        '''
        doc_freq = Counter()
        f = [doc_freq.update(item) for item in self.jobs_info_data_frame['keywords']]
        overall_skills_data_frame = self.extractor.count(overall_skills_dict, doc_freq)
        overall_skills_data_frame['Freq_perc'] = (overall_skills_data_frame['Freq']) * 100 / self.jobs_info_data_frame.shape[0]
        overall_skills_data_frame = overall_skills_data_frame.sort_values(by='Freq_perc', ascending=False)
        plt.figure(figsize=(14, 8))
        overall_skills_data_frame.iloc[0:30, overall_skills_data_frame.columns.get_loc('Freq_perc')].plot.bar()
        plt.title('Percentage of Required Data Skills in Data Scientist/Engineer/Analyst Job Posts')
        plt.ylabel('Percentage Required in Jobs (%)')
        plt.xticks(rotation=30)
        plt.show()
        all_keywords_str = self.jobs_info_data_frame['keywords'].apply(' '.join).str.cat(sep=' ')
        slide_word_cloud = WordCloud(background_color="white").generate(all_keywords_str)
        plt.figure()
        plt.imshow(slide_word_cloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        data_frame_edu = self.extractor.count(education, doc_freq)
        data_frame_edu.loc['bachelor', 'Freq'] = data_frame_edu.loc['bachelor', 'Freq'] + data_frame_edu.loc[
            'undergraduate', 'Freq']
        data_frame_edu.drop(labels='undergraduate', axis=0, inplace=True)
        data_frame_edu['Freq_perc'] = (data_frame_edu['Freq']) * 100 / self.jobs_info_data_frame.shape[0]
        data_frame_edu = data_frame_edu.sort_values(by='Freq_perc', ascending=False)
        plt.figure(figsize=(14, 8))
        data_frame_edu['Freq_perc'].plot.bar()
        plt.title('Percentage of Required Education out of All Job Posts')
        plt.ylabel('Percentage Required in Jobs (%)')
        plt.xticks(rotation=0)
        plt.show()
        plt.figure(figsize=(8, 8))
        self.jobs_info_data_frame['location'].value_counts().plot.pie(autopct='%1.1f%%', textprops={'fontsize': 10})
        plt.title(
            'Total {} posted jobs in last {} days'.format(
                self.jobs_info_data_frame.shape[0], settings.old_post_limit_days))
        plt.ylabel('')
        plt.show()

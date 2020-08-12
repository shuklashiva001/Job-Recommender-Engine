"""
Build a simple data-science-skill-keyword-based job recommendation engine, 
which match keywords from resume to data science jobs in major Canadian cities.
Step 1: Scrape "data scientist/engineer/analyst" jobs from indeed.co.in
Step 2: Tokenize and extract skill keywords from job descriptions
Step 3: Tokenize and extract skill keywords from resume
Step 4: Calculate Jaccard similarity of keywords from posted jobs and resume, 
        and recommend top 5 matches 
"""
import sys 
import settings, indeed_web_scrapper
from algorithms_and_extracters import Extractor, Similarity_Calculator, Analyzer

def main():
    location = ''
    if (len(sys.argv) > 1):
        if (sys.argv[1] in settings.indian_locations_to_search):
            location = sys.argv[1]
        else:
            sys.exit('*** Please try again. *** \nEither leave it blank or input a city from this list:\n{}'.format('\n'.join(settings.indian_locations_to_search)))
    jobs_info = indeed_web_scrapper.load_job_info_using_location(location)
    extractor = Extractor(jobs_info)
    extractor.extract_jobs_keywords()
    if (len(sys.argv) == 1):
        Analyzer(extractor).analyze_data_and_plot_graph()
    skill_from_resume = extractor.extract_resume_keywords(settings.resume_location)
    top_job_matches = Similarity_Calculator(extractor).calculate_similarity(skill_from_resume.index, location)
    top_job_matches.to_csv(settings.save_recommendations + location + '.csv', index=False)
    print('Recommendations saved in a file in data folder :)')
     
if __name__ == "__main__": 
    main()
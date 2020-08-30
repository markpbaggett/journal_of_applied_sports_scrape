from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import os


class IssueReviewer:
    def __init__(self, driver, issue):
        self.driver = driver
        self.issue = issue
        self.articles = self.get_articles()

    def get_articles(self):
        self.driver.get(self.issue)
        articles = self.driver.find_elements_by_xpath('//div[@class="tocTitle"]/a')
        return [(article.text, article.get_attribute('href')) for article in articles]


class ArticleReviewer:
    def __init__(self, driver, article_uri):
        self.driver = driver
        self.article_uri = article_uri
        self.dom = self.driver.get(article_uri)
        self.metadata = self.get_metadata()

    def get_metadata(self):
        metadata = {}
        metadata['title'] = self.driver.title.split('|')[0]
        metadata['full_text'] = self.get_pdf_full_text()
        metadata['keyword'] = self.get_keywords()
        return metadata

    def get_pdf_full_text(self):
        return self.driver.find_element_by_xpath('//meta[@name="citation_pdf_url"]').get_attribute('content')

    def get_keywords(self):
        keywords = ""
        keyword_elements = self.driver.find_elements_by_xpath('//meta[@name="citation_keywords"]')
        for element in keyword_elements:
            keywords += f"{element.get_attribute('content')}, "
        return keywords[:-2]


if __name__ == "__main__":
    articles = []
    pages = ('https://js.sagamorepub.com/jasm/issue/archive', 'https://js.sagamorepub.com/jasm/issue/archive?issuesPage=2#issues')
    options = Options()
    options.add_argument('--headless')
    x = Chrome(executable_path=os.path.abspath("/home/mark/bin/chromedriver"), options=options)
    x.get('https://js.sagamorepub.com/jasm/issue/archive?issuesPage=2#issues')
    all_anchors = x.find_elements_by_xpath('//a')
    issues = [anchor.get_attribute('href') for anchor in all_anchors if anchor.text.startswith('Vol')]
    for issue in issues:
        reviewer = IssueReviewer(x, issue)
        #print(reviewer.articles)
        for article in reviewer.articles:
            new_review = ArticleReviewer(x, article[1])
            print(new_review.metadata)

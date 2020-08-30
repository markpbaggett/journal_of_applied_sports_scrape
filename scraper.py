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
        

if __name__ == "__main__":
    pages = ('https://js.sagamorepub.com/jasm/issue/archive', 'https://js.sagamorepub.com/jasm/issue/archive?issuesPage=2#issues')
    options = Options()
    options.add_argument('--headless')
    x = Chrome(executable_path=os.path.abspath("/home/mark/bin/chromedriver"), options=options)
    x.get('https://js.sagamorepub.com/jasm/issue/archive?issuesPage=2#issues')
    all_anchors = x.find_elements_by_xpath('//a')
    issues = [anchor.get_attribute('href') for anchor in all_anchors if anchor.text.startswith('Vol')]
    for issue in issues:
        reviewer = IssueReviewer(x, issue)
        print(reviewer.articles)


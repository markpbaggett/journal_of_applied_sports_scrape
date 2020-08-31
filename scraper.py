from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import os
import csv


class IssueReviewer:
    def __init__(self, driver, issue):
        self.driver = driver
        self.issue = issue
        self.articles = self.get_articles()

    def get_articles(self):
        self.driver.get(self.issue)
        articles = self.driver.find_elements_by_xpath('//div[@class="tocTitle"]/a')
        return [(article.text, article.get_attribute("href")) for article in articles]


class ArticleReviewer:
    def __init__(self, driver, article_uri):
        self.driver = driver
        self.article_uri = article_uri
        self.dom = self.driver.get(article_uri)
        self.metadata = self.get_metadata()

    def get_metadata(self):
        metadata = {}
        metadata["title"] = self.driver.title.split("|")[0]
        metadata["full_text"] = self.get_pdf_full_text()
        metadata["keyword"] = self.get_keywords()
        metadata["abstract"] = self.get_abstract()
        authors = self.get_authors()
        i = 1
        for author in authors:
            metadata[f"author_{i}"] = author
            i += 1
        i += 1
        while i < 7:
            metadata[f"author_{i}"] = ""
            i += 1
        metadata["date_submitted"] = self.get_date_submitted()
        metadata["date_modified"] = self.get_date_modified()
        metadata["date_issued"] = self.get_date_submitted()
        metadata["journal_name"] = self.get_journal_name()
        metadata["issn"] = self.get_issn()
        metadata["issue"] = self.get_issue()
        metadata["volume"] = self.get_volume()
        metadata["identifier"] = self.get_identifier()
        return metadata

    def get_pdf_full_text(self):
        try:
            return self.driver.find_element_by_xpath(
                '//meta[@name="citation_pdf_url"]'
            ).get_attribute("content")
        except NoSuchElementException:
            where_it_lives = self.driver.find_element_by_xpath(
                '//meta[@name="DC.Identifier.URI"]'
            ).get_attribute("content")
            return f"Missing Download at {where_it_lives}"

    def get_keywords(self):
        keywords = ""
        keyword_elements = self.driver.find_elements_by_xpath(
            '//meta[@name="citation_keywords"]'
        )
        for element in keyword_elements:
            keywords += f"{element.get_attribute('content')}, "
        return keywords[:-2]

    def get_abstract(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Description"]'
        ).get_attribute("content")

    def get_authors(self):
        authors = []
        author_elements = self.driver.find_elements_by_xpath(
            '//meta[@name="DC.Creator.PersonalName"]'
        )
        for author in author_elements:
            authors.append(author.get_attribute("content"))
        return authors

    def get_date_submitted(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Date.dateSubmitted"]'
        ).get_attribute("content")

    def get_date_modified(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Date.modified"]'
        ).get_attribute("content")

    def get_date_issued(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Date.issued"]'
        ).get_attribute("content")

    def get_journal_name(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Source"]'
        ).get_attribute("content")

    def get_issn(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Source.ISSN"]'
        ).get_attribute("content")

    def get_issue(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Source.Issue"]'
        ).get_attribute("content")

    def get_volume(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Source.Volume"]'
        ).get_attribute("content")

    def get_identifier(self):
        return self.driver.find_element_by_xpath(
            '//meta[@name="DC.Identifier"]'
        ).get_attribute("content")


def build_csv(list_of_articles):
    with open("output.csv", "w") as csvfile:
        fieldnames = [
            "title",
            "full_text",
            "keyword",
            "abstract",
            "author_1",
            "author_2",
            "author_3",
            "author_4",
            "author_5",
            "author_6",
            "author_7",
            "date_submitted",
            "date_modified",
            "date_issued",
            "journal_name",
            "issn",
            "issue",
            "volume",
            "identifier",
        ]
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, delimiter="|", quotechar='"'
        )
        writer.writeheader()
        for article in list_of_articles:
            writer.writerow(article)


if __name__ == "__main__":
    articles = []
    pages = (
        "https://js.sagamorepub.com/jasm/issue/archive",
        "https://js.sagamorepub.com/jasm/issue/archive?issuesPage=2#issues",
    )
    options = Options()
    options.add_argument("--headless")
    x = Chrome(
        executable_path=os.path.abspath("/home/mark/bin/chromedriver"), options=options
    )
    for page in pages:
        x.get(page)
        all_anchors = x.find_elements_by_xpath("//a")
        issues = [
            anchor.get_attribute("href")
            for anchor in all_anchors
            if anchor.text.startswith("Vol")
        ]
        for issue in issues:
            reviewer = IssueReviewer(x, issue)
            for article in reviewer.articles:
                new_review = ArticleReviewer(x, article[1])
                articles.append(new_review.metadata)
    build_csv(articles)

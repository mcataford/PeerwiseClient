from bs4 import BeautifulSoup

import requests
import re

class PeerwiseClient():

  LOGIN_URL = "https://peerwise.cs.auckland.ac.nz/at/?"
  BASE_URL = "https://peerwise.cs.auckland.ac.nz/course/main.php"

  def __init__(self):
    self.session = requests.Session()

  def auth(self, uname, pwd, inst):
    post_data = {
      "user": uname,
      "pass": pwd,
      "inst_shortcode": inst,
      "cmd": "login",
      "redirect": ""
    }

    response = self.session.post(self.LOGIN_URL + inst, data=post_data, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "lxml")

    #Get course codes from the dashboard
    course_codes = list()

    for course_listing in soup.select("td.courseListingNameStyle a"):
      course_codes.append(re.sub('[^0-9]','', course_listing.get("href")))
    
    return course_codes

  def select_course(self, course_code):
    get_data = {
      "course_id": course_code
    }

    return self.session.post(self.BASE_URL, data=get_data, headers={"User-Agent": "Mozilla/5.0"})

  def get_user_scores(self, course_code):

    resp = self.select_course(course_code)
    soup = BeautifulSoup(resp.text, "lxml")

    scores = dict()

    for div in soup.select("div.karmaDisplay > div"):
      heading = div.select("b")[0].text.replace(" score", "")
      score = div.select("a.info span")[0].text

      scores[heading] = int(score)

    return scores

  def get_questions(self, course_code, mode):

    self.select_course(course_code)

    questions = list()

    questions_left = True
    offset = 0

    while questions_left:

      cmd = None

      if mode == "answered":
        cmd = "showAnsweredQuestions"
      elif mode == "unanswered":
        cmd = "showUnansweredQuestions"
      elif mode =="own":
        cmd = "showUserQuestions"

      url_params = "?cmd={}&offset={}".format(cmd, offset)

      resp = self.session.post(self.BASE_URL + url_params, headers={"User-Agent": "Mozilla/5.0"})
      soup = BeautifulSoup(resp.text, "lxml")

      questions_left = False

      for question in soup.select("table#basicTable tr"):

        if question.select("td.spaceLeft"):
          print(len(questions))
          questions_left = True

          question_data = dict()

          question_data["id"] = int(re.sub('[^0-9]','', question.select(".spaceLeft a")[0].get("href")))
          question_data["preview"] = question.select("#previewTextFormat")[0].text

          questions.append(question_data)

      offset += 10

    return questions

  def get_own_questions(self, course_code):
    return self.get_questions(course_code, "own")

  def get_unanswered_questions(self, course_code):
    return self.get_questions(course_code, "unanswered")

  def get_answered_questions(self, course_code):
    return self.get_questions(course_code, "answered")

from bs4 import BeautifulSoup

import requests
import re

class PeerwiseClient():

  LOGIN_URL = "https://peerwise.cs.auckland.ac.nz/at/?"
  BASE_URL = "https://peerwise.cs.auckland.ac.nz/course/main.php"

  def __init__(self):
    self.session = requests.Session()

  def auth(self, uname, pwd, inst):
    """
    Gets the session cookies and creates the client's session object.
    @param uname string Username
    @param pwd string Password
    @param inst string Institution shortcode, as defined by Peerwise (mcgill_ca for McGill)
    @return List of course codes attached to the account.
    """
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
    """
    Selects a course, necessary to access questions or any course-related data. Modifies the session.
    @param course_code int Course identifier
    @return The soup of the user dashboard page, if needed
    """

    get_data = {
      "course_id": course_code
    }

    return self.session.post(self.BASE_URL, data=get_data, headers={"User-Agent": "Mozilla/5.0"})

  def get_user_scores(self, course_code):
    """
    Gets the user's reputation and answer scores.
    @param course_code int Course code.
    @return Dict containing the scores.
    """

    resp = self.select_course(course_code)
    soup = BeautifulSoup(resp.text, "lxml")

    scores = dict()

    for div in soup.select("div.karmaDisplay > div"):
      heading = div.select("b")[0].text.replace(" score", "")
      score = div.select("a.info span")[0].text

      scores[heading] = int(score)

    return scores

  def get_questions(self, course_code, mode):
    """
    Scrapes the questions from the selected listing (using mode)
    @param course_code int Course code
    @param mode string Selects unanswered, answered or own questions
    @return List of question dicts.
    """

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
          questions_left = True

          question_data = dict()

          cells = question.select("td")

          question_data["id"] = int(re.sub('[^0-9]','', question.select(".spaceLeft a")[0].get("href")))
          question_data["preview"] = question.select("#previewTextFormat")[0].text
          question_data["author_reputation"] = int(cells[2].text)
          question_data["answered_on"] = cells[3].text

          question_status_img = cells[4].select("img")[0].get("src")

          if "fullTick" in question_status_img:
            question_data["status"] = "Success"
          elif "authorTick" in question_status_img:
            question_data["status"] = "Changed"
          else:
            question_data["status"] = "Failed"
          
          question_data["num_answers"] = int(cells[6].text)
          question_data["help_requests"] = int(cells[7].text)
          question_data["recent_comment"] = cells[8].text
          question_data["num_comments"] = int(cells[9].text)
          question_data["difficulty"] = cells[10].text
          question_data["rating"] = float(cells[11].text)

          questions.append(question_data)

      offset += 10

    return questions

  def get_question_details(self, question_code, mode):
    """
    Queries the full question details for the question code attached.
    @param question_code int Question ID
    @param mode string Either Unanswered, answered of self question.
    @return Dictionary containing the question data
    """

    cmd = None

    if mode == "answered":
      cmd = "viewAnsweredQuestionDetail"
    elif mode == "unanswered":
      cmd = "viewUnansweredQuestionDetail"
    elif mode == "own":
      cmd = "viewUserQuestionDetail"

    url_params = "?cmd={}&id={}".format(cmd, question_code)

    resp = self.session.get(self.BASE_URL + url_params, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "lxml")


    question_data = dict()

    question_data["text"] = soup.select("#questionDisplay")[0].text
    question_data["choices"] = list()

    for option in soup.select("#displayQuestionTable tr"):
      if option.select("#alternativesDisplay"):
        question_data["choices"].append(option.select("#alternativesDisplay")[0].text)
        
        if mode == "answered":
          question_data["selected"] = option.select("td.displayGraph")[0].text
          question_data["confirmed"] = option.select("td.displayGraph")[1].text


    return question_data


  def get_own_questions(self, course_code):
    """
    Gets the user's own questions, uses get_question and mode=="own"
    @param course_code int Course code.
    @return List of dict containing the questions
    """
    return self.get_questions(course_code, "own")

  def get_unanswered_questions(self, course_code):
    """
    Gets the user's unanswered questions, uses get_question and mode=="unanswered"
    @param course_code int Course code.
    @return List of dict containing the questions
    """
    return self.get_questions(course_code, "unanswered")

  def get_answered_questions(self, course_code):
    """
    Gets the user's answered questions, uses get_question and mode=="answered"
    @param course_code int Course code.
    @return List of dict containing the questions
    """
    return self.get_questions(course_code, "answered")

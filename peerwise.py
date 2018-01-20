from bs4 import BeautifulSoup

import requests
import re

from config import USERNAME, PASSWORD, INST_CODE

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

  def get_user_score(self, course_code):
    get_data = {
      "course_id": course_code
    }

    resp = self.session.post(self.BASE_URL, data=get_data, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "lxml")

    scores = dict()

    for div in soup.select("div.karmaDisplay > div"):
      heading = div.select("b")[0].text.replace(" score", "")
      score = div.select("a.info span")[0].text

      scores[heading] = int(score)

    return scores

if __name__ == "__main__":
  
  pw_client = PeerwiseClient()
  course_codes = pw_client.auth(USERNAME, PASSWORD, INST_CODE)

  for course in course_codes:
    scores = pw_client.get_user_score(course)
    print(scores)
    

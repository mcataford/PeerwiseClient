# PeerwiseClient

Python client for the Peerwise peer-quizzing system (https://peerwise.cs.auckland.ac.nz/)

# Motivation

This Python wrapper for the Peerwise peer-quizzing system came out of frustration at the clunkiness of Peerwise's current website and the necessity to use it often for certain courses. The idea is to streamline the process of using the service by using a Python client that can provide greater control over the data (i.e. list of questions, comments, etc) and avoid extraneous fiddling with the website's UI.

# Installing

PeerwiseClient depends mainly on `requests` and `BeautifulSoup`. The dependencies can be installed automatically by using the `requirements.txt` file. You should also have Python 3.5+.

```
pip install -r requirements.txt
```

# Documentation

## Authentication
```python
def auth(self, uname, pwd, inst):
  """
  Gets the session cookies and creates the client's session object.
  @param uname string Username
  @param pwd string Password
  @param inst string Institution shortcode, as defined by Peerwise (mcgill_ca for McGill)
  @return List of course codes attached to the account.
  """
```

The username and password are obtained by registering on Peerwise, and the institution shortcode can be fished directly from Peerwise's login page. The site uses simple session cookies to handle user connections, the cookie is saved in the client.

## Course selection
```python
def select_course(self, course_code):
  """
  Selects a course, necessary to access questions or any course-related data. Modifies the session.
  @param course_code int Course identifier
  @return The soup of the user dashboard page, if needed
  """
```

Peerwise requires the user to select a course before querying for questions. The selection modifies the session data. Once selected, a course can be navigated. This must be reused to navigate another course once done.

## User scores
```python
def get_user_scores(self, course_code):
  """
  Gets the user's reputation and answer scores.
  @param course_code int Course code.
  @return Dict containing the scores.
  """
```

Peerwise keeps track of reputation (based on users answer questions you submitted) and answer (based on your answers) scores. These scores are displayed on the dashboard page.

## Fetching questions

Fetching questions can be done using one of three methods:

```python
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
```

Each is based on the more general `get_questions`, which takes in a `mode` selector. The method is always the same, as the listing pages are built from the same PHP template.


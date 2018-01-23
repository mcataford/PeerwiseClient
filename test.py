from peerwise import PeerwiseClient
from config import USERNAME, PASSWORD, INST_CODE

if __name__ == "__main__":
  
  pw_client = PeerwiseClient()
  course_codes = pw_client.auth(USERNAME, PASSWORD, INST_CODE)

  for course in course_codes:
    ans_q = pw_client.get_answered_questions(course)
    print(pw_client.get_question_details(ans_q[2]["id"], "answered"))
import openpyxl
import pyttsx3
import speech_recognition as sr
import time
import pandas as pd


class AskQuestion:

    
    def ask_questions(question_count, user_score, running,questionList,recognizer,daily_quota,engine,answers,ques):
        # global question_count, user_score, running

        while running and question_count < daily_quota:
            time.sleep(20)  # Wait for 60 seconds before asking the next question
            timeout = 10  # Set a timeout of 10 seconds

            engine.say(f"Question {ques + 1}: {questionList}")
            engine.runAndWait()
            engine.say("You can answer by speaking ")

            # Listen for the user's answer
            with sr.Microphone() as source:
                print(f"Question {ques + 1}: {questionList}")
                engine.say("Now, please tell me your answer.")
                engine.runAndWait()
            running = False

        return True

            

    def start_questions(questionList,answers,engine,ques):
        

        # Initialize speech recognition
        recognizer = sr.Recognizer()

        # Set up the loop
        question_count = 0
        daily_quota = 2

        # Initialize the user's score
        user_score = 0

        # Flag for controlling the loop
        running = False
        
        if not running:
            engine.say("Questionnaire started.")
            engine.runAndWait()
            running = True
            AskQuestion.ask_questions(question_count, user_score, running,questionList,recognizer,daily_quota,engine,answers,ques)
        else:
            engine.say("Questionnaire is already running.")
            engine.runAndWait()

    def stop_questions():
        global running
        engine = pyttsx3.init()
        if running:
            engine.say("Questionnaire stopped.")
            engine.runAndWait()
            running = False
            return True
        else:
            engine.say("Questionnaire is not running.")
            engine.runAndWait()
            return False



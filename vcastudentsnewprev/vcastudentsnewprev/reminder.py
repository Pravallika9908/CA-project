import subprocess
import wolframalpha
import pyttsx3
import tkinter
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import messagebox
from dateutil import parser
import tkinter as tk
from tkinter import filedialog
import json
import random
import operator
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import re
import glob
import winshell
import pyjokes
import feedparser
import smtplib
import ctypes
import time
import requests
import shutil
import pyautogui
import pywhatkit
from twilio.rest import Client
from clint.textui import progress
from ecapture import ecapture as ec
from bs4 import BeautifulSoup
import win32com.client as wincl
from urllib.request import urlopen
from time import sleep
# from assignment import run_selenium_code_assignment
# from userc import create_user_with_domain
from flask import Flask
import webbrowser
from transformers import pipeline
from textblob import TextBlob
import smtplib
import getpass
import gtts
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import webbrowser
from pytube import YouTube
import pandas as pd



engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


# Function to speak
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Customized greetings based on the time of day
def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning Sir!")

    elif 12 <= hour < 18:
        speak("Good Afternoon Sir!")

    else:
        speak("Good Evening Sir!")

    assname = "Friday 1 point 0"
    speak("I am your Assistant")
    speak(assname)

# Greeting
def greet():
    speak("Hello Bharath Sir, welcome back")
    speak("How are you sir?")

# Analysing user emotions based on spoken input



def takeCommand():
	
	r = sr.Recognizer()
	
	with sr.Microphone() as source:
		
		print("Listening...")
        
		r.adjust_for_ambient_noise(source)
		audio = r.listen(source)

	try:
		print("Recognizing...")
		query = r.recognize_google(audio, language ='en-in')
		# query = r.recognize_google(audio, language ='hi-IN')

		print(f"User said: {query}\n")

	except Exception as e:
		print(e)
		print("Unable to Recognize your voice.")
		return "None"
	
	return query

#------------------reminder code------------------------------------#

# # Create a root window
# root = tk.Tk()
# root.withdraw()  # Hide the root window


# # Customize the input dialog
# root.geometry("400x200")  # Set the size of the dialog
# root.title("Add Reminder")  # Set the title of the dialog

# Define a list to store reminders
reminders = []

# Function to add a reminder using a GUI input form
# Function to add a reminder using a GUI input form
# Function to add a reminder using a GUI input form
def add_reminder_gui():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt the user for reminder content
    content = simpledialog.askstring("Input", "What's the reminder content?")

    if content is not None:
        # Prompt the user for the reminder date
        date_str = simpledialog.askstring("Input", "When should I remind you (e.g., 12th of August, 12 8, August 12th)?")
        
        # Prompt the user for the reminder time
        time_str = simpledialog.askstring("Input", "At what time should I remind you (e.g., 14:30)")

        if date_str is not None and time_str is not None:
            try:
                date_time = parser.parse(date_str + " " + time_str)
                reminders.append({"content": content, "datetime": date_time})
                print("Reminder added successfully.")
            except ValueError:
                print("Invalid date or time format. Please provide a recognizable format.")
        else:
            print("Reminder creation canceled.")
    else:
        print("Reminder creation canceled.")
# 
# Function to check and notify reminders
# Function to check and notify reminders
# Function to check and notify reminders
def check_reminders():
    current_time = datetime.datetime.now()
    for reminder in reminders:
        if reminder["datetime"] <= current_time:
            speak("Sir, you have a reminder now. Shall I show it or speak it?")
            response = takeCommand().lower()
            if "show" in response:
                show_reminder(reminder)
            elif "speak" in response:
                speak_reminder(reminder)

# Function to show the reminder
def show_reminder(reminder):
    content = reminder["content"]
    messagebox.showinfo("Reminder", content)
    speak("Sir, would you like to mark this reminder as 'finished' or 'postpone it'?")
    response = takeCommand().lower()
    if "finished" in response:
        reminders.remove(reminder)
        print("Reminder marked as finished")
    elif "postpone" in response:
        postpone_reminder(reminder)

# Function to speak the reminder
def speak_reminder(reminder):
    content = reminder["content"]
    speak(content)
    speak("Sir, would you like to mark this reminder as 'finished' or 'postpone it'?")
    response = takeCommand().lower()
    if "finished" in response:
        reminders.remove(reminder)
        print("Reminder marked as finished")
    elif "postpone" in response:
        postpone_reminder(reminder)

# Function to postpone the reminder
def postpone_reminder(reminder):
    new_date_str = simpledialog.askstring("Reminder", "Enter the new date (e.g., 12th of August, 12 8, August 12th)")
    new_time_str = simpledialog.askstring("Reminder", "Enter the new time (e.g., 14:30)")
    try:
        new_date_time = parser.parse(new_date_str + " " + new_time_str)
        reminder["datetime"] = new_date_time
        print("Reminder postponed successfully")
    except ValueError:
        print("Invalid date or time format. Please provide a recognizable format")

#

#------------------reminder code------------------------------------#



if __name__ == '__main__':
    clear = lambda: os.system('cls')
     
    # This Function will clean any
    # command before execution of this python file
    clear()
    wishMe()
    greet()
     
    while True:
        
        query = takeCommand().lower()
        print(f"User command: {query}")
        
         
        # All the commands said by user will be
        # stored here in 'query' and will be
        # converted to lower case for easily
        # recognition of command
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences = 3)
            speak("According to Wikipedia")
            print(results)
            speak(results)
            
        if 'create a reminder' in query:
            add_reminder_gui()
        elif 'show me the reminder' in query:
            for i, reminder in enumerate(reminders):
                print(f"Reminder {i+1}: {reminder['content']} at {reminder['datetime']}")
            # Add code to interact with reminders here.
        else:
            # Add other commands based on your script.
            check_reminders()
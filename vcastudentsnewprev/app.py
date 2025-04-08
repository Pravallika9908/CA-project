import cursor
from flask import Flask, render_template, send_from_directory,request,jsonify,redirect,url_for,flash,make_response,session
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, set_access_cookies,unset_jwt_cookies 
import os
import json
import random
import sys
import subprocess
from caques import Questions
import smtplib
from datetime import datetime
import mysql.connector
import pytz
from datetime import datetime, timedelta
from getconnection import Getconnection
from getquestions import GetQuestions
from datetime import timedelta
import uuid
import pandas as pd
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e6d7g8h9i10'


# Enter your database connection details below

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Replace with a strong secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)  # Token expiration time
jwt = JWTManager(app)

def authenticate(username, password):
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    connection = Getconnection.getconnection()
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    columns = [desc[0] for desc in cursor.description]
    account = cursor.fetchone()
    user = dict(zip(columns, account))
    print(user)
    if user:
        return user

user_sessions = {}



@app.route('/get_question/<string:questionList>/<int:question_index>')
def get_question(question_index,questionList):
    print(question_index,questionList)
    questions = GetQuestions.get_questions(questionList)
    # print(questions)
    if question_index < len(questions):
        return jsonify(questions[question_index])
    else:
        return jsonify({'question': '', 'answer': ''})

# Global variables to control the script execution
running_process = None

# Function to load user data from JSON file
def load_users(username, mobile_number, email):
    check_query = """
        SELECT * FROM users
        WHERE username = %s OR mobile_number = %s OR email = %s
    """
    print(f"Executing query: {check_query} with params: ({username}, {mobile_number}, {email})")
    
    connection = Getconnection.getconnection()
    cursor = connection.cursor()
    cursor.execute(check_query, (username, mobile_number, email))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        # Convert the tuple to a dictionary
        user_dict = {
            'user_id': existing_user[0],
            'username': existing_user[1],
            'password': existing_user[2],  # Stored password (plaintext)
            'email': existing_user[3],
            'mobile_number': existing_user[4],
        }
        print(f"User found: {user_dict}")
        return user_dict
    else:
        print("No user found.")
        return None



def validate_credentials(username, password):
    # Load user data based on the provided username
    user_data = load_users(username, None, None)

    if user_data:
        # Directly compare the stored password with the input password
        if user_data['password'] == password:
            return True  # Passwords match
    return False  # Invalid credentials


# Function to save user data to JSON file
def save_users(new_username, new_password, new_email, new_mobile, refer_code, is_subscribe, new_class):
    insert_query = """
    INSERT INTO users (username, password, email, mobile_number, refer_code, created_at, is_subscribe, class_name)
    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
    """
    user_data = (new_username, new_password, new_email, new_mobile, refer_code, is_subscribe, new_class)
    connection = Getconnection.getconnection()
    cursor = connection.cursor()
    print(user_data)
    cursor.execute(insert_query, user_data)
    # Commit the changes
    connection.commit()


@app.route('/')
def index():
    return render_template('index.html')

def generate_unique_session_id():
    return str(uuid.uuid4())

def save_token_in_db(user_id, token):
    try:
        insert_query = """
            INSERT INTO user_tokens (user_id, token)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE token = VALUES(token)
        """
        user_data = (user_id, token)

        connection = Getconnection.getconnection()  # Replace with your actual connection setup
        cursor = connection.cursor()
        cursor.execute(insert_query, user_data)
        connection.commit()
    except Exception as e:
        print(f"Error saving token to the database: {e}")
        # Handle the error as appropriate
    finally:
        cursor.close()
        connection.close()

def check_token(token):
    try:
        select_query = """
            SELECT user_id
            FROM user_tokens
            WHERE token = %s
        """

        connection = Getconnection.getconnection()  # Replace with your actual connection setup
        cursor = connection.cursor()
        cursor.execute(select_query, (token,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            # print(token,user_id,result,"error user_id")

            return user_id
            

        else:
            return None
    except Exception as e:
        print(f"Error checking token in database: {e}")
        return None
    finally:
        cursor.close()
        connection.close()






@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Check if there's an existing session and log out
            if 'session_id' in user_sessions:
                print(session)
                # Check if the session is stale (last login time more than 30 minutes ago, adjust as needed)
                last_login_time = session.get('last_login_time')
                print(last_login_time)

                if last_login_time and (datetime.now() - last_login_time) >= timedelta(minutes=30):
                    # Log out the previous session
                    session.pop('session_id', None)
                    session.pop('loggedin', None)
                    session.pop('id', None)
                    session.pop('username', None)
                    # Optionally, unset JWT cookies here

                    # Create a response and unset the JWT cookies
                    response = make_response(redirect(url_for('login')))

                    # Add headers to prevent caching
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    unset_jwt_cookies(response)
                    print("sucess")

                    return response

            # Check if the user exists
            user_data = load_users(username, None, None)

            if user_data and validate_credentials(username, password):
                # Set the last login time in the session
                session['last_login_time'] = datetime.now()

                # Log out the previous session (if any)
                if 'session_id' in user_sessions:
                    # Remove the session variables
                    session.pop('session_id', None)
                    session.pop('loggedin', None)
                    session.pop('id', None)
                    session.pop('username', None)
                    # Optionally, unset JWT cookies here

                    # Create a response and unset the JWT cookies
                    response = make_response(redirect(url_for('login')))

                    # Add headers to prevent caching
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    unset_jwt_cookies(response)

                    return response

                # Create session data, we can access this data in other routes
                session['session_id'] = generate_unique_session_id()
                session['loggedin'] = True
                session['id'] = user_data['user_id']
                session['username'] = user_data['username']
                save_token_in_db(user_data['user_id'], session['session_id'])

                # Create a JWT token and set it in the response headers
                # Convert user_id to string to avoid "Subject must be a string" error
                access_token = create_access_token(identity=str(user_data['user_id']))
                response = redirect(url_for('dashboard'))
                set_access_cookies(response, access_token)

                return {'status': '1', 'message': 'Login successful', 'username': username}
            else:
                print("Invalid credentials.")
                return {'status': '0', 'message': 'Invalid credentials'}

        return render_template('index.html')
    except Exception as e:
        print(e)
        return {'status': '0', 'message': 'An error occurred during login'}


@app.route('/interactive', methods=[ 'POST'])
def interactive():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']
        print(token)
        if check_token(token):
            try:
                # print('in here')
                connection = Getconnection.getconnection()
                cursor = connection.cursor()
                query = "select question,correct_answer,attempt_no from user_answer where user_id ="+str(user_id)+" and attempt_no >= 2"
                # print(query)
                cursor.execute(query)
                columns = cursor.description 
                result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                local_file_name = pd.DataFrame(result)
                local_file_name = local_file_name.sample(n=1)
                print(local_file_name)
                local_file_name = local_file_name.to_dict(orient='records')
                connection.close()
                
                # Pass the test results data to the template
                return jsonify(results=local_file_name)
            except Exception as e:
                print(e)
                return jsonify({'status': 'error', 'message': 'Invalid token'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

@app.route('/save_interactive', methods=['POST'])
def save_interactive():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            try:
                data = request.get_json()
                questions = data.get('questions')
                correct_answers = data.get('correctAnswers')
                user_answers = data.get('userAnswers')
                similarity_scores = data.get('similarityScores')

                # Assuming the arrays are of the same length
                for i in range(len(questions)):
                    question = questions[i]
                    correct_answer = correct_answers[i]
                    user_answer = user_answers[i]
                    similarity = similarity_scores[i]
                    correct_answer = correct_answers[i]
                    
                    print(question,correct_answer,user_answer,similarity,correct_answer)

                    savedb_interactive(user_id, question, correct_answer, user_answer, similarity)
                
                return jsonify({'status': 'success'})
            except Exception as e:
                print(f"Error processing data: {e}")
                return jsonify({'status': 'error', 'message': 'Error processing data'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})


def savedb_interactive(user_id, question, correct_answer, user_answer,similarity):
    try:
        insert_query = """
            INSERT INTO user_answer_interactive (user_id, question, correct_answer, user_answer,similarity)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (user_id, question, correct_answer, user_answer,similarity)
        print(data,"datasave data")

        connection = Getconnection.getconnection()  # Replace with your actual connection setup
        cursor = connection.cursor()
        cursor.execute(insert_query, data)
        connection.commit()
    except Exception as e:
        print(f"Error saving data to the database: {e}")
        # Handle the error as appropriate
    finally:
        # Close the database connection if needed
        cursor.close()
        connection.close()


from datetime import datetime
from flask import session


@app.route('/testresults', methods=['GET', 'POST'])
def get_testresults():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            try:
                connection = Getconnection.getconnection()
                cursor = connection.cursor()
                
                # Modify the query to filter results for the logged-in user
                query = """
                    SELECT * FROM user_answer ua 
                    LEFT JOIN Subject su ON ua.subjectname = su.id 
                    WHERE ua.user_id = %s
                """
                cursor.execute(query, [user_id])
                results = cursor.fetchall()
                connection.close()

                # Fetch user_info from your database or wherever it is stored
                # Modify the following line based on how you retrieve user_info
                user_info = fetch_user_info(user_id)
                # print("User Info:", user_info)

                # Pass the test results data and user_info to the template
                return render_template('results.html', results=results, user_info=user_info)
            except Exception as e:
                print("Database error:", e)
                return jsonify({'status': 'error', 'message': f'Error retrieving test results from the database: {str(e)}'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'})



@app.route('/get_interactiveresults', methods=['GET','POST'])
def get_interactiveresults():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            try:
                connection = Getconnection.getconnection()
                cursor = connection.cursor()
                cursor.execute("select * from user_answer_interactive where 1 and user_id = %s", [user_id])
                results = cursor.fetchall()
                print(results)
                connection.close()
                # Pass the test results data to the template
                return render_template('interactiveresults.html', results=results)
            except Exception as e:
                print(e)
                return jsonify({'status': 'error', 'message': 'Invalid token'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'})
    


@app.route('/save_results', methods=['POST'])
def save_results():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            try:
                data = request.get_json()
                questions = data.get('questions')
                correct_answers = data.get('correctAnswers')
                user_answers = data.get('userAnswers')
                similarity_scores = data.get('similarityScores')
                attemptednumber = data.get('attemptednumber')
                numbertest = data.get('numbertest')
                subjectname = data.get('subjectname')
                chaptername = data.get('chaptername')

                numbertest = numbertest[0]
                subjectname = subjectname[0]
                chaptername = chaptername[0]

                for i in range(len(questions)):
                    question = questions[i]
                    correct_answer = correct_answers[i]
                    user_answer = user_answers[i]
                    similarity = similarity_scores[i]
                    attempt_no = attemptednumber[i]

                    print(question, correct_answer, user_answer, similarity, attempt_no, numbertest, subjectname, chaptername)

                    save_to_database(user_id, question, correct_answer, user_answer, similarity, attempt_no, numbertest, subjectname, chaptername)

                return jsonify({'status': 'success'})
            except Exception as e:
                print(f"Error processing data: {e}")
                return jsonify({'status': 'error', 'message': 'Error processing data'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})

# Add the get_subject_name function
def get_subject_name(subject_id):
    try:
        connection = Getconnection.getconnection()  # Replace with your actual connection setup
        cursor = connection.cursor()
        cursor.execute("SELECT subject_name FROM Subject WHERE id = %s", (subject_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()

# Now define the save_to_database function
def save_to_database(user_id, question, correct_answer, user_answer, similarity, attempt_no, numbertest, subject_id, chaptername):
    try:
        connection = Getconnection.getconnection()  # Replace with your actual connection setup
        cursor = connection.cursor()

        # Fetch subject name based on subject ID
        subject_name = get_subject_name(subject_id)
        if subject_name is None:
            print(f"Subject with ID '{subject_id}' not found.")
            return

        # Insert into user_answer with a subquery to get the chapter ID
        insert_query = """
            INSERT INTO user_answer (user_id, question, correct_answer, user_answer, similarity, attempt_no, test_no, subjectname, chaptername, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (user_id, question, correct_answer, user_answer, similarity, int(attempt_no), int(numbertest), subject_name, chaptername, current_date)

        cursor.execute(insert_query, data)
        connection.commit()
    except Exception as e:
        print(f"Error saving data to the database: {e}")
    finally:
        cursor.close()
        connection.close()




@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')
        new_email = data.get('email')
        new_mobile = data.get('mobile')
        is_subscribe = data.get('is_subscribe', 0)
        new_class = data.get('class_name')
        print(new_class,"werror")

        existing_user = load_users(new_username, new_mobile, new_email)

        refer_code = (new_username[:4] + new_mobile[-4:]).upper()

        if existing_user:
            # User already exists with the given username, mobile number, or email
            error_message = 'User already exists with the following data:\n'
            if existing_user.get('username') == new_username:
                error_message += f'Username: {new_username}\n'
            if existing_user.get('email') == new_email:
                error_message += f'Email: {new_email}\n'
            if existing_user.get('mobile_number') == new_mobile:
                error_message += f'Mobile Number: {new_mobile}\n'

            print(error_message)
            return {'status': '0', 'message': error_message}
        else:
            # Save the new user
            save_users(new_username, new_password, new_email, new_mobile, refer_code, is_subscribe, new_class)
            return {'status': '1', 'message': 'Successfully Registered'}


# The rest of your code...
def generateOTPUpdate(otp_size=6):
    final_otp = ''
    for i in range(otp_size):
        final_otp = final_otp + str(random.randint(0, 9))
    return final_otp

        

def sendEmailVerificationRequestUpdate(receiver="bharath.office365@gmail.com", custom_text="Hello, Your OTP is "):
    sender = "bassartindia15@gmail.com"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    google_app_password = "nfkizhuioryklcmb"
    server.login(sender, google_app_password)
    cur_otp = generateOTPUpdate()
    msg = custom_text + cur_otp
    server.sendmail(sender, receiver, msg)
    
    print(cur_otp,"sendEmailVerificationRequestUpdate")

    return cur_otp


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        connection = Getconnection.getconnection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email LIKE %s", [email])
        user = cursor.fetchone()

        if user:
            # User exists, generate OTP and send it via email
            reset_otp = sendEmailVerificationRequestUpdate(receiver=email)
            session['reset_otp'] = reset_otp
            session['reset_email'] = email

            # Send OTP via email (remove this line since it's redundant)
            # subject = 'Password Reset OTP'
            # body = f'Your OTP for password reset is: {reset_otp}'
            # sendEmailVerificationRequest(receiver=email, custom_text=body)

            flash("An email has been sent with instructions to reset your password.", "success")

            return redirect(url_for('reset_password'))
        else:
            flash("Email not found. Please enter a valid email address.", "danger")

    return render_template('forgot_password.html', title='Forgot Password')


# Your existing code for the reset password route
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if entered_otp == session.get('reset_otp') and new_password == confirm_password:
            # Update password in the database
            email = session.get('reset_email')

            connection = Getconnection.getconnection()
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", [new_password, email])
            connection.commit()


            flash("Password reset successfully. You can now log in with your new password.", "success")
            session.pop('reset_otp', None)
            session.pop('reset_email', None)

            return redirect(url_for('login'))
        else:
            flash("Invalid OTP or passwords do not match. Please try again.", "danger")

    return render_template('reset_password.html', title='Reset Password')

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/startquestions', methods=['GET', 'POST'])
def start_script():
    if request.method == 'POST':
        data = request.get_json()
        questionList = data.get('questionList')
        print(f"Received questionList: {questionList}")
        questionobject = Questions.start_questions(questionList)
        print("Started questions.")
        return questionobject
    return True

@app.route('/stopquestions', methods=['GET', 'POST'])
def stop_script():
    if request.method == 'GET':
        questionobject = Questions.stop_questions()
        print("Stopped questions.")
        return questionobject
    return True

    # global running_process
    # if running_process is None or running_process.poll() is not None:
    #     running_process = subprocess.Popen(['python', 'caques.py'])
    #     return jsonify({'status': 'started'})
    # return jsonify({'status': 'already running'})
    


@app.route('/header', methods=['GET', 'POST'])
def header():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            return render_template('header.html', username=session['username'], title="Header")
    return render_template('index.html')

def fetch_user_info(user_id):
    connection = Getconnection.getconnection()
    cursor = connection.cursor()

    query = "SELECT username, is_subscribe, class_name, refer_code FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    # Fetch the result
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result


def fetch_subjects(user_id):
    connection = Getconnection.getconnection()
    cursor = connection.cursor()

    # Fetch user information
    user_info_query = "SELECT is_subscribe, class_name FROM users WHERE user_id = %s"
    cursor.execute(user_info_query, (user_id,))
    user_info = cursor.fetchone()
    print("subject",user_info)

    # Fetch subjects based on user's class and subscription status
    if user_info:
        if user_info[1] == 'CA_intermediate' and user_info[0] == 1:
            query = "SELECT id, subject_name FROM Subject WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8)"
        elif user_info[1] == 'CA_intermediate' and user_info[0] == 0:
            query = "SELECT id, subject_name FROM Subject WHERE id = 1"
        elif user_info[1] == 'CA_final' and user_info[0] == 1:
            query = "SELECT id, subject_name FROM Subject WHERE id IN (9, 10, 11, 12, 13)"
        elif user_info[1] == 'CA_final' and user_info[0] == 0:
            query = "SELECT id, subject_name FROM Subject WHERE id = 9"
        # else:
            # query = "SELECT id, subject_name FROM Subject"

        cursor.execute(query)
        subjects = cursor.fetchall()
    else:
        subjects = []

    cursor.close()
    connection.close()

    return subjects


from flask import jsonify

@app.route('/fetch_chapters', methods=['GET'])
def fetch_chapters():
    # print("yeah I arrived here")
    subject_id = request.args.get('subject_id')

    connection = Getconnection.getconnection()
    cursor = connection.cursor()

    query = "SELECT id, chapter_name FROM Chapter WHERE subject_id = %s"
    # print(subject_id)
    cursor.execute(query, (subject_id,))
    chapters = cursor.fetchall()
    # print(chapters,'chapters')
    cursor.close()
    connection.close()

    return jsonify(chapters=chapters)


@app.route('/fetchquestions', methods=['POST','GET'])
def fetchquestions():
    # print("yeah I arrived here")
    selectedChapterName = request.args.get('selectedChapterName')
    subjectid = request.args.get('subjectid')

    
    # print(selectedChapterName)
    connection = Getconnection.getconnection()
    cursor = connection.cursor()

    query = "SELECT  questions FROM Chapter WHERE subject_id = %s and chapter_name= %s"
    cursor.execute(query, (subjectid,selectedChapterName,))
    chapters = cursor.fetchall()
    print(chapters,'chapters')
    cursor.close()
    connection.close()

    return jsonify(chapters=chapters)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            # Fetch user information
            user_info = fetch_user_info(user_id)
            subjects = fetch_subjects(user_id)
            # print(user_info,"user_info")
            # print(subjects,"subjects")

            if user_info:
                # print(user_info,"errore1")

                # Pass user_info to the template
                return render_template('dashboard.html', username=session['username'], title="Home", user_info=user_info,subjects=subjects)
               
            else:
                # print(user_info,"errore2")
                # Handle the case when user information is not found
                return render_template('dashboard.html', username=session['username'], title="Home", user_info=None)
        # Handle the case when the token is not valid
        else:
            return render_template('/index.html', title="Index")
    
    # Handle the case when 'id' or 'session_id' is not in session
    return render_template('/index.html', title="Home", user_info=None)






# ...

@app.route('/logout')
def logout():
    try:
        # print(session, "user_sessions in logout")
        # Check if user is logged in
        if 'id' in session and 'session_id' in session:
            user_id = session['id']
            token = session['session_id']

            if check_token(token):
                # Get the last login timestamp from the session
                last_login_time = session.get('last_login_time')

                # Check if the last login time is available and within a certain threshold
                if last_login_time:
                    # Set the logout session variable
                    session['logout'] = True

                    # Remove the session variables
                    session.pop('session_id', None)
                    session.pop('loggedin', None)
                    session.pop('id', None)
                    session.pop('username', None)

                    # Create a response and unset the JWT cookies
                    response = make_response(redirect(url_for('login')))

                    # Add headers to prevent caching
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    unset_jwt_cookies(response)

                    return response

        return render_template('/index.html', title="Index")
    except Exception as e:
        print(e)
        return redirect(url_for(''))

# ...



    


@app.route('/subscription', methods=['GET', 'POST'])
def subscription():
    # Check if user is logged in
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            # Check if the request method is POST and contains 'utr' and 'refer_code'
            if request.method == 'POST' and all(key in request.form for key in ['utr', 'refer_code']):
                utr = request.form['utr']
                refer_code = request.form['refer_code']
                # print(utr,'utr')
                # print(refer_code,'refer_code')

                # Update the 'users' table for the logged-in user with the provided 'utr' and 'refer_code'
                # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                connection = Getconnection.getconnection()
                cursor = connection.cursor()
                cursor.execute('UPDATE users SET utr = %s, refer_code = %s WHERE user_id = %s', (utr, refer_code, session['id']))
                # mysql.connection.commit()
                connection.commit()
                flash("Subscription information updated successfully!", "success")
                return render_template('subscription.html', username=session['username'])
            else:
                flash("Incomplete form!", "danger")

            # Render the subscription template
            return render_template('subscription.html', username=session['username'])
        else:
            # User is not logged in, redirect to the login page
            return redirect(url_for('login'))






@app.route('/getremainingtime', methods=['GET', 'POST'])
def get_getremainingtime():
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        if check_token(token):
            try:
                connection = Getconnection.getconnection()
                cursor = connection.cursor()
                cursor.execute("SELECT created_at FROM caproject.users where user_id  = %s", [user_id])
                results = cursor.fetchall()
                created_at = results[0][0]

                # Calculate the remaining days
                expiration_date = created_at + timedelta(days=90)
                remaining_days = (expiration_date - datetime.now()).days

                connection.close()

                # Pass the remaining days to the frontend
                return jsonify({'daysLeft': remaining_days})

            except Exception as e:
                return jsonify({'status': 'error', 'message': 'Invalid token'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'})
    

@app.route('/interactiveone')
def interactive_one():
    # Check if the user is logged in
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        # Assuming check_token is a function that validates the token
        if check_token(token):
            # Fetch user information using fetch_user_info function
            user_info = fetch_user_info(user_id)

            # Pass user information to the template
            return render_template('interactiveone.html', user_info=user_info)
        else:
            # User is not logged in or token is invalid, redirect to login
            return redirect(url_for('login'))
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('login'))

#--------------------template mowa-----------------#

# @app.route('/button_clicked', methods=['GET', 'POST'])
# def button_clicked():
#     if request.method == 'POST':
#         # Code to handle button click event for POST requests
#         # For example, you can perform some server-side processing here

#         # Respond with a message or redirect to another page
#         return render_template('intertwo.html')
#     else:
#         # Handle GET requests if needed
#         return render_template('intertwo.html')
#--------------------template mowa-----------------#

@app.route('/button_clicked')
def button_clicked():
    # Check if the user is logged in
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        # Assuming check_token is a function that validates the token
        if check_token(token):
            # Fetch user information using fetch_user_info function
            user_info = fetch_user_info(user_id)

            # Pass user information to the template
            return render_template('intertwo.html', user_info=user_info)
        else:
            # User is not logged in or token is invalid, redirect to login
            return redirect(url_for('login'))
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('login'))
    
#subbutton code

@app.route('/subbuttonoo')
def subbuttonoo():
    # Check if the user is logged in
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        # Assuming check_token is a function that validates the token
        if check_token(token):
            # Fetch user information using fetch_user_info function
            user_info = fetch_user_info(user_id)

            # Pass user information to the template
            return render_template('suboneoo.html', user_info=user_info)
        else:
            # User is not logged in or token is invalid, redirect to login
            return redirect(url_for('login'))
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('login'))
    
@app.route('/subarasacibe')
def subarasacibe():
    # Check if the user is logged in
    if 'id' in session and 'session_id' in session:
        user_id = session['id']
        token = session['session_id']

        # Assuming check_token is a function that validates the token
        if check_token(token):
            # Fetch user information using fetch_user_info function
            user_info = fetch_user_info(user_id)

            # Pass user information to the template
            return render_template('subscription.html', user_info=user_info)
        else:
            # User is not logged in or token is invalid, redirect to login
            return redirect(url_for('login'))
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('login'))

if __name__ == '__main__':
    port=9090
    # app.run(port=port)
    app.run(host='0.0.0.0', port=port, debug=True)
import sys
import os
import numpy as np
import cv2
from datetime import date
import pickle
from sklearn.linear_model import LogisticRegression

from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL, MySQLdb
import bcrypt


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pneumonia_detection'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'Aniket123'
mysql = MySQL(app)


MODEL_PATH = 'static/AI-model/model_updated.pkl'
model = pickle.load(open('static/AI-model/model_updated.pkl','rb'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def aboutus():
    return render_template('about-us.html')

@app.route('/login', methods=['GET','POST'])
def loginuser():
    error = ' '
    if request.method == 'POST':
        user_email_log = request.form['user-email-log']
        user_pass_log = request.form['user-password-log'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM register WHERE Email_Id = %s ',(user_email_log,))
        user = cur.fetchone()
        cur.close()
        try:

            if len(user) != 0:
                if bcrypt.hashpw(user_pass_log,user['Password'].encode('utf-8')) == user['Password'].encode('utf-8'):
                    session['Email_Id'] = user_email_log
                    session['First_Name'] = user['First_Name']

                    return redirect(url_for('aiwebapp'))
                else:
                    error = 'Password is not correct! Please use valid password'
                    return render_template('log-in.html', error=error)

            else:
                error = 'Credentials are not valid! Please use valid credentials'
                return render_template('log-in.html', error = error)

        except Exception as e:
            error = 'Credentials are not valid. Please use valid credentials !'
            return render_template('log-in.html', error=error)


    else:
        return render_template('log-in.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET','POST'])
def registeruser():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        user_email = request.form['user-email']
        user_pass = request.form['user-pass'].encode('utf-8')
        hash_pass = bcrypt.hashpw(user_pass,bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO register (First_Name,Last_Name,Email_Id,Password) VALUES(%s,%s,%s,%s)', (first_name,last_name,user_email,hash_pass))
        mysql.connection.commit()
        session['Email_Id'] = user_email
        session['First_Name'] = first_name
        return redirect(url_for('aiwebapp'))




@app.route('/ai-webapp',methods=['GET','POST'])
def aiwebapp():

    CATEGORIES = ['Patient is normal', 'Pneumonia is present']
    MODEL_PATH = 'static/AI-model/model_updated.pkl'

    if request.method == 'POST':

        int_features=[]

        oxygen = request.form['patient_oxygen']
        int_features.append(oxygen)

        heart_rate = request.form['patient_heart_rate']
        int_features.append(heart_rate)

        blood_pressure = request.form['patient_blood_pressure']
        int_features.append(blood_pressure)

        fever = request.form['patient_fever']
        int_features.append(fever)



        final = [np.array(int_features)]

        result = model.predict(final)
        prediction_value = (CATEGORIES[int(result)])


        return render_template('ai-webapp.html',result=prediction_value)

    return render_template('ai-webapp.html')

if __name__ == "__main__":
    app.run(debug=True)
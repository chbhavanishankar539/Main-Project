from flask import Flask,render_template,flash,request,send_from_directory
import pandas as pd
import mysql.connector
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tensorflow as tf
from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D
mydb = mysql.connector.connect(host="localhost", user="root", passwd="",port=3307, database="signature")
cursor = mydb.cursor()
app=Flask(__name__)
app.config['SECRET_KEY']="abcd"
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/contact',methods=['POST','GET'])
def contact():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        pwd=request.form['pwd']
        pno=request.form['pno']
        addr=request.form['addr']
        print(email,name,pwd,addr,pno)
        sql="select * from users where email='"+email+"'"
        data=pd.read_sql_query(sql,mydb)
        emails=data['email'].values
        print(emails)
        if email in emails:
            flash("Email already exists","warning")
            return render_template('contact.html')
        else:
            sql1="insert into users(name,email,pwd,pno,address) values(%s,%s,%s,%s,%s)"
            val=(name,email,pwd,pno,addr)
            print("vall",val)
            cursor.execute(sql1,val)
            mydb.commit()
            flash("Data added successfully","success") 
            return render_template('contact.html')           

    return render_template('contact.html')


@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        # opt = request.form['opt']
        password = request.form['pwd']
        sql = "select * from users where email='"+username+"' and pwd='"+password+"' " 
        cursor.execute(sql)
        results = cursor.fetchall()
        mydb.commit()
        print(type(results))
        if not results:
            flash("Invalid Email / Password", "danger")
            return render_template('contact.html')

        else:
    
            if len(results) > 0:
                flash("Welcome ", "primary")
                return render_template('userhome.html', msg=results[0][1])
    return render_template('contact.html')
@app.route('/forget',methods=['POST', 'GET'])
def forget():
    if request.method == "POST":
        email = request.form['email']
        sql = "select count(*),name,pwd from users where email='%s'" % (email)
        x=pd.read_sql_query(sql, mydb)
        count=x.values[0][0]
        pwd=x.values[0][2]
        name=x.values[0][1]
        if count==0:
            flash("Email not valid try again","info")
            return render_template('forgot.html')
        else:
            # msg = 'This your password : '
            # t = 'Regards,'
            # t1 = 'E-Agri Kit Services.'
            # mail_content = 'Dear ' + name +','+'\n'+msg  +pwd+ '\n' + '\n' + t + '\n' + t1
            # sender_address = 'ashokreshma2000@gmail.com'
            # sender_pass = 'Waltstreet@1'
            # receiver_address = email
            # message = MIMEMultipart()
            # message['From'] = sender_address
            # message['To'] = receiver_address
            # message['Subject'] = 'E-Agri Kit- Agriculture Aid'
            # message.attach(MIMEText(mail_content, 'plain'))
            # ses = smtplib.SMTP('smtp.gmail.com', 587)
            # ses.starttls()
            # ses.login(sender_address, sender_pass)
            # text = message.as_string()
            # ses.sendmail(sender_address, receiver_address, text)
            # ses.quit()
            flash("Password sent to your mail ", "success")
            return render_template("contact.html")

    return render_template('forgot.html')
@app.route('/changepass',methods=['POST','GET'])
def changepass():
    if request.method=='POST':
        email = request.form['email']
        pwd = request.form['pwd']
        new_pwd = request.form['new_pwd']
        confirm_pwd = request.form['confirm_pwd']
        sql="select * from users where email='"+email+"' and pwd='"+pwd+"'"
        x=pd.read_sql_query(sql,mydb)
        emails=x['email'].values
        if len(emails)>0:
            sq="update users set pwd='"+confirm_pwd+"'"
            cursor.execute(sq,mydb)
            mydb.commit()
            flash("Password Changed successfully","success")
            return render_template('contact.html')
        else:
            flash('Email or password incorrect data, check once',"danger")
            return render_template('changepass.html')
    return render_template('changepass.html')

# @app.route("/upload", methods=["POST","GET"])
# def upload():
#     print('a')
#     if request.method=='POST':
#         myfile=request.files['file']
#         fn=myfile.filename
#         mypath=os.path.join('images/', fn)
#         myfile.save(mypath)
#         print("{} is the file name",fn)
#         print ("Accept incoming file:", fn)
#         print ("Save it to:", mypath)
#         classes = ['Forgery','Real']
#         new_model = load_model("models/mobilenet.h5")
#         test_image = image.load_img(mypath, target_size=(224, 224))
#         test_image = image.img_to_array(test_image)
#         test_image = test_image / 255
#         test_image = np.expand_dims(test_image, axis=0)
#         result = new_model.predict(test_image)
#         preds = classes[np.argmax(result)]
#         accuracy = float(np.max(result,axis=1)[0])
#         print(accuracy)
#         formatted_val = f"{accuracy * 100:.2f}"
#         print(formatted_val)
#         return render_template("upload.html",image_name=fn, text=preds,acc=formatted_val)
#     return render_template('userhome.html')



# Load the saved classification model

model = tf.keras.models.load_model('models/mobilenet_v2_classifier_model.h5')

# Reload the MobileNet feature extractor
base_model = MobileNet(weights='imagenet', include_top=False)
feature_extractor = Model(inputs=base_model.input, outputs=GlobalAveragePooling2D()(base_model.output))

class_names = ['FORGERY', 'REAL']


def make_prediction(model, image_path):
    """
    Preprocess the image and make a prediction using the trained model.
    """
    # Load the image and preprocess it
    img = load_img(image_path, target_size=(224, 224))  # Resize to MobileNet input size
    img_array = img_to_array(img)  # Convert to a NumPy array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = preprocess_input(img_array)  # Preprocess for MobileNet

    # Extract features using the MobileNet feature extractor
    features = feature_extractor.predict(img_array)

    # Predict the class using the trained classification model
    predictions = model.predict(features)
    predicted_class_idx = np.argmax(predictions)  # Get index of the highest probability
    predicted_class = class_names[predicted_class_idx]  # Map index to class name

    return predicted_class

@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        myfile = request.files['file']  # Get the uploaded file
        fn = myfile.filename  # Extract filename
        mypath = os.path.join('static', 'img', fn)  # Save path
        myfile.save(mypath)  # Save the file to the server

        # Make prediction
        predicted_class = make_prediction(model, mypath)

        # Return result to the template
        return render_template('upload.html', path=mypath, prediction=predicted_class)

    return render_template('upload.html')

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


if __name__=='__main__':
    app.run(debug=True)
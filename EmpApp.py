from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name,
                       last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route('/aboutUs')
def aboutUs():
    emp_id = tuple()
    first_name = tuple()
    last_name = tuple()
    pri_skill = tuple()
    location = tuple()
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee')
    db = cursor.fetchall()
    for employee in db:
        emp_id = emp_id + (employee[0],)
        first_name = first_name + (employee[1],)
        last_name = last_name+(employee[2],)
        pri_skill = pri_skill+(employee[3],)
        location = location+(employee[4],)
    emp_image_file = 'https://pbs.twimg.com/profile_images/1389140738827501568/RUeCH5Dg_400x400.jpg'
    return render_template(
        # 'AboutUs.html', fname=first_name, lname=last_name,
        'TryAboutUs.html', fname=first_name, lname=last_name,
        emp_image_file=emp_image_file,
        pri_skill=pri_skill, location=location
    )


'''
@app.route('/aboutUs')
def aboutUs():
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee WHERE emp_id=%s', ('1'))
    db = cursor.fetchone()
    emp_id = db[0]
    first_name = db[1]
    last_name = db[2]
    pri_skill = db[3]
    location = db[4]
    emp_image_file = 'https://pbs.twimg.com/profile_images/1389140738827501568/RUeCH5Dg_400x400.jpg'
    return render_template(
        # 'AboutUs.html', fname=first_name, lname=last_name,
        'TryAboutUs.html', fname=first_name, lname=last_name,
        emp_image_file=emp_image_file,
        pri_skill=pri_skill, location=location
    )
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

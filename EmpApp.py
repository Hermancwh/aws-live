from flask import Flask, render_template, request, redirect
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
def Dashboard():
    return render_template('DashBoard.html')

@app.route("/employee", methods=['GET', 'POST'])
def Employee():
    query_string = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    employees = cursor.fetchall()
    cursor.close()

    count = "SELECT COUNT(*) FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(count)
    here = cursor.fetchall()
    print(here[0][0])

    return render_template('Employee.html', employees=employees)

@app.route("/attendance", methods=['GET', 'POST'])
def Attendance():
    return render_template('Attendance.html')

@app.route("/payroll", methods=['GET', 'POST'])
def Payroll():
    return render_template('Payroll.html')

@app.route("/leave", methods=['GET', 'POST'])
def Leave():
    return render_template('Leave.html')

@app.route("/adding", methods=['GET', 'POST'])
def adding():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    # emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    counts = "SELECT COUNT(*) FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(counts)
    emp_id = cursor.fetchall()
    emp_id = int(emp_id[0][0]) + 1

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (str(emp_id), first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-first-name-" + first_name + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
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

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        query_string = "SELECT * FROM employee WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(query_string, emp_id)
        employee = cursor.fetchall()

    else:
        employee = ""

    return render_template('GetEmp.html', employee=employee)

@app.route('/employee/<string:id>/delete', methods=['GET', 'POST'])
def delete(id):
    query_string = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    employee = cursor.fetchall()

    if request.method == 'POST':
        delete_sql = "DELETE FROM employee WHERE emp_id=%s"
        cursor = db_conn.cursor()
        cursor.execute(delete_sql, id)
        db_conn.commit()
        print("ID " + id + " successfully been deleted.")

    return render_template('EditEmp.html', deleteEmp=employee)

@app.route('/employee/<string:id>/edit', methods=['GET', 'POST'])
def edit(id):
    query_string = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    employee = cursor.fetchall()

    if request.method == 'POST':

        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']

        try:
            update_sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s WHERE emp_id=%s"
            cursor = db_conn.cursor()

            cursor.execute(update_sql, (first_name, last_name, pri_skill, location, emp_id))
            db_conn.commit()

            # # Uplaod image file in S3 #
            # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            # s3 = boto3.resource('s3')
            #
            # try:
            #     print("Data inserted in MySQL RDS... uploading image to S3...")
            #     s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            #     bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            #     s3_location = (bucket_location['LocationConstraint'])
            #
            #     if s3_location is None:
            #         s3_location = ''
            #     else:
            #         s3_location = '-' + s3_location
            #
            #     object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            #         s3_location,
            #         custombucket,
            #         emp_image_file_name_in_s3)
            #
            # except Exception as e:
            #     return str(e)
        finally:
            cursor.close()

        return redirect('/employee/' + emp_id + '/edit')

    return render_template('EditEmp.html', editEmp=employee)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

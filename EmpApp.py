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
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_attendance = "SELECT * FROM attendance"
    cursor = db_conn.cursor()
    cursor.execute(query_attendance)
    attendance = cursor.fetchall()

    query_employee = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_employee)
    employees = cursor.fetchall()

    query_payroll = "SELECT * FROM payroll"
    cursor = db_conn.cursor()
    cursor.execute(query_payroll)
    payroll = cursor.fetchall()

    # calculate total amount payroll and pay rate
    total_payroll = 0
    total_payrate = 0
    for x in range(len(payroll)):
        total_payroll += float(payroll[x][3])
        total_payrate += float(payroll[x][2])

    query_leaves = "SELECT * FROM leaves"
    cursor = db_conn.cursor()
    cursor.execute(query_leaves)
    leaves = cursor.fetchall()

    return render_template('DashBoard.html', attendance=attendance, employees=employees, payroll=payroll, leaves=leaves, total_payroll=total_payroll, total_payrate=total_payrate, total_employee=len(employees), total_leave=len(leaves))

@app.route("/attendance", methods=['GET', 'POST'])
def Attendance():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM attendance"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    attendance = cursor.fetchall()

    query_string = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    employees = cursor.fetchall()

    return render_template('Attendance.html', attendance=attendance, employees=employees)

@app.route("/attendance/<string:id>/edit", methods=['GET', 'POST'])
def GetAttendance(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM attendance WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    attendance = cursor.fetchone()

    if request.method == 'POST':

        total_hours = request.form['total_hours']
        start_work = request.form['start_work']
        end_work = request.form['end_work']
        over_time = request.form['over_time']

        try:
            update_sql = "UPDATE attendance SET total_hours=%s, start_work=%s, end_work=%s, over_time=%s WHERE attendance_id=%s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (total_hours, start_work, end_work, over_time, id))
            db_conn.commit()

        finally:
            cursor.close()

        print("Successfully edited Attendance ID " + id)
        return redirect('/attendance')

    return render_template('EditAttendance.html', attendance=attendance)

@app.route("/payroll", methods=['GET', 'POST'])
def Payroll():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM payroll"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    payroll = cursor.fetchall()
    cursor.close()

    query_string = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    employees = cursor.fetchall()

    return render_template('Payroll.html', payroll=payroll, employees=employees)

@app.route("/payroll/<string:id>/edit", methods=['GET', 'POST'])
def GetPayroll(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    payroll_string = "SELECT * FROM payroll WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(payroll_string, id)
    payroll = cursor.fetchone()

    attendance_string = "SELECT * FROM attendance WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(attendance_string, id)
    attendance = cursor.fetchone()

    working_hours = int(attendance[2]) + int(attendance[5])
    payroll_amount = working_hours * payroll[2]

    if request.method == 'POST':

        pay_rate = request.form['pay_rate']
        payroll_amount = request.form['payroll_amount']

        try:
            update_sql = "UPDATE payroll SET pay_rate=%s, payroll_amount=%s WHERE payroll_id=%s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (pay_rate, payroll_amount, id))
            db_conn.commit()

        finally:
            cursor.close()

        print("Successfully edited Payroll ID "+id)
        return redirect('/payroll/'+id+'/edit')

    return render_template('EditPayroll.html', payroll=payroll, working_hours=working_hours, payroll_amount=payroll_amount)

@app.route("/leave", methods=['GET', 'POST'])
def Leave():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    emp_leaves = ""
    query_string = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    employees = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        search_emp = request.form['search_emp']

        try:
            get_query = "SELECT * FROM leaves WHERE emp_id=%s ORDER BY leave_id"
            cursor = db_conn.cursor()
            cursor.execute(get_query, search_emp)
            emp_leaves = cursor.fetchall()
        except Exception as e:
            print(str(e))

        if emp_leaves is None:
            emp_leaves = ""

    return render_template('Leave.html', employees=employees, emp_leaves=emp_leaves)

@app.route("/leave/<string:id>", methods=['GET', 'POST'])
def settingLeave(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    employee = cursor.fetchone()

    return render_template('applyLeave.html', employee=employee)

@app.route("/leave/<string:id>/apply", methods=['POST'])
def applyLeave(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']
        status = request.form['status']

        #auto-generate id
        try:
            get_query = "SELECT * FROM leaves ORDER BY leave_id DESC LIMIT 1"
            cursor = db_conn.cursor()
            cursor.execute(get_query)
            latest_id = cursor.fetchone()
        except Exception as e:
            print(str(e))

        if latest_id is not None:
            latest_id = int(latest_id[0]) + 1
        else:
            latest_id = 1

        insert_sql = "INSERT INTO leaves VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (str(latest_id), id, start_date, end_date, reason, status))
            db_conn.commit()

        finally:
            cursor.close()

        print("Leave ID " + str(latest_id) + " has apply successfully.")

    return redirect('/leave')

@app.route("/adding", methods=['GET', 'POST'])
def adding():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    return render_template('www.intellipaat.com')

@app.route("/aboutUs", methods=['GET', 'POST'])
def aboutUs():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    return render_template('AboutUs.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    location = request.form['location']
    phone = request.form['phone']
    position = request.form['position']
    emp_image_file = request.files['emp_image_file']

    #auto-generate id
    try:
        get_query = "SELECT * FROM employee ORDER BY emp_id DESC LIMIT 1"
        cursor = db_conn.cursor()
        cursor.execute(get_query)
        latest_id = cursor.fetchone()
    except Exception as e:
        return str(e)

    if latest_id is not None:
        latest_id = int(latest_id[0]) + 1
    else:
        latest_id = 1

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    # Upload Img
    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (str(latest_id), first_name, last_name, email, location, phone, position))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp_id_" + str(latest_id) + "_image_file"
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
    print("Done Employee Table...")

    #Add attendance
    attendance_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(attendance_sql, (str(latest_id), str(latest_id), "", "", "", ""))
        db_conn.commit()

    finally:
        cursor.close()
    print("Done Attendance Table...")

    #Add Payroll
    leave_sql = "INSERT INTO payroll VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(leave_sql, (str(latest_id), str(latest_id), "", "0"))
        db_conn.commit()

    finally:
        cursor.close()
    print("Done Payroll Table...")

    print("Uploaded successful...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    if request.method == 'POST':
        emp_id = request.form['emp_id']
        query_string = "SELECT * FROM employee WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(query_string, emp_id)
        employee = cursor.fetchall()

    else:
        employee = ""

    return render_template('GetEmp.html', employee=employee)

@app.route("/employee", methods=['GET', 'POST'])
def Employee():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    employees = cursor.fetchall()
    cursor.close()

    count = "SELECT COUNT(*) FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(count)
    count_emp = cursor.fetchall()

    return render_template('Employee.html', employees=employees, count_emp=count_emp[0][0])

@app.route('/employee/<string:id>/delete', methods=['GET', 'POST'])
def delete(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    employee = cursor.fetchall()

    if request.method == 'POST':
        #Delete Payroll Row
        delete_leaves_sql = "DELETE FROM leaves WHERE emp_id=%s"
        cursor = db_conn.cursor()
        cursor.execute(delete_leaves_sql, id)
        db_conn.commit()
        print("Leave ID " + id + " successfully been deleted from leave.")

        #Delete Payroll Row
        delete_payroll_sql = "DELETE FROM payroll WHERE payroll_id=%s"
        cursor = db_conn.cursor()
        cursor.execute(delete_payroll_sql, id)
        db_conn.commit()
        print("Payroll ID " + id + " successfully been deleted from payroll.")

        #Delete Attendance Row
        delete_attendance_sql = "DELETE FROM attendance WHERE attendance_id=%s"
        cursor = db_conn.cursor()
        cursor.execute(delete_attendance_sql, id)
        db_conn.commit()
        print("Attendance ID " + id + " successfully been deleted from attendance.")

        #Delete Employee Row
        delete_employee_sql = "DELETE FROM employee WHERE emp_id=%s"
        cursor = db_conn.cursor()
        cursor.execute(delete_employee_sql, id)
        db_conn.commit()
        print("Employeee ID " + id + " successfully been deleted from employee.")



        return redirect('/employee')

    return render_template('EditEmp.html', deleteEmp=employee)

@app.route('/employee/<string:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )

    query_string = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(query_string, id)
    employee = cursor.fetchall()

    if request.method == 'POST':

        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        location = request.form['location']
        phone = request.form['phone']
        position = request.form['position']

        try:
            update_sql = "UPDATE employee SET first_name=%s, last_name=%s, email=%s, location=%s, phone=%s, position=%s WHERE emp_id=%s"
            cursor = db_conn.cursor()

            cursor.execute(update_sql, (first_name, last_name, email, location, phone, position, emp_id))
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

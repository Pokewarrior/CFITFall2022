from warnings import catch_warnings
from app import app
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from datetime import datetime
from app.models import user, section_a, section_b, section_c, section_d, section_e, assessments, admin, student, instructor, client
import sys
from sqlalchemy import delete
import smtplib

#################################################
#
# Home
#
#################################################
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])

def login():
    
    if request.method == 'POST':
        email = request.form.get("email")
        print(email, file=sys.stderr)
        password = request.form.get("password")
        print(password, file=sys.stderr)

        # Query DB for users by username
        users = db.session.query(user).filter_by(email=email).first()
        
        if users is None or not users.check_password(password):
            print('[EVENT] :::::: Login failed!!! ::::::', file=sys.stderr)
            flash('Invalid Username or Password provided', 'warning')
            return redirect(url_for('login'))
            
   
        # login_user is a flask_login function that starts a session
        else:
            login_user(users)
            print('[EVENT] :::::: user: ' + users.username + ' logged in on ' + str(datetime.utcnow()) + '::::::', file=sys.stderr)
       
        # Check user level
        if is_admin():
            return redirect(url_for('admin_dashboard'))
        if is_instructor():
            return redirect(url_for('instructor_dashboard'))
        if is_student():
            return redirect(url_for('student_dashboard'))
    return render_template('login.html')
    
#################################################
#
# LOGOUT
#
#################################################
@app.route('/logout')
@login_required
def logout():
    session.pop('Username',None)
    logout_user()
    return render_template('logout.html')

#################################################
#
# getsession - used by Flask to keep track of 
# user in this session - this needs to be expanded
#
#################################################
@app.route('/getsession')
def getsession():
    if 'Username' in session:
        Username = session['Username']
        return "Welcome {Username}"


#################################################
#
# soon - used to display the coming soon page
#
#################################################
@app.route('/soon',methods=['GET', 'POST'])
@login_required
def soon():
    return render_template('soon.html')
#################################################
#
# dashboard - this will redirect the user to the
# appropriate dashboard based on user role
#
#################################################
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
        
    if is_instructor():
        return redirect(url_for('instructor_dashboard'))
       
    if is_student():
        return redirect(url_for('student_dashboard'))
    return render_template('admin.html')

#################################################
#
# Admin Dashboard
#
#################################################
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if is_admin():
        print(current_user, file=sys.stderr)
        if request.method=="POST":
            if 'addadmin' in request.form:
                id=request.form["id"]
                username=request.form["username"]
                email=request.form["email"]
                password_hash=request.form["password_hash"]
                # change so that id is automatically assigned to avoid duplication
                new_user=user(id=id, role='admin',username=username,email=email,password_hash=password_hash)
                new_admin=admin(id=id, username=username, email=email)
                new_instructor=instructor(id=id, username=username,email=email)
                new_user.set_password(password_hash)

                check_admin = db.session.query(admin).filter_by(id=id).first()
                check_password = db.session.query(user).filter_by(password_hash=password_hash).first()
               
                if check_admin is not None:
                    return render_template("exists.html")
                                                   
                else: 
                    db.session.add(new_user)
                    db.session.add(new_instructor)
                    db.session.add(new_admin)
                    db.session.commit()
                
            elif 'deleteadmin' in request.form:
                id=request.form["id"]
                new_admin=admin(id=id)
                new_user=user(id=id)
                delete_admin=new_admin.query.get_or_404(id)
                delete_user=new_user.query.get_or_404(id)
                db.session.delete(delete_admin)
                db.session.delete(delete_user)
                db.session.commit()

        if request.method=="POST":
                if 'addinstructor' in request.form:
                    id=request.form["id"]
                    username=request.form["username"]
                    email=request.form["email"]
                    password_hash=request.form["password_hash"]
                    new_user=user(id=id,role='instructor', username=username,email=email,password_hash=password_hash)           
                    new_instructor=instructor(id=id, username=username,email=email)
                    new_user.set_password(password_hash)
                    check_password = db.session.query(user).filter_by(password_hash=password_hash).first()    
                    check_instructor = db.session.query(instructor).filter_by(id=id).first()
                    if check_instructor is not None:
                        return render_template("exists.html")
                    else: 
                        db.session.add(new_user)
                        db.session.add(new_instructor)                        
                        db.session.commit()
                        
                elif 'deleteinstructor' in request.form:
                    id=request.form["id"]
                    new_instructor=instructor(id=id)
                    new_user=user(id=id)
                    delete_instructor=new_instructor.query.get_or_404(id)
                    delete_user=new_user.query.get_or_404(id)
                    db.session.delete(delete_instructor)
                    db.session.delete(delete_user)
                    db.session.commit()
                
        if request.method=="POST":
                if 'addstudent' in request.form: 
                    id=request.form["id"]
                    student_name=request.form["student_name"]
                    username=request.form["student_name"]
                    email=request.form["email"]
                    password_hash=request.form["password_hash"]
                               
                    class_year=request.form["class_year"]
                    course=request.form["course"]
                    semester=request.form["semester"]
                    course_instructor=request.form["course_instructor"]
                
                    new_user=user(id=id,role='student',username=username,email=email,password_hash=password_hash)
                    new_student=student(id=id,student_id=id,class_year=class_year,course=course,semester=semester,student_name=student_name,course_instructor=course_instructor,email=email)
                    new_assessment=assessments(student_id=id,session_id=None,course=course,semester=semester,student_name=student_name,course_instructor=course_instructor)
                    new_user.set_password(password_hash)
                                
                    check_student = db.session.query(student).filter_by(id=id).first()
                    if check_student is not None:
                        return render_template("exists.html")
                    else:
                        #users.set_password(password_hash)
                        db.session.add(new_user)
                        db.session.add(new_assessment)
                        db.session.add(new_student)
                        db.session.commit()
                    
                elif 'deletestudent' in request.form:
                    id=request.form["id"]
                    new_student=student(id=id)
                    new_user=user(id=id)
                    delete_student=new_student.query.get_or_404(id)
                    delete_user=new_user.query.get_or_404(id)
                    db.session.delete(delete_student)
                    db.session.delete(delete_user)
                    db.session.commit()

                return render_template("admin.html", 
                    admin=user.query.filter_by(role='admin').all(),
                    instructor=instructor.query.all(),
                    values=assessments.query.all(),
                    student=student.query.all())

        return render_template("admin.html",
                                        admin=user.query.filter_by(role='admin').all(),
                                        instructor=instructor.query.all(),
                                        values=assessments.query.all(), 
                                        student=student.query.all())
    else:                
        return render_template("error.html")

#################################################
#
# Instructor Dashboard
#
#################################################
@app.route('/instructor', methods=['GET', 'POST'])
@login_required
def instructor_dashboard():
    if is_admin() or is_instructor():
        print('Instructor Dashboard', file=sys.stderr)
        current_instructor = current_user.username
        print(current_instructor, file=sys.stderr)
        # get data from HTML page
        if request.method=="POST":
            id=request.form["id"]
            session_id = request.form["id"]
            session["id"] = id
            print('instructor', file=sys.stderr)
            print(session["id"], file=sys.stderr)
            print(session_id, file=sys.stderr)
            name=request.form["name"]
            date=request.form["date"]
            disorder=request.form["disorder"]
            new_client=client(id=id,name=name,date=date,disorder=disorder, session_id=session_id)
               
            if 'addclient' in request.form:
                check_client = db.session.query(client).filter_by(id=id).first()
                if check_client is not None:
                     return render_template("exists.html")
                else:
                    db.session.add(new_client)
                    db.session.commit()
            elif 'deleteclient' in request.form:
                delete_client=new_client.query.get_or_404(id)
                db.session.delete(delete_client)
                db.session.commit()
  
            return render_template("instructor.html", 
            values=assessments.query.filter_by(course_instructor=current_instructor).all(), 
            client=client.query.all())
        
        return render_template("instructor.html", 
                values=db.session.query(assessments).filter_by(course_instructor=current_instructor).all(), 
                client=client.query.all())
    else:                
        return render_template("error.html")

#################################################
#
# Student Dashboard
#
#################################################
@app.route('/student',  methods=['GET', 'POST'])
@login_required
def student_dashboard():
    if is_student():
        print('Student Dashboard', file=sys.stderr)
        student_id=current_user.id
        session["student_id"] = student_id
        print(student_id, file=sys.stderr)
        if request.method=="POST":
            student_id=current_user.id
            session["student_id"] = student_id
            print(student_id, file=sys.stderr)
            return render_template('student.html', values=db.session.query(section_a).filter_by(student_id=student_id).all())
        
        return render_template('student.html', values=db.session.query(section_a).filter_by(student_id=student_id).all())
    else:                
        return render_template("error.html")

#################################################
#
# View
#   The main assessment page
#   this will load a previously completed assessment
#   and display the ratings and comments    
#
#################################################
@app.route('/view', methods=['GET', 'POST'])
@login_required
def view_assessment():
    session["is_new"] = 0
    print(session["is_new"], file=sys.stderr)
    print('View assessment for:', file=sys.stderr)
     
    if request.method=="POST":
        assessment_id=request.form.get('session_id')
        student_id=request.form.get('student_id')
        print('student_id:', file=sys.stderr)
        print(student_id, file=sys.stderr)
        print('assessment_id:', file=sys.stderr)
        print(assessment_id, file=sys.stderr)
      
        #check for empty assessment
        if assessment_id is None:
            print('IGNORED!', file=sys.stderr)
            return render_template("invalid.html")
    else:
        student_id = session["student_id"]
        print(student_id, file=sys.stderr)
   
    
    check_student = db.session.query(student).filter_by(id=student_id).first()
    current_student = db.session.query(section_a).filter_by(student_id=student_id).first()

    #check for empty assessment
    if check_student.session_id is None:
        return render_template("invalid.html")

    student_name = current_student.student_name
    print('student_name:', file=sys.stderr)
    print(student_name, file=sys.stderr)
    course = current_student.course
    print('course:', file=sys.stderr)
    print(course, file=sys.stderr)
    semester = current_student.semester
    print('semester:', file=sys.stderr)
    print(semester, file=sys.stderr)
    
    print('session_id:', file=sys.stderr)
    
    print('session_id:', assessment_id)
    session_id=assessment_id
    print('session_id:', file=sys.stderr)
    print(session_id, file=sys.stderr)
    session["assessment_id"] = assessment_id
    print("assessment_id from session:", file=sys.stderr)
    print(session["assessment_id"], file=sys.stderr)
  
    # grab the session id from the assessment. 
    client_name=db.session.query(section_a.client).filter_by(session_id=assessment_id).first()
    client_disorder=db.session.query(section_a.disorder).filter_by(session_id=assessment_id).first()
    course_instructor=db.session.query(section_a.course_instructor).filter_by(session_id=assessment_id).first()
    
    #############################
    # Section A
    #############################
    # Ratings
    a1_rating = db.session.query(section_a.a1_rating).filter_by(session_id=assessment_id).first()
    a2_rating = db.session.query(section_a.a2_rating).filter_by(session_id=assessment_id).first()
    a3_rating = db.session.query(section_a.a3_rating).filter_by(session_id=assessment_id).first()
    a4_rating = db.session.query(section_a.a4_rating).filter_by(session_id=assessment_id).first()
    a5_rating = db.session.query(section_a.a5_rating).filter_by(session_id=assessment_id).first()
   
    # Instructor Comments
    a1_instructor_comment = db.session.query(section_a.a1_instructor_comment).filter_by(session_id=assessment_id).first()
    a2_instructor_comment = db.session.query(section_a.a2_instructor_comment).filter_by(session_id=assessment_id).first()
    a3_instructor_comment = db.session.query(section_a.a3_instructor_comment).filter_by(session_id=assessment_id).first()
    a4_instructor_comment = db.session.query(section_a.a4_instructor_comment).filter_by(session_id=assessment_id).first()
    a5_instructor_comment = db.session.query(section_a.a5_instructor_comment).filter_by(session_id=assessment_id).first()

    # Student Comments
    a1_student_comment = db.session.query(section_a.a1_student_comment).filter_by(session_id=assessment_id).first()
    a2_student_comment = db.session.query(section_a.a2_student_comment).filter_by(session_id=assessment_id).first()
    a3_student_comment = db.session.query(section_a.a3_student_comment).filter_by(session_id=assessment_id).first()
    a4_student_comment = db.session.query(section_a.a4_student_comment).filter_by(session_id=assessment_id).first()
    a5_student_comment = db.session.query(section_a.a5_student_comment).filter_by(session_id=assessment_id).first()


    #############################
    # Section B
    #############################
    # Ratings
    b1_rating = db.session.query(section_b.b1_rating).filter_by(session_id=assessment_id).first()
    b2_rating = db.session.query(section_b.b2_rating).filter_by(session_id=assessment_id).first()
    b3_rating = db.session.query(section_b.b3_rating).filter_by(session_id=assessment_id).first()
    b4_rating = db.session.query(section_b.b4_rating).filter_by(session_id=assessment_id).first()

    # Instructor Comments
    b1_instructor_comment = db.session.query(section_b.b1_instructor_comment).filter_by(session_id=assessment_id).first()
    b2_instructor_comment = db.session.query(section_b.b2_instructor_comment).filter_by(session_id=assessment_id).first()
    b3_instructor_comment = db.session.query(section_b.b3_instructor_comment).filter_by(session_id=assessment_id).first()
    b4_instructor_comment = db.session.query(section_b.b4_instructor_comment).filter_by(session_id=assessment_id).first()

    # Student Comments
    b1_student_comment = db.session.query(section_b.b1_student_comment).filter_by(session_id=assessment_id).first()
    b2_student_comment = db.session.query(section_b.b2_student_comment).filter_by(session_id=assessment_id).first()
    b3_student_comment = db.session.query(section_b.b3_student_comment).filter_by(session_id=assessment_id).first()
    b4_student_comment = db.session.query(section_b.b4_student_comment).filter_by(session_id=assessment_id).first()


    #############################
    # Section C
    #############################
    # Ratings
    c1_rating = db.session.query(section_c.c1_rating).filter_by(session_id=assessment_id).first()
    c2_rating = db.session.query(section_c.c2_rating).filter_by(session_id=assessment_id).first()
    c3_rating = db.session.query(section_c.c3_rating).filter_by(session_id=assessment_id).first()
    c4_rating = db.session.query(section_c.c4_rating).filter_by(session_id=assessment_id).first()
    c5_rating = db.session.query(section_c.c5_rating).filter_by(session_id=assessment_id).first()
    c6_rating = db.session.query(section_c.c6_rating).filter_by(session_id=assessment_id).first()
    c7_rating = db.session.query(section_c.c7_rating).filter_by(session_id=assessment_id).first()
    c8_rating = db.session.query(section_c.c8_rating).filter_by(session_id=assessment_id).first()
    c9_rating = db.session.query(section_c.c9_rating).filter_by(session_id=assessment_id).first()
    c10_rating = db.session.query(section_c.c10_rating).filter_by(session_id=assessment_id).first()
    c11_rating = db.session.query(section_c.c11_rating).filter_by(session_id=assessment_id).first()
    c12_rating = db.session.query(section_c.c12_rating).filter_by(session_id=assessment_id).first()
    c13_rating = db.session.query(section_c.c13_rating).filter_by(session_id=assessment_id).first()

    # Instructor Comments
    c1_instructor_comment = db.session.query(section_c.c1_instructor_comment).filter_by(session_id=assessment_id).first()
    c2_instructor_comment = db.session.query(section_c.c2_instructor_comment).filter_by(session_id=assessment_id).first()
    c3_instructor_comment = db.session.query(section_c.c3_instructor_comment).filter_by(session_id=assessment_id).first()
    c4_instructor_comment = db.session.query(section_c.c4_instructor_comment).filter_by(session_id=assessment_id).first()
    c5_instructor_comment = db.session.query(section_c.c5_instructor_comment).filter_by(session_id=assessment_id).first()
    c6_instructor_comment = db.session.query(section_c.c6_instructor_comment).filter_by(session_id=assessment_id).first()
    c7_instructor_comment = db.session.query(section_c.c7_instructor_comment).filter_by(session_id=assessment_id).first()
    c8_instructor_comment = db.session.query(section_c.c8_instructor_comment).filter_by(session_id=assessment_id).first()
    c9_instructor_comment = db.session.query(section_c.c9_instructor_comment).filter_by(session_id=assessment_id).first()
    c10_instructor_comment = db.session.query(section_c.c10_instructor_comment).filter_by(session_id=assessment_id).first()
    c11_instructor_comment = db.session.query(section_c.c11_instructor_comment).filter_by(session_id=assessment_id).first()
    c12_instructor_comment = db.session.query(section_c.c12_instructor_comment).filter_by(session_id=assessment_id).first()
    c13_instructor_comment = db.session.query(section_c.c13_instructor_comment).filter_by(session_id=assessment_id).first()

    # Student Comments
    c1_student_comment = db.session.query(section_c.c1_student_comment).filter_by(session_id=assessment_id).first()
    c2_student_comment = db.session.query(section_c.c2_student_comment).filter_by(session_id=assessment_id).first()
    c3_student_comment = db.session.query(section_c.c3_student_comment).filter_by(session_id=assessment_id).first()
    c4_student_comment = db.session.query(section_c.c4_student_comment).filter_by(session_id=assessment_id).first()
    c5_student_comment = db.session.query(section_c.c5_student_comment).filter_by(session_id=assessment_id).first()
    c6_student_comment = db.session.query(section_c.c6_student_comment).filter_by(session_id=assessment_id).first()
    c7_student_comment = db.session.query(section_c.c7_student_comment).filter_by(session_id=assessment_id).first()
    c8_student_comment = db.session.query(section_c.c8_student_comment).filter_by(session_id=assessment_id).first()
    c9_student_comment = db.session.query(section_c.c9_student_comment).filter_by(session_id=assessment_id).first()
    c10_student_comment = db.session.query(section_c.c10_student_comment).filter_by(session_id=assessment_id).first()
    c11_student_comment = db.session.query(section_c.c11_student_comment).filter_by(session_id=assessment_id).first()
    c12_student_comment = db.session.query(section_c.c12_student_comment).filter_by(session_id=assessment_id).first()
    c13_student_comment = db.session.query(section_c.c13_student_comment).filter_by(session_id=assessment_id).first()


    #########################
    # Section D
    #############################
    # Ratings
    d1_rating = db.session.query(section_d.d1_rating).filter_by(session_id=assessment_id).first()
    d2_rating = db.session.query(section_d.d2_rating).filter_by(session_id=assessment_id).first()
    d3_rating = db.session.query(section_d.d3_rating).filter_by(session_id=assessment_id).first()

    # Instructor Comments
    d1_instructor_comment = db.session.query(section_d.d1_instructor_comment).filter_by(session_id=assessment_id).first()
    d2_instructor_comment = db.session.query(section_d.d2_instructor_comment).filter_by(session_id=assessment_id).first()
    d3_instructor_comment = db.session.query(section_d.d3_instructor_comment).filter_by(session_id=assessment_id).first()

    # Student Comments
    d1_student_comment = db.session.query(section_d.d1_student_comment).filter_by(session_id=assessment_id).first()
    d2_student_comment = db.session.query(section_d.d2_student_comment).filter_by(session_id=assessment_id).first()
    d3_student_comment = db.session.query(section_d.d3_student_comment).filter_by(session_id=assessment_id).first()


    #############################
    # Section E
    #############################
    # Ratings
    e1_rating = db.session.query(section_e.e1_rating).filter_by(session_id=assessment_id).first()
    e2_rating = db.session.query(section_e.e2_rating).filter_by(session_id=assessment_id).first()

    # Instructor Comments
    e1_instructor_comment = db.session.query(section_e.e1_instructor_comment).filter_by(session_id=assessment_id).first()
    e2_instructor_comment = db.session.query(section_e.e2_instructor_comment).filter_by(session_id=assessment_id).first()

    # Student Comments
    e1_student_comment = db.session.query(section_e.e1_student_comment).filter_by(session_id=assessment_id).first()
    e2_student_comment = db.session.query(section_e.e2_student_comment).filter_by(session_id=assessment_id).first()

    return render_template('assessment.html',  
                            a1_rating=a1_rating[0], a1_instructor_comment=a1_instructor_comment[0], a1_student_comment=a1_student_comment[0],
                            a2_rating=a2_rating[0], a2_instructor_comment=a2_instructor_comment[0], a2_student_comment=a2_student_comment[0],
                            a3_rating=a3_rating[0], a3_instructor_comment=a3_instructor_comment[0], a3_student_comment=a3_student_comment[0],
                            a4_rating=a4_rating[0], a4_instructor_comment=a4_instructor_comment[0], a4_student_comment=a4_student_comment[0],
                            a5_rating=a5_rating[0], a5_instructor_comment=a5_instructor_comment[0], a5_student_comment=a5_student_comment[0],
                            b1_rating=b1_rating[0], b1_instructor_comment=b1_instructor_comment[0], b1_student_comment=b1_student_comment[0],
                            b2_rating=b2_rating[0], b2_instructor_comment=b2_instructor_comment[0], b2_student_comment=b2_student_comment[0],
                            b3_rating=b3_rating[0], b3_instructor_comment=b3_instructor_comment[0], b3_student_comment=b3_student_comment[0],
                            b4_rating=b4_rating[0], b4_instructor_comment=b4_instructor_comment[0], b4_student_comment=b4_student_comment[0],
                            c1_rating=c1_rating[0], c1_instructor_comment=c1_instructor_comment[0], c1_student_comment=c1_student_comment[0],
                            c2_rating=c2_rating[0], c2_instructor_comment=c2_instructor_comment[0], c2_student_comment=c2_student_comment[0],
                            c3_rating=c3_rating[0], c3_instructor_comment=c3_instructor_comment[0], c3_student_comment=c3_student_comment[0],
                            c4_rating=c4_rating[0], c4_instructor_comment=c4_instructor_comment[0], c4_student_comment=c4_student_comment[0],
                            c5_rating=c5_rating[0], c5_instructor_comment=c5_instructor_comment[0], c5_student_comment=c5_student_comment[0],
                            c6_rating=c6_rating[0], c6_instructor_comment=c6_instructor_comment[0], c6_student_comment=c6_student_comment[0],
                            c7_rating=c7_rating[0], c7_instructor_comment=c7_instructor_comment[0], c7_student_comment=c7_student_comment[0],
                            c8_rating=c8_rating[0], c8_instructor_comment=c8_instructor_comment[0], c8_student_comment=c8_student_comment[0],
                            c9_rating=c9_rating[0], c9_instructor_comment=c9_instructor_comment[0], c9_student_comment=c9_student_comment[0],
                            c10_rating=c10_rating[0], c10_instructor_comment=c10_instructor_comment[0], c10_student_comment=c10_student_comment[0],
                            c11_rating=c11_rating[0], c11_instructor_comment=c11_instructor_comment[0], c11_student_comment=c11_student_comment[0],
                            c12_rating=c12_rating[0], c12_instructor_comment=c12_instructor_comment[0], c12_student_comment=c12_student_comment[0],
                            c13_rating=c13_rating[0], c13_instructor_comment=c13_instructor_comment[0], c13_student_comment=c13_student_comment[0],
                            d1_rating=d1_rating[0], d1_instructor_comment=d1_instructor_comment[0], d1_student_comment=d1_student_comment[0],
                            d2_rating=d2_rating[0], d2_instructor_comment=d2_instructor_comment[0], d2_student_comment=d2_student_comment[0],
                            d3_rating=d3_rating[0], d3_instructor_comment=d3_instructor_comment[0], d3_student_comment=d3_student_comment[0],
                            e1_rating=e1_rating[0], e1_instructor_comment=e1_instructor_comment[0], e1_student_comment=e1_student_comment[0],
                            e2_rating=e2_rating[0], e2_instructor_comment=e2_instructor_comment[0], e2_student_comment=e2_student_comment[0],
                            id=student_id, student_name=student_name, course=course, semester=semester,  course_instructor=course_instructor[0], client_name=client_name[0], client_disorder=client_disorder[0]) 

#################################################
#
# select_client - this will select the client for
# when 'New Assessment' is selected
#
# This functionality shoudl be moved to the assessment
# form as a drop down
#
#################################################
@app.route('/select_client', methods=['GET', 'POST'])
@login_required
def select_client():
    if request.method=="POST":  

        student_id=request.form["student_id"]
        #student_id = session['student_id']
        print('Assigned Client for: ',file=sys.stderr)
        print(student_id,file=sys.stderr )
        student_name=request.form["student_name"]
        print('student_name: ',file=sys.stderr )
        print(student_name ,file=sys.stderr )
     
        #class_year=request.form["class_year"]
        course=request.form["course"]
        semester=request.form["semester"]
    

        print('Current user: ',file=sys.stderr)
        print(current_user, file=sys.stderr)

        current_student = db.session.query(student).filter_by(id=student_id).first()
        student_name = current_student.student_name
        course = current_student.course
        semester = current_student.semester
        session['student_id'] = student_id
       
    return render_template("client.html", values=client.query.all(),id=student_id)
    
#################################################
#
# new_assessment
# This creates a new assessment with all ratings
# set to 0
#
#################################################   
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_assessment():

   
    if request.method=="POST":  
        session["is_new"] = 1
        student_id = session['student_id']
        print(student_id, file=sys.stderr )
        current_student = db.session.query(student).filter_by(id=student_id).first()
        client_id=request.form.get("id")
        current_client=db.session.query(client).filter_by(id=client_id).first()
        print('New Assessment for Client: ',file=sys.stderr )
        print(student_id,file=sys.stderr )
        session['id'] = request.form.get("id")
        print(session['id'],file=sys.stderr ) 
        course_instructor = current_user.username
        print(course_instructor, file=sys.stderr )
        session['course_instructor'] = current_user.username
        print(session['course_instructor'], file=sys.stderr )
        session['date'] = request.form.get("date")
        print(session['date'],file=sys.stderr )
        student_name = current_student.student_name
        print(student_name, file=sys.stderr )
        course = current_student.course
        session['course'] = current_student.course
        print(session['course'], file=sys.stderr )
        semester = current_student.semester
        session['semester'] = current_student.semester  
        print(session['semester'], file=sys.stderr )
        client_name = current_client.name
        session['client_name'] = current_client.name
        print(session['client_name'], file=sys.stderr )
        client_disorder = current_client.disorder
        session['client_disorder'] = current_client.disorder
        print(session['client_disorder'], file=sys.stderr )    
        studentemail = current_student.email
    else:
        print("ERROR", file=sys.stderr)


    # Start an assessment with all ratings at N/A (rating = 0)
    assessment_a = section_a(
                           a1_rating=0,                  
                           a2_rating=0,  
                           a3_rating=0,
                           a4_rating=0,
                           a5_rating=0, 
                           student_id=student_id, student_name=student_name)
    
    assessment_b = section_b(
                           b1_rating=0,                  
                           b2_rating=0,  
                           b3_rating=0,
                           b4_rating=0,
                           student_id=student_id, student_name=student_name)
    
    assessment_c = section_c(
                           c1_rating=0,                  
                           c2_rating=0,  
                           c3_rating=0,
                           c4_rating=0,
                           c5_rating=0, 
                           c6_rating=0, 
                           c7_rating=0, 
                           c8_rating=0, 
                           c9_rating=0, 
                           c10_rating=0, 
                           c11_rating=0, 
                           c12_rating=0, 
                           c13_rating=0, 
                           student_id=student_id, student_name=student_name)
   
    assessment_d = section_d(
                           d1_rating=0,                  
                           d2_rating=0,  
                           d3_rating=0,
                           student_id=student_id, student_name=student_name)

    
    assessment_e = section_e(
                           e1_rating=0,                  
                           e2_rating=0,  
                           student_id=student_id, student_name=student_name)

   
    db.session.add(assessment_a)
    db.session.add(assessment_b)
    db.session.add(assessment_c)
    db.session.add(assessment_d)
    db.session.add(assessment_e)
    #
    try:
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('scsucfittemp@gmail.com','qyfjtpwmfbxtoeej')
        message = """Subject: New Acessment made 

        \n A new accessment was made by your instructor \n"""
        server.sendmail('scsucfittemp@gmail.com',studentemail , message)
        print('mail sent')
        server.quit()
        print('email session closed')
    except smtplib.SMTPRecipientsRefused:
        print("invalid recieving email")
    except smtplib.SMTPHeloError: 
        print("Email failed to send")
    except smtplib.SMTPAuthenticationError:
        print("login error for account")
    except smtplib.SMTPDataError:
        print("data send error")

    except Exception as e: 
        print("other error: " + str(e))

    


    return render_template('assessment.html',  
                            a1_rating=0,
                            a2_rating=0,  
                            a3_rating=0,
                            a4_rating=0,
                            a5_rating=0,
                            b1_rating=0,
                            b2_rating=0,
                            b3_rating=0,
                            b4_rating=0,
                            c1_rating=0,
                            c2_rating=0,
                            c3_rating=0,
                            c4_rating=0,
                            c5_rating=0,
                            c6_rating=0,
                            c7_rating=0,
                            c8_rating=0,
                            c9_rating=0,
                            c10_rating=0,
                            c11_rating=0,
                            c12_rating=0,
                            c13_rating=0,
                            d1_rating=0,
                            d2_rating=0,
                            d3_rating=0,
                            e1_rating=0,
                            e2_rating=0,
                            id=student_id, student_name=student_name, course=course, semester=semester, 
                            course_instructor=course_instructor, 
                            client_name=client_name, client_disorder=client_disorder) 



#################################################
#
# save_assessment
# This saves an assessment 
#
#################################################   
@app.route('/save', methods=['GET', 'POST'])
@login_required
def save_assessment():
    if is_student():
        return render_template("error.html")
    print('Saving Assessment.....', file=sys.stderr) 
 
    is_new = session["is_new"]
    print('Modify assessment: ', file=sys.stderr)
    print(is_new, file=sys.stderr)
    if request.method == "POST":
      
        student_id = session['student_id']
        print(student_id, file=sys.stderr)
        current_student = db.session.query(user).filter_by(id=student_id).first()
        student_name = current_student.username
        print(current_student.username, file=sys.stderr)
        date = None #session['date']
        print(date, file=sys.stderr)
        course = session['course'] 
        print(course, file=sys.stderr)
        semester = session['semester'] 
        print(semester, file=sys.stderr)
        client = session['client_name']
        print(client, file=sys.stderr)
        disorder= session['client_disorder'] 
        print(disorder, file=sys.stderr)
        course_instructor = session['course_instructor'] 
        assessment_id = None #session["assessment_id"] #temp change to none for testing. 
        print(course_instructor, file=sys.stderr)
        print('saving assessment_id', file=sys.stderr)
        print(assessment_id, file=sys.stderr)

      
 

        # get data from HTML assessment form page
        a1_rating = request.form.get("a1_rating")
        a2_rating = request.form.get("a2_rating")
        a3_rating = request.form.get("a3_rating")
        a4_rating = request.form.get("a4_rating")
        a5_rating = request.form.get("a5_rating")
                
        a1_instructor_comment = request.form.get("a1_instructor_comment")
        a2_instructor_comment = request.form.get("a2_instructor_comment")
        a3_instructor_comment = request.form.get("a3_instructor_comment")
        a4_instructor_comment = request.form.get("a4_instructor_comment")
        a5_instructor_comment = request.form.get("a5_instructor_comment")

        a1_student_comment = request.form.get("a1_student_comment")
        a2_student_comment = request.form.get("a2_student_comment")
        a3_student_comment = request.form.get("a3_student_comment")
        a4_student_comment = request.form.get("a4_student_comment")
        a5_student_comment = request.form.get("a5_student_comment")

        # save section A data in section_a object
        assessment_a = section_a(
                            a1_rating=a1_rating, a1_instructor_comment=a1_instructor_comment, a1_student_comment=a1_student_comment,
                            a2_rating=a2_rating, a2_instructor_comment=a2_instructor_comment, a2_student_comment=a2_student_comment,
                            a3_rating=a3_rating, a3_instructor_comment=a3_instructor_comment, a3_student_comment=a3_student_comment,
                            a4_rating=a4_rating, a4_instructor_comment=a4_instructor_comment, a4_student_comment=a4_student_comment,
                            a5_rating=a5_rating, a5_instructor_comment=a5_instructor_comment, a5_student_comment=a5_student_comment,
                            student_id=student_id, student_name=student_name, course_instructor=course_instructor, course=course, semester=semester, date=date, client=client, disorder=disorder)

        
        
        b1_rating = request.form.get("b1_rating")
        b2_rating = request.form.get("b2_rating")
        b3_rating = request.form.get("b3_rating")
        b4_rating = request.form.get("b4_rating")
 
        b1_instructor_comment = request.form.get("b1_instructor_comment")
        b2_instructor_comment = request.form.get("b2_instructor_comment")
        b3_instructor_comment = request.form.get("b3_instructor_comment")
        b4_instructor_comment = request.form.get("b4_instructor_comment")

        b1_student_comment = request.form.get("b1_student_comment")
        b2_student_comment = request.form.get("b2_student_comment")
        b3_student_comment = request.form.get("b3_student_comment")
        b4_student_comment = request.form.get("b4_student_comment")

        # save section B data in section_b object
        assessment_b = section_b(
                            b1_rating=b1_rating, b1_instructor_comment=b1_instructor_comment, b1_student_comment=b1_student_comment,
                            b2_rating=b2_rating, b2_instructor_comment=b2_instructor_comment, b2_student_comment=b2_student_comment,
                            b3_rating=b3_rating, b3_instructor_comment=b3_instructor_comment, b3_student_comment=b3_student_comment,
                            b4_rating=b4_rating, b4_instructor_comment=b4_instructor_comment, b4_student_comment=b4_student_comment,
                            student_id=student_id, student_name=student_name, course_instructor=course_instructor, course=course, semester=semester, date=date, client=client, disorder=disorder)

   

        c1_rating = request.form.get("c1_rating")
        c2_rating = request.form.get("c2_rating")
        c3_rating = request.form.get("c3_rating")
        c4_rating = request.form.get("c4_rating")
        c5_rating = request.form.get("c5_rating")
        c6_rating = request.form.get("c6_rating")
        c7_rating = request.form.get("c7_rating")
        c8_rating = request.form.get("c8_rating")
        c9_rating = request.form.get("c9_rating")
        c10_rating = request.form.get("c10_rating")
        c11_rating = request.form.get("c11_rating")
        c12_rating = request.form.get("c12_rating")
        c13_rating = request.form.get("c13_rating")

        c1_instructor_comment = request.form.get("c1_instructor_comment")
        c2_instructor_comment = request.form.get("c2_instructor_comment")
        c3_instructor_comment = request.form.get("c3_instructor_comment")
        c4_instructor_comment = request.form.get("c4_instructor_comment")
        c5_instructor_comment = request.form.get("c5_instructor_comment")
        c6_instructor_comment = request.form.get("c6_instructor_comment")
        c7_instructor_comment = request.form.get("c7_instructor_comment")
        c8_instructor_comment = request.form.get("c8_instructor_comment")
        c9_instructor_comment = request.form.get("c9_instructor_comment")
        c10_instructor_comment = request.form.get("c10_instructor_comment")
        c11_instructor_comment = request.form.get("c11_instructor_comment")
        c12_instructor_comment = request.form.get("c12_instructor_comment")
        c13_instructor_comment = request.form.get("c13_instructor_comment")

        c1_student_comment = request.form.get("c1_student_comment")
        c2_student_comment = request.form.get("c2_student_comment")
        c3_student_comment = request.form.get("c3_student_comment")
        c4_student_comment = request.form.get("c4_student_comment")
        c5_student_comment = request.form.get("c5_student_comment")
        c6_student_comment = request.form.get("c6_student_comment")
        c7_student_comment = request.form.get("c7_student_comment")
        c8_student_comment = request.form.get("c8_student_comment")
        c9_student_comment = request.form.get("c9_student_comment")
        c10_student_comment = request.form.get("c10_student_comment")
        c11_student_comment = request.form.get("c11_student_comment")
        c12_student_comment = request.form.get("c12_student_comment")
        c13_student_comment = request.form.get("c13_student_comment")

        # save section C data in section_c object
        assessment_c = section_c(
                            c1_rating=c1_rating, c1_instructor_comment=c1_instructor_comment, c1_student_comment=c1_student_comment,
                            c2_rating=c2_rating, c2_instructor_comment=c2_instructor_comment, c2_student_comment=c2_student_comment,
                            c3_rating=c3_rating, c3_instructor_comment=c3_instructor_comment, c3_student_comment=c3_student_comment,
                            c4_rating=c4_rating, c4_instructor_comment=c4_instructor_comment, c4_student_comment=c4_student_comment,
                            c5_rating=c5_rating, c5_instructor_comment=c5_instructor_comment, c5_student_comment=c5_student_comment,
                            c6_rating=c6_rating, c6_instructor_comment=c6_instructor_comment, c6_student_comment=c6_student_comment,
                            c7_rating=c7_rating, c7_instructor_comment=c7_instructor_comment, c7_student_comment=c7_student_comment,
                            c8_rating=c8_rating, c8_instructor_comment=c8_instructor_comment, c8_student_comment=c8_student_comment,
                            c9_rating=c9_rating, c9_instructor_comment=c9_instructor_comment, c9_student_comment=c9_student_comment,
                            c10_rating=c10_rating, c10_instructor_comment=c10_instructor_comment, c10_student_comment=c10_student_comment,
                            c11_rating=c11_rating, c11_instructor_comment=c11_instructor_comment, c11_student_comment=c11_student_comment,
                            c12_rating=c12_rating, c12_instructor_comment=c12_instructor_comment, c12_student_comment=c12_student_comment,
                            c13_rating=c13_rating, c13_instructor_comment=c13_instructor_comment, c13_student_comment=c13_student_comment,
                            student_id=student_id, student_name=student_name, course_instructor=course_instructor, course=course, semester=semester, date=date, client=client, disorder=disorder)


        d1_rating = request.form.get("d1_rating")
        d2_rating = request.form.get("d2_rating")
        d3_rating = request.form.get("d3_rating")

        d1_instructor_comment = request.form.get("d1_instructor_comment")
        d2_instructor_comment = request.form.get("d2_instructor_comment")
        d3_instructor_comment = request.form.get("d3_instructor_comment")
        
        d1_student_comment = request.form.get("d1_student_comment")
        d2_student_comment = request.form.get("d2_student_comment")
        d3_student_comment = request.form.get("d3_student_comment")

        # save section D data in section_d object
        assessment_d = section_d(
                            d1_rating=d1_rating, d1_instructor_comment=d1_instructor_comment, d1_student_comment=d1_student_comment,
                            d2_rating=d2_rating, d2_instructor_comment=d2_instructor_comment, d2_student_comment=d2_student_comment,
                            d3_rating=d3_rating, d3_instructor_comment=d3_instructor_comment, d3_student_comment=d3_student_comment,
                            student_id=student_id, student_name=student_name, course_instructor=course_instructor, course=course, semester=semester, date=date, client=client, disorder=disorder)



        e1_rating = request.form.get("e1_rating")
        e2_rating = request.form.get("e2_rating")
        
        e1_instructor_comment = request.form.get("e1_instructor_comment")
        e2_instructor_comment = request.form.get("e2_instructor_comment")
        
        e1_student_comment = request.form.get("e1_student_comment")
        e2_student_comment = request.form.get("e2_student_comment")

        # save section E data in section_e object
        assessment_e = section_e(
                            e1_rating=e1_rating, e1_instructor_comment=e1_instructor_comment, e1_student_comment=e1_student_comment,
                            e2_rating=e2_rating, e2_instructor_comment=e2_instructor_comment, e2_student_comment=e2_student_comment,
                            student_id=student_id, student_name=student_name, course_instructor=course_instructor, course=course, semester=semester, date=date, client=client, disorder=disorder)




        # If this is a not a new assessment - save any changes made to existing assessment
        if is_new == 0:
            print('MODIFICATION FOR ASSESSMENT: ', file=sys.stderr)
            print(assessment_id,file=sys.stderr)

            current_assessment_a = section_a.query.filter_by(session_id=assessment_id).first()
            current_assessment_b = section_b.query.filter_by(session_id=assessment_id).first()
            current_assessment_c = section_c.query.filter_by(session_id=assessment_id).first()
            current_assessment_d = section_d.query.filter_by(session_id=assessment_id).first()
            current_assessment_e = section_e.query.filter_by(session_id=assessment_id).first()
                
            current_assessment_a.a1_rating=a1_rating
            current_assessment_a.a2_rating=a2_rating
            current_assessment_a.a3_rating=a3_rating
            current_assessment_a.a4_rating=a4_rating
            current_assessment_a.a5_rating=a5_rating

            current_assessment_a.a1_instructor_comment = a1_instructor_comment
            current_assessment_a.a2_instructor_comment = a2_instructor_comment
            current_assessment_a.a3_instructor_comment = a3_instructor_comment
            current_assessment_a.a4_instructor_comment = a4_instructor_comment
            current_assessment_a.a5_instructor_comment = a5_instructor_comment
            
            current_assessment_a.a1_student_comment = a1_student_comment
            current_assessment_a.a2_student_comment = a2_student_comment
            current_assessment_a.a3_student_comment = a3_student_comment
            current_assessment_a.a4_student_comment = a4_student_comment
            current_assessment_a.a5_student_comment = a5_student_comment
            
            current_assessment_b.b1_rating=b1_rating
            current_assessment_b.b2_rating=b2_rating
            current_assessment_b.b3_rating=b3_rating
            current_assessment_b.b4_rating=b4_rating

            current_assessment_b.b1_instructor_comment = b1_instructor_comment
            current_assessment_b.b2_instructor_comment = b2_instructor_comment
            current_assessment_b.b3_instructor_comment = b3_instructor_comment
            current_assessment_b.b4_instructor_comment = b4_instructor_comment
                       
            current_assessment_b.b1_student_comment = b1_student_comment
            current_assessment_b.b2_student_comment = b2_student_comment
            current_assessment_b.b3_student_comment = b3_student_comment
            current_assessment_b.b4_student_comment = b4_student_comment
            
            current_assessment_c.c1_rating=c1_rating
            current_assessment_c.c2_rating=c2_rating
            current_assessment_c.c3_rating=c3_rating
            current_assessment_c.c4_rating=c4_rating
            current_assessment_c.c5_rating=c5_rating
            current_assessment_c.c6_rating=c6_rating
            current_assessment_c.c7_rating=c7_rating
            current_assessment_c.c8_rating=c8_rating
            current_assessment_c.c9_rating=c9_rating
            current_assessment_c.c10_rating=c10_rating
            current_assessment_c.c11_rating=c11_rating
            current_assessment_c.c12_rating=c12_rating
            current_assessment_c.c13_rating=c13_rating

            current_assessment_c.c1_instructor_comment = c1_instructor_comment
            current_assessment_c.c2_instructor_comment = c2_instructor_comment
            current_assessment_c.c3_instructor_comment = c3_instructor_comment
            current_assessment_c.c4_instructor_comment = c4_instructor_comment
            current_assessment_c.c5_instructor_comment = c5_instructor_comment
            current_assessment_c.c6_instructor_comment = c6_instructor_comment
            current_assessment_c.c7_instructor_comment = c7_instructor_comment
            current_assessment_c.c8_instructor_comment = c8_instructor_comment
            current_assessment_c.c9_instructor_comment = c9_instructor_comment
            current_assessment_c.c10_instructor_comment = c10_instructor_comment
            current_assessment_c.c11_instructor_comment = c11_instructor_comment
            current_assessment_c.c12_instructor_comment = c12_instructor_comment
            current_assessment_c.c13_instructor_comment = c13_instructor_comment

            current_assessment_c.c1_student_comment = c1_student_comment
            current_assessment_c.c2_student_comment = c2_student_comment
            current_assessment_c.c3_student_comment = c3_student_comment
            current_assessment_c.c4_student_comment = c4_student_comment
            current_assessment_c.c5_student_comment = c5_student_comment
            current_assessment_c.c6_student_comment = c6_student_comment
            current_assessment_c.c7_student_comment = c7_student_comment
            current_assessment_c.c8_student_comment = c8_student_comment
            current_assessment_c.c9_student_comment = c9_student_comment
            current_assessment_c.c10_student_comment = c10_student_comment
            current_assessment_c.c11_student_comment = c11_student_comment
            current_assessment_c.c12_student_comment = c12_student_comment
            current_assessment_c.c13_student_comment = c13_student_comment

            current_assessment_d.d1_rating=d1_rating
            current_assessment_d.d2_rating=d2_rating
            current_assessment_d.d3_rating=d3_rating
            
            current_assessment_d.d1_instructor_comment = d1_instructor_comment
            current_assessment_d.d2_instructor_comment = d2_instructor_comment
            current_assessment_d.d3_instructor_comment = d3_instructor_comment
            
            current_assessment_d.d1_student_comment = d1_student_comment
            current_assessment_d.d2_student_comment = d2_student_comment
            current_assessment_d.d3_student_comment = d3_student_comment

            current_assessment_e.e1_rating = e1_rating
            current_assessment_e.e2_rating = e2_rating
                        
            current_assessment_e.e1_instructor_comment = e1_instructor_comment
            current_assessment_e.e2_instructor_comment = e2_instructor_comment
                        
            current_assessment_e.e1_student_comment = e1_student_comment            
            current_assessment_e.e2_student_comment = e2_student_comment            
                
            db.session.commit()

        # Modify and existing assessment    
        else:
            # add new records to session - will be commited to DB below
            db.session.add(assessment_a)
            db.session.add(assessment_b)
            db.session.add(assessment_c)
            db.session.add(assessment_d)
            db.session.add(assessment_e)
            db.session.add(assessment_e)
            db.session.flush()
            
            #############################################################
            # THIS NEEDS TO BE CHANGED
            # IT WORKS BUT IT IS NOT IDEAL
            # WHEN AN EXISTING ASSESSMENT IS BEING MODIFIED, 
            # THE ID IS SAVED
            # A NEW RECORD IS CREATED WITH THAT ASSESSMENT ID
            # THE OLD RECORD IS DELETED WITH THAT ASSESSMENT ID
            #
            # THERE HAS TO BE A WAY TO JUST UPDATE THE FIELDS RATHER 
            # THAN CREATE AND DELETE AS IS THE CASE NOW
            #############################################################

            # get the current assessment id of the assessment being modified/saved - get from assessment_a object. All sections share the same data
            id_= assessment_a.id
            print('assessment_id to save', file=sys.stderr)
            print(id_, file=sys.stderr)

            # delete the old record with that assessment id     
            db.session.query(assessments).filter(assessments.session_id == None).filter(assessments.student_id==student_id).delete()
           
            # get the id from the DB and save that as the session_id
            current_assessment_a = assessment_a.query.get(id_)
            current_assessment_a.session_id = id_
            # create the new assessment object
            new_assessments = assessments(session_id=id_,student_id=student_id,student_name=student_name,course=course,course_instructor=course_instructor,semester=semester, date=date,client=client,disorder=disorder)

            # assign the current assessments id as the session id in the other assessment sections
            assessment_b.session_id = id_
            assessment_c.session_id = id_
            assessment_d.session_id = id_
            assessment_e.session_id = id_

            # add the assessment record to the DB
            db.session.add(new_assessments)
            # get the student ID that is beign assessed
            usr = student.query.filter_by(id=student_id).first()
            # store this assessments session id to that student
            usr.session_id = id_
           
            # commit changes to the Database
            db.session.commit()
       
        
    print('saving all sections and redirecting', file=sys.stderr)
    

    return redirect(url_for('dashboard'))



#################################################
#
# delete
# This deletes an assessment 
#
################################################# 
@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if is_admin():
        assessment_id=request.form.get('session_id')
        # delete from Database
        db.session.query(assessments).filter(assessments.session_id==assessment_id).delete()
        print('Deleteing assessment and redirecting', file=sys.stderr)
        print(assessment_id, file=sys.stderr)
       
        
        return redirect(url_for('dashboard'))
    else:
        return render_template("error.html")



#################################################
#
# Helper function to determine if authenticated
# user is an admin.
#################################################
def is_admin():

    if current_user:
        if current_user.role == 'admin':
            return True
        else:
            return False
    else:
        print('User not authenticated.', file=sys.stderr)


#################################################
#
# Helper function to determine if authenticated
# user is an instructor.
#################################################
def is_instructor():
    
    if current_user:
        if current_user.role == 'instructor':
            return True
        else:
            return False
    else:
        print('User not authenticated.', file=sys.stderr)        

#################################################
#
# Helper function to determine if authenticated
# user is an student.
#################################################
def is_student():
    
    if current_user:
        if current_user.role == 'student':
            return True
        else:
            return False
    else:
        print('User not authenticated.', file=sys.stderr)    

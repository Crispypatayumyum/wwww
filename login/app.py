from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)
app.template_folder = 'templates'

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'geeklogin'

mysql = MySQL(app)

def login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'username' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper

@app.route('/')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logout' in session:
        msg = 'You have been logged out successfully!'
        session.pop('logout', None)
        return render_template('login.html', msg=msg, show_popup=True)

    
    

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return redirect(url_for('Home'))  # Redirect to the home page
        else:
            msg = 'Incorrect username / password!'

      
        

    return render_template('login.html', msg=msg)


@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    if 'adlogout' in session:
        msg = 'You have been logged out successfully!'
        session.pop('logout', None)
        return render_template('adminlog.html', msg=msg, show_popup=True)

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admins WHERE username = %s AND password = %s', (username, password,))
        admin = cursor.fetchone()
        if admin:
            session['loggedin'] = True
            session['id'] = admin['id']
            session['username'] = admin['username']
            msg = 'Logged in successfully!'
            return redirect(url_for('admin_list'))  # Redirect to the home page
        else:
            msg = 'Incorrect username / password!'

    return render_template('adminlog.html', msg=msg)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))




@app.route('/register', methods =['GET', 'POST'])	
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route('/Home')
def Home():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    return render_template('Home.html')

@app.route('/admin_list')
def admin_list():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM waitlist ORDER BY id;")
    data = cursor.fetchall()
    return render_template('admin_list.html', waitlist_data=data)




# Courses-----------------------------------------

@app.route('/courses')
def courses():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses ORDER BY name;")
    data = cursor.fetchall()
    return render_template('courses.html', courses=data)


@app.route('/ad_courses')
def ad_courses():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses ORDER BY name;")
    data = cursor.fetchall()
    return render_template('ad_courses.html', courses=data)


@app.route('/ad_course/<int:course_id>')
def ad_course_details(course_id):
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    return render_template('ad_course_details.html', course=course)


@app.route('/search', methods=['GET'])
def search():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    keyword = request.args.get('keyword')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses WHERE name COLLATE utf8_general_ci LIKE %s", ('%' + keyword + '%',))
    courses = cursor.fetchall()
    cursor.execute("SELECT * FROM courses ORDER BY name;")
    all_courses = cursor.fetchall()
    if all_courses is None:
        all_courses = []  # Set all_courses to an empty list if it's None
    return render_template('courses.html', courses=courses, all_courses=all_courses)

@app.route('/ad_search', methods=['GET'])
def ad_search():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    keyword = request.args.get('keyword')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses WHERE name COLLATE utf8_general_ci LIKE %s", ('%' + keyword + '%',))
    courses = cursor.fetchall()
    cursor.execute("SELECT * FROM courses ORDER BY name;")
    all_courses = cursor.fetchall()
    if all_courses is None:
        all_courses = []  # Set all_courses to an empty list if it's None
    return render_template('ad_courses.html', courses=courses, all_courses=all_courses)



@app.route('/course/<int:course_id>')
def course_details(course_id):
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    return render_template('course_details.html', course=course)


@app.route('/learn/<int:course_id>')
def learn(course_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # Perform any necessary actions or database updates here

    finished = True  # Set the finished variable to True

    return render_template('course_details.html', finished=finished)







    # Activities-----------------------------------------

@app.route('/activities')
def activities():
        if 'loggedin' not in session:
            return redirect(url_for('login', show_popup=True))
 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from activities order by name;")
        data = cursor.fetchall()
        return render_template('activities.html', activities=data)


@app.route('/ad_activities')
def ad_activities():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM activities ORDER BY name;")
    data = cursor.fetchall()
    return render_template('ad_activities.html', activities=data)

@app.route('/ad_activities/<int:activities_id>')
def ad_activities_details(activities_id):
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM activities WHERE id = %s", (activities_id,))
    activities = cursor.fetchone()
    return render_template('ad_activities_details.html', activities=activities)

@app.route('/ad_searcha', methods=['GET'])
def ad_searcha():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    keyword = request.args.get('keyword')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM activities WHERE name COLLATE utf8_general_ci LIKE %s", ('%' + keyword + '%',))
    activities = cursor.fetchall()
    cursor.execute("SELECT * FROM activities ORDER BY name;")
    all_activities = cursor.fetchall()
    if all_activities is None:
        all_activities = []  # Set all_activities to an empty list if it's None
    return render_template('ad_activities.html', activities=activities, all_activities=all_activities)

@app.route('/searcha', methods=['GET'])
def searcha():
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    keyword = request.args.get('keyword')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM activities WHERE name COLLATE utf8_general_ci LIKE %s", ('%' + keyword + '%',))
    activities = cursor.fetchall()
    cursor.execute("SELECT * FROM activities ORDER BY name;")
    all_activities = cursor.fetchall()
    if all_activities is None:
        all_activities = []  # Set all_activities to an empty list if it's None
    return render_template('activities.html', activities=activities, all_activities=all_activities)


@app.route('/activities/<int:activities_id>')
def activities_details(activities_id):
    if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM activities WHERE id = %s", (activities_id,))
    activities = cursor.fetchone()
    return render_template('activities_details.html', activities=activities)
	

#upload===================================================================================

@app.route('/add_to_waitlist', methods=['POST'])
def add_to_waitlist():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        overview = request.form['overview']
        source = request.form['source']
        w_type = request.form['type']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO waitlist (name, subject, overview, source, type) VALUES (%s, %s, %s, %s, %s)',
                       (name, subject, overview, source, w_type))
        mysql.connection.commit()
        cursor.close()

        return render_template('Added.html', name=name, subject=subject, overview=overview, source=source, type=w_type)


@app.route('/about')
def about():
      if 'loggedin' not in session:
        return redirect(url_for('login', show_popup=True))
      return render_template('about.html')

if __name__ == '__main__':
    app.run()





   
import json
import mysql.connector
import subprocess
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField

app = Flask(__name__)
app.secret_key = 'ABCC123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class LoginForm(FlaskForm):
    password = PasswordField('Password')
    submit = SubmitField('Log In')

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User()
    user.id = username
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        if password == 'test123':  # Replace with your actual password
            user = User()
            user.id = 'admin'
            login_user(user)
            return redirect(url_for('manage_requests'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def get_video_info(video_url):
    command = ['youtube-dl', '-J', video_url]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        video_info = json.loads(result.stdout)
        full_title = video_info.get('fulltitle', 'N/A')
        channel = video_info.get('uploader', 'N/A')
        return full_title, channel
    except subprocess.CalledProcessError as e:
        print(f'Command failed with error: {e.stderr}')
        return None, None
    except json.JSONDecodeError as e:
        print(f'Failed to decode JSON: {e}')
        return None, None

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="aaron",
        password="Bigdaddy",
        database="filtertube"
    )

def copy_to_history(db_connection, request_id):
    cursor = db_connection.cursor()
    # Copy current row data to req_history table
    cursor.execute(
        """
        INSERT INTO req_history (date, requestor, video_name, status, URL, channel_name, video_title)
        SELECT date, requestor, video_name, status, URL, channel_name, video_title FROM req WHERE id = %s
        """,
        (request_id,)
    )
    cursor.close()
    db_connection.commit()


@app.route('/api/video-request/<username>/<video_id>', methods=['GET'])
def video_request(username, video_id):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    full_title, channel = get_video_info(video_url)  # Fetch video title and channel name

    # If get_video_info failed to get the title or channel, default to 'N/A'
    if full_title is None:
        full_title = 'N/A'
    if channel is None:
        channel = 'N/A'

    db_connection = connect_db()
    cursor = db_connection.cursor()
    insert_query = (
        "INSERT INTO req (date, requestor, video_name, status, URL, channel_name, video_title) "
        "VALUES (NOW(), %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(insert_query, (username, 'Video Title', 'Pending', video_url, channel, full_title))
    db_connection.commit()
    cursor.close()
    db_connection.close()

    video_request = {
        'youtube_url': video_url,
        'username': username,
        'status': 'Pending',
        'video_title': full_title,
        'channel_name': channel
    }
    return jsonify(video_request), 201

@app.route('/parentportal/manage/requests')
@login_required
def manage_requests():
    page = request.args.get('page', 1, type=int)  # Get the page number from the query parameters
    per_page = 20  # Number of history entries per page
    offset = (page - 1) * per_page  # Calculate the offset

    db_connection = connect_db()
    cursor = db_connection.cursor(dictionary=True)
    
    # Query the req table for pending requests
    cursor.execute("SELECT * FROM req")
    requests = cursor.fetchall()
    
    # Query the req_history table for historical requests
    cursor.execute(
        "SELECT date, requestor, URL, video_title, channel_name, status FROM req_history ORDER BY date DESC LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    history_requests = cursor.fetchall()

    
    cursor.close()
    db_connection.close()
    
    # Pass both the pending and historical requests to the template
    return render_template(
        'manage_requests.html',
        requests=requests,
        history_requests=history_requests,
        page=page
    )

@app.route('/api/process-request/<int:request_id>/<action>', methods=['POST'])
def process_request(request_id, action):
    db_connection = connect_db()
    cursor = db_connection.cursor()
    
    if action == 'approve':
        cursor.execute("UPDATE req SET status = 'Approved' WHERE id = %s", (request_id,))
        copy_to_history(db_connection, request_id)  # Copy row to history
        cursor.execute("DELETE FROM req WHERE id = %s", (request_id,))
        db_connection.commit()
        status = 'success'

    elif action == 'deny':
        cursor.execute("UPDATE req SET status = 'Denied' WHERE id = %s", (request_id,))
        copy_to_history(db_connection, request_id)  # Copy row to history
        cursor.execute("DELETE FROM req WHERE id = %s", (request_id,))
        db_connection.commit()
        status = 'success'
    else:
        status = 'failure'
    
    cursor.close()
    db_connection.close()
    return jsonify({'status': status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

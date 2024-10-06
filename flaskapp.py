import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import sqlite3

app = Flask(__name__)

# Set the folder to store uploaded files
UPLOAD_FOLDER = '/home/ubuntu/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# SQLite setup
def connect_db():
    conn = sqlite3.connect('/home/ubuntu/mydatabase.db')
    return conn

@app.route('/')
def index():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    # Handle file upload
    file = request.files['file']
    if file and file.filename.endswith('.txt'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read the file with UTF-8 encoding to avoid UnicodeDecodeError
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            word_count = len(text.split())

        # Store user data and word count in the database
        conn = connect_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, firstname, lastname, email, word_count, file_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email, word_count, file.filename))
        conn.commit()
        conn.close()

        return redirect(url_for('profile', username=username))

    return "Please upload a valid .txt file."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = connect_db()
        c = conn.cursor()

        # Retrieve user info based on username and password
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            # If user exists, redirect to the profile page and display user info
            return render_template('profile.html', user=user)
        else:
            # If no user is found, return an error message
            return "Invalid username or password"

    # Render login form for GET request
    return render_template('login.html')



@app.route('/profile/<username>')
def profile(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

# Route to serve the uploaded file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)


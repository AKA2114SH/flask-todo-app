from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'akash_1'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store profile photos
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit file uploads to 2MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=True)  # New field: User's name
    bio = db.Column(db.String(500), nullable=True)  # New field: User's bio
    profile_photo = db.Column(db.String(200), nullable=True)  # New field: Path to profile photo

# Todo model
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route("/")
@login_required
def home():
    todos = Todo.query.filter_by(user_id=current_user.id, deleted=False).all()
    return render_template("index.html", todos=todos)

# About route
@app.route("/about")
def about():
    return render_template("about.html")

# Add todo route
@app.route("/add", methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title')
    desc = request.form.get('desc')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')

    if not title or not desc:
        flash("Title and Description cannot be empty.", "error")
        return redirect("/")

    todo = Todo(
        title=title,
        desc=desc,
        due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
        priority=priority,
        user_id=current_user.id
    )
    db.session.add(todo)
    db.session.commit()
    flash("Todo added successfully!", "success")
    return redirect("/")

# Update todo route
@app.route("/update/<int:sno>", methods=['GET', 'POST'])
@login_required
def update(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first()
    if not todo:
        flash("Todo not found.", "error")
        return redirect("/")

    if request.method == 'POST':
        # Safely get form data
        todo.title = request.form.get('title')
        todo.desc = request.form.get('desc')
        due_date_str = request.form.get('due_date')
        todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        todo.priority = request.form.get('priority')
        
        # Save changes to the database
        db.session.commit()
        flash("Todo updated successfully!", "success")
        return redirect("/")

    return render_template("update.html", todo=todo)

# Mark as completed route
@app.route("/complete/<int:sno>")
@login_required
def complete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first()
    if not todo:
        flash("Todo not found.", "error")
        return redirect("/")
    todo.completed = True
    db.session.commit()
    flash("Todo marked as completed!", "success")
    return redirect("/")

# Delete todo route
@app.route("/delete/<int:sno>")
@login_required
def delete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first()
    if not todo:
        flash("Todo not found.", "error")
        return redirect("/")
    todo.deleted = True
    db.session.commit()
    flash("Todo moved to recycle bin!", "success")
    return redirect("/")

# Filter todos route
@app.route("/filter", methods=['GET'])
@login_required
def filter_todos():
    priority = request.args.get('priority')
    due_date = request.args.get('due_date')
    query = Todo.query.filter_by(user_id=current_user.id, deleted=False)

    if priority:
        query = query.filter_by(priority=priority)
    if due_date:
        query = query.filter_by(due_date=datetime.strptime(due_date, '%Y-%m-%d'))

    todos = query.all()
    return render_template("index.html", todos=todos)

# Signup route
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect("/signup")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.", "error")
            return redirect("/signup")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect("/signup")

        user = User(email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect("/login")

    return render_template("signup.html")

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect("/login")

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect("/")

    return render_template("login.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect("/login")

# Recycle Bin route
@app.route("/recycle-bin")
@login_required
def recycle_bin():
    deleted_todos = Todo.query.filter_by(user_id=current_user.id, deleted=True).all()
    return render_template("recycle_bin.html", deleted_todos=deleted_todos)

# Restore todo route
@app.route("/restore/<int:sno>")
@login_required
def restore(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first()
    if not todo:
        flash("Todo not found.", "error")
        return redirect("/recycle-bin")
    todo.deleted = False
    db.session.commit()
    flash("Todo restored successfully!", "success")
    return redirect("/recycle-bin")

# Permanently delete todo route
@app.route("/permanent-delete/<int:sno>")
@login_required
def permanent_delete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first()
    if not todo:
        flash("Todo not found.", "error")
        return redirect("/recycle-bin")
    db.session.delete(todo)
    db.session.commit()
    flash("Todo permanently deleted!", "success")
    return redirect("/recycle-bin")

# Search todos route
@app.route("/search", methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    if query:
        search_results = Todo.query.filter(
            (Todo.title.ilike(f'%{query}%')) | (Todo.desc.ilike(f'%{query}%'))
        ).filter_by(user_id=current_user.id, deleted=False).all()
    else:
        search_results = Todo.query.filter_by(user_id=current_user.id, deleted=False).all()
    return render_template("index.html", todos=search_results)

# Profile route
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update name and bio
        current_user.name = request.form.get('name')
        current_user.bio = request.form.get('bio')

        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.profile_photo = filename  # Save the file path in the database
            elif file and not allowed_file(file.filename):
                flash("Invalid file type. Allowed types: png, jpg, jpeg, gif.", "error")
                return redirect("/profile")

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect("/profile")

    return render_template("profile.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=8000)
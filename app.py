from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

# SQLite database connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'akash_1'

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define the Todo model
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete flag

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# Home route - Display and add todos
@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':  # Handle form submission
        # Fetch 'title' and 'desc' from form data
        title = request.form.get('title')
        desc = request.form.get('desc')
        
        # Server-side validation
        if not title or not desc:
            flash("Error: Title and Description cannot be empty. Please fill in both fields.", "error")
            return redirect("/")
        
        # Create a new Todo entry
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
        flash("Todo added successfully!", "success")
    
    # Retrieve all non-deleted todos from the database
    all_todo = Todo.query.filter_by(deleted=False).all()
    return render_template("index.html", allTodo=all_todo)

# Update route - Edit a todo
@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if not todo:
        flash("Error: Todo not found.", "error")
        return redirect("/")
    
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo.title = title
        todo.desc = desc
        db.session.commit()
        flash("Todo updated successfully!", "success")
        return redirect("/")
    
    return render_template("update.html", todo=todo)

# Delete route - Soft delete a todo (move to recycle bin)
@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if not todo:
        flash("Error: Todo not found.", "error")
        return redirect("/")
    
    todo.deleted = True  # Mark as deleted instead of removing from the database
    db.session.commit()
    flash("Todo moved to recycle bin!", "success")
    return redirect("/")

# Search route - Search todos by title or description
@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')  # Get the search query from the URL parameters
    if query:
        # Filter todos where title or description contains the query (case-insensitive)
        search_results = Todo.query.filter(
            (Todo.title.ilike(f'%{query}%')) | (Todo.desc.ilike(f'%{query}%'))
        ).filter_by(deleted=False).all()  # Exclude deleted todos
    else:
        # If no query is provided, show all non-deleted todos
        search_results = Todo.query.filter_by(deleted=False).all()
    
    return render_template("index.html", allTodo=search_results)

# Recycle Bin route - Display deleted todos
@app.route("/recycle-bin")
def recycle_bin():
    # Fetch todos that are marked as deleted
    deleted_todos = Todo.query.filter_by(deleted=True).all()
    return render_template("recycle_bin.html", deleted_todos=deleted_todos)

# Restore route - Restore a deleted todo
@app.route("/restore/<int:sno>")
def restore(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if not todo:
        flash("Error: Todo not found.", "error")
        return redirect("/recycle-bin")
    
    todo.deleted = False  # Mark as not deleted
    db.session.commit()
    flash("Todo restored successfully!", "success")
    return redirect("/recycle-bin")

# Permanent Delete route - Permanently delete a todo from the recycle bin
@app.route("/permanent-delete/<int:sno>")
def permanent_delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if not todo:
        flash("Error: Todo not found.", "error")
        return redirect("/recycle-bin")
    
    db.session.delete(todo)  # Permanently delete the todo
    db.session.commit()
    flash("Todo permanently deleted!", "success")
    return redirect("/recycle-bin")

# Run the Flask application
if __name__ == "__main__":
    # Run the Flask application
    app.run(debug=True, port=8000)
# Flask Todo App

A simple and user-friendly Todo application built with Flask, Python, HTML, Bootstrap, and SQLite. This app allows users to manage their daily tasks efficiently.

## ✨ Features

- Add new tasks with due dates
- Mark tasks as completed
- Edit or delete existing tasks
- Clean and responsive user interface
- Data persistence using SQLite
- User-friendly date picker
- Task priority levels
- Task filtering and sorting

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/AKA2114SH/flask-todo-app.git
cd flask-todo-app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```

Visit `http://localhost:5000` in your browser to use the application.

## 🛠️ Tech Stack

- **Flask**: Python web framework
- **SQLite**: Database for storing tasks
- **Bootstrap**: Frontend styling
- **HTML/CSS**: Frontend structure and design
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-Migrate**: Database migrations

## 📁 Project Structure

```
flask-todo-app/
├── app.py              # Main application file
├── instance/          # SQLite database
├── migrations/        # Database migrations
├── static/           # CSS, JS, and other static files
├── templates/        # HTML templates
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## 💻 Usage

1. **Adding a Task**:
   - Click on "Add Task" button
   - Enter task details and due date
   - Click "Save"

2. **Completing a Task**:
   - Click the checkbox next to the task
   - Task will be marked as completed

3. **Editing a Task**:
   - Click "Edit" button on the task
   - Modify task details
   - Click "Save"

4. **Deleting a Task**:
   - Click "Delete" button on the task
   - Confirm deletion

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Akash Khatale - [@AKA2114SH](https://github.com/AKA2114SH)

Project Link: [https://github.com/AKA2114SH/flask-todo-app](https://github.com/AKA2114SH/flask-todo-app)

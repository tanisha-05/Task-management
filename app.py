from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import bcrypt
import re

# from flask import Flask, render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy     #import db 
# from datetime import datetime, date   
# import bcrypt            
# import re
    
# # from flask import jsonify, request
# # from app import app, db, Todo
# from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///D:/python/todo.db"   #config db
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

#db schema define

#task db
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#return todo object
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

#user db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    todos = db.relationship('Todo', backref='user', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self,password):
         return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
with app.app_context():
     db.create_all()

#register
@app.route('/',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                'register.html',
                error="Email already exists"
            )
        
        #new user create
        new_user = User(
                name=name,
                email=email,
                password=password
            )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    
    return render_template('register.html') 

#login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
          email = request.form['email']
          password = request.form['password']

          user = User.query.filter_by(email=email).first()

          if user and user.check_password(password):
               session['user_id'] = user.id
               session['email'] = user.email
               return redirect('/add')
          
          else:
               return render_template('login.html', error='Invalid user')
    
    return render_template('login.html') 

#dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']

    complete_count = Todo.query.filter_by(status="Complete", user_id=user_id).count()
    pending_task = Todo.query.filter_by(status="Pending", user_id=user_id).count()
    low_priority = Todo.query.filter_by(status="Pending", priority="low", user_id=user_id).count()
    medium_priority = Todo.query.filter_by(status="Pending", priority="medium", user_id=user_id).count()
    high_priority = Todo.query.filter_by(status="Pending", priority="high", user_id=user_id).count()
    total_tasks = Todo.query.filter_by(user_id=user_id).count()

    overdue_count = Todo.query.filter(
    Todo.due_date.isnot(None),
    Todo.due_date < date.today(),
    Todo.status != "Complete",
    Todo.user_id == user_id
).count()
    
    label = ['pending_task', 'overdue_count', 'Complete']
    data = [pending_task,  overdue_count, complete_count]

    label1 = ['low_priority', 'medium_priority', 'high_priority']
    data1 = [low_priority, medium_priority, high_priority]
    return render_template('dashboard.html', label=label, data=data, label1=label1, data1 = data1, total_tasks=total_tasks,
                           pending_tasks=pending_task, completed_tasks=complete_count,
                           overdue_tasks=overdue_count)

#logout
@app.route('/logout')
def logout():
    session.pop('email',None)
    session.clear()
    return redirect('/login')

#add task
@app.route("/add",methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')
    
   
    if request.method=='POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form.get("due_date")
        due_date = date.fromisoformat(due_date_str) if due_date_str else None
        priority = request.form['priority']
        status = request.form['status']
        todo = Todo(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status,
            user_id=session['user_id']
            )
        user_id = session['user_id']
        tasks = Todo.query.filter_by(user_id=user_id).all()
        print("TASKS:", [t.title for t in tasks])
        db.session.add(todo)
        db.session.commit()
        return redirect("/add")
    
    allTodo = Todo.query.filter_by(user_id=session['user_id']).all()
    return render_template("index.html", allTodo=allTodo)

#delete task
@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect("/add")

#update task
@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form.get('due_date')
        due_date = date.fromisoformat(due_date_str) if due_date_str else None
        priority = request.form['priority']
        status = request.form['status']

        if todo:
            todo.title = title
            todo.description = description
            todo.due_date = due_date
            todo.priority = priority
            todo.status = status

            db.session.commit()

        return redirect("/add")

    return render_template("update.html", todo=todo)

#complete task
@app.route("/complete/<int:sno>")
def complete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first()
    if todo:
        todo.status = "Complete"
        db.session.commit()
    return redirect("/add")

#API ENDPOINT
# GET ALL TASKS
@app.route('/api/tasks', methods=['GET'])
def get_tasks():

    tasks = Todo.query.all()

    result = []

    for t in tasks:
        result.append({
            "id": t.sno,
            "title": t.title,
            "description": t.description,
            "due_date": str(t.due_date),
            "priority": t.priority,
            "status": t.status
        })

    return jsonify(result)

# ADD TASK
@app.route('/api/tasks', methods=['POST'])
def add_task_api():

    data = request.json

    try:

        due_date = None

        if data.get("due_date"):
            due_date = date.fromisoformat(data["due_date"])

        new_task = Todo(
            title=data['title'],
            description=data['description'],
            due_date=due_date,
            priority=data['priority'],
            status=data['status']
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "message": "Task created successfully"
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400

# UPDATE TASK
@app.route('/api/tasks/<int:sno>', methods=['PUT'])
def update_task_api(sno):

    task = Todo.query.get(sno)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    data = request.json

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)

    if data.get("due_date"):
        task.due_date = date.fromisoformat(data["due_date"])

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully"
    })

# DELETE TASK
@app.route('/api/tasks/<int:sno>', methods=['DELETE'])
def delete_task_api(sno):

    task = Todo.query.get(sno)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully"
    })

# MARK TASK COMPLETE
@app.route('/api/tasks/<int:sno>/complete', methods=['PATCH'])
def complete_task_api(sno):

    task = Todo.query.get(sno)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404
    
    task.status = "Complete"
    db.session.commit()

    return jsonify({
        "message": "Task marked complete"
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)

from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/todoapp' #Here is the database name
mongo = PyMongo(app)

# Access the collection like this:
# mongo.db.todos


# Add data
@app.route('/', methods=['POST', 'GET'])
def index():
    

    if request.method == 'POST':
        task_content = request.form.get('content')
        new_task = {
            "content": task_content,
            "completed": 0,
            "date_created": datetime.now()
        }

        try:
            mongo.db.todos.insert_one(new_task)
            return redirect(url_for('index'))
        except Exception as e:
            return f'There was an issue adding your task: {e}'
    else:
        todos = list(mongo.db.todos.find())
        return render_template('index.html', tasks=todos)

# Delete data
@app.route('/delete/<task_id>')
def delete_task(task_id):
    try:
        mongo.db.todos.delete_one({"_id": ObjectId(task_id)})
        return redirect(url_for('index'))
    except Exception as e:
        return f'There was a problem deleting that task: {e}'

@app.route('/update/<task_id>', methods=['POST', 'GET'])
def update_task(task_id):
    task = mongo.db.todos.find_one({"_id": ObjectId(task_id)})

    if task is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        task_content = request.form.get('content')
        try:
            mongo.db.todos.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"content": task_content}}
            )
            return redirect(url_for('index'))
        except Exception as e:
            return f'There was an issue updating your task: {e}'
    else:
        return render_template('update.html', task=task, task_id=task_id)


if __name__ == "__main__":
    app.run(debug=True)
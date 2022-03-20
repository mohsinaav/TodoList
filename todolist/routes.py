from datetime import datetime
from todolist import app, db, bcrypt
from flask import render_template, redirect, flash, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from todolist.models import User, List, Task
from todolist.utils import TasksBasedOnDates, ColorPickOptions, save_picture
from todolist.forms import RegistrationForm, LoginForm, TaskForm, ListForm, ListUpdateForm, AccountUpdateForm, SearchTaskForm
from sqlalchemy import func, DATE

colorOptions = []
colorOptions.append(ColorPickOptions('#ffffff', 'White'))
colorOptions.append(ColorPickOptions('#0081a7', 'Blue'))
colorOptions.append(ColorPickOptions('#e63946', 'Red'))
colorOptions.append(ColorPickOptions('#e4c1f9', 'Lavender'))
colorOptions.append(ColorPickOptions('#007200', 'Green'))
colorOptions.append(ColorPickOptions('#ffbf69', 'Yellow'))
colorOptions.append(ColorPickOptions('#01befe', 'Light Blue'))
colorOptions.append(ColorPickOptions('#cb997e', 'Brown'))
colorOptions.append(ColorPickOptions('#9381ff', 'Purple'))
colorOptions.append(ColorPickOptions('#fec89a', 'Beige'))
colorOptions.append(ColorPickOptions('#d9ed92', 'Light green'))
colorOptions.append(ColorPickOptions('#e85d04', 'Orange'))


@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
@login_required
def home_page():
    form = ListForm()
    searchTaskForm = SearchTaskForm()
    form.color.choices = [(color.value, color.id) for color in colorOptions]
    if form.validate_on_submit():
        existing_list = List.query.filter(List.title == form.title.data.lower()).filter(List.user_id == current_user.id).first()
        if existing_list:
            flash(f'{form.title.data} list already exists', category='danger')
        else:
            new_list = List(user_id = current_user.id, title = form.title.data.lower(), description = form.description.data, is_important = form.is_important.data, color = form.color.data)
            db.session.add(new_list)
            db.session.commit()
            flash('New list added!!', category='success')
        return redirect(url_for('home_page'))

    if searchTaskForm.validate_on_submit() and request.method == 'POST':
        searchKeyword = searchTaskForm.searchText.data
        relatedTasks = search_task_by_keywords(searchKeyword)
        return render_template('searchTask.html', relatedTasks = relatedTasks, keyword = searchKeyword)

    openLists = getOpenLists()
    return render_template("home.html", title="Home Page", openLists = openLists, form = form, searchTaskForm = searchTaskForm, colorOptions = colorOptions)


@app.route("/get_list/<int:list_id>", methods=['GET','POST'])
@login_required
def get_list_by_id(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    taskForm = TaskForm()
    listForm = ListUpdateForm()
    listForm.color.choices = [(color.value, color.id) for color in colorOptions]

    if taskForm.validate_on_submit():
        existing_task = Task.query.filter(Task.list_id == list_id).filter(Task.content == taskForm.content.data.capitalize()).first()
        if existing_task:
            flash(f"{taskForm.content.data} already exists!!", category='danger')
        else:
            new_task = Task(list_id = list_id, content = taskForm.content.data.capitalize())
            db.session.add(new_task)
            db.session.commit()
            flash('New task added!!', category='success')
        return redirect(url_for('get_list_by_id', list_id = list_id))
    elif request.method == 'GET':
        listForm.title.data = required_list.title
        listForm.description.data = required_list.description
        listForm.is_important.data = required_list.is_important
        listForm.color.data = required_list.color

    openTasks = getOpenTasks(list_id)
    completedTasksLists = getCompletedTasks(list_id)
    print(len(completedTasksLists))
    return render_template('list.html', title="List Page", required_list = required_list, openTasks = openTasks, completedTasksLists = completedTasksLists, taskForm=taskForm ,listForm = listForm, colorOptions = colorOptions)


@app.route("/updateList/<int:list_id>", methods=['GET','POST'])
@login_required
def update_list(list_id):
    listForm = ListUpdateForm()
    listForm.color.choices = [(color.value, color.id) for color in colorOptions]
    required_list = List.query.get_or_404(list_id)
    if listForm.validate_on_submit():
        print("inside update method")
        required_list.title = listForm.title.data
        required_list.description = listForm.description.data
        required_list.is_important = listForm.is_important.data
        required_list.color = listForm.color.data
        db.session.commit()
        flash("List details are successfully updated!!.", category = 'success')

    return redirect(url_for('home_page'))


@app.route("/changeStatusToComplete/<int:task_id>")
@login_required
def change_TaskStatus_ToComplete(task_id):
    task = Task.query.filter_by(id = task_id).first()
    if task and task.collection.owner.id == current_user.id:
        task.is_completed = 1
        task.completed_on = datetime.utcnow()
        task.modified_on = datetime.utcnow()
        db.session.commit()
    else:
        flash(f'No such task exists!')
    return redirect(url_for('get_list_by_id', list_id = task.list_id))


@app.route("/changeStatusToNotComplete/<int:completedTask_id>")
@login_required
def change_TaskStatus_ToNotComplete(completedTask_id):
    task = Task.query.filter_by(id = completedTask_id).first()
    if task and task.collection.owner.id == current_user.id:
        task.is_completed = 0
        task.completed_on = None
        task.modified_on = datetime.utcnow()
        db.session.commit()
    else:
        flash(f'No such task exists!')
    return redirect(url_for('get_list_by_id', list_id = task.list_id))


@app.route("/markAllTasksComplete/<int:list_id>")
@login_required
def mark_all_tasks_complete(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    for task in required_list.tasks:
        task.is_completed = 1
        task.completed_on = datetime.utcnow()
        task.modified_on = datetime.utcnow()
    db.session.commit()
    flash(f"All tasks in list \"{required_list.title}\" are now marked as complete!!", category="success")
    return redirect(url_for('get_list_by_id', list_id = list_id))

@app.route("/markAllTasksNotComplete/<int:list_id>")
@login_required
def mark_all_tasks_incomplete(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    for task in required_list.tasks:
        task.is_completed = 0
        task.completed_on = None
        task.modified_on = datetime.utcnow()
    db.session.commit()
    flash(f"All tasks in list \"{required_list.title}\" are now marked as incomplete!!", category="success")
    return redirect(url_for('get_list_by_id', list_id = list_id))


@app.route("/archiveList/<int:list_id>")
@login_required
def archive_list(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    required_list.is_archived = 1
    db.session.commit()
    flash(f"List {required_list.title} is now archived !!", category = 'success')
    return redirect(url_for('home_page'))


@app.route("/unarchiveList/<int:list_id>")
@login_required
def un_archive_list(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    required_list.is_archived = 0
    db.session.commit()
    flash(f"List {required_list.title} is now unarchived !!", category = 'success')
    return redirect(url_for('archive_page'))


@app.route("/markImportant/<int:list_id>")
@login_required
def mark_important(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    old_value = required_list.is_important
    required_list.is_important = 1 if old_value == 0 else 0
    db.session.commit()
    flash(f"List {required_list.title} marked as important !!", category = 'success')
    return redirect(url_for('home_page'))


@app.route("/deleteList/<int:list_id>")
@login_required
def delete_list(list_id):
    required_list = List.query.get_or_404(list_id)
    if required_list.owner != current_user:
        abort(403)
    
    db.session.delete(required_list)
    db.session.commit()
    flash("List deleted !!", category = 'success')
    return redirect(url_for('home_page'))


@app.route("/deleteTask/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    list_id = task.list_id
    if task and task.collection.owner.id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash(f'Task deleted !!', category='success')
    else:
        abort(403)
        flash(f'No such task exists!', category='danger')
    return redirect(url_for('get_list_by_id', list_id = list_id))
    

@app.route("/about", methods=['GET','POST'])
def about_page():
    searchTaskForm = SearchTaskForm()
    return render_template('about.html', title='About Page', searchTaskForm = searchTaskForm)


@login_required
@app.route("/archive", methods=['GET','POST'])
def archive_page():
    if current_user.is_authenticated:
        archived_list = getArchivedLists()
    else:
        return redirect(url_for('login_page'))
    return render_template('archive.html', title='Archive Page', archived_list=archived_list)


@app.route("/account", methods=['GET','POST'])
def account_page():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        current_user.name = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f"Your account information has been updated!!", category = 'success')
        return redirect(url_for('account_page'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title="Account Page", form = form, image_file = image_file)


@app.route("/register", methods=['GET','POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', category='success')
        return redirect(url_for('login_page'))
    return render_template('register.html', title = 'Registor', form = form)


@app.route("/login", methods=['GET','POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        # If user exists, check if password matches
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login the user
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            print("next page is ", next_page)
            return redirect(next_page) if next_page else redirect(url_for('home_page')) 
        else:
            flash('Login Unsuccessful!! Please check email and password.', category='danger')
    return render_template('login.html', title="Login", form = form)


@app.route("/logout")
def logout_page():
    logout_user()
    return redirect(url_for('about_page'))

# private method starts here
# Function to retrieve open lists of the user, ordered in terms of dates
def getOpenLists():
    imp_lists = List.query.filter_by(user_id=current_user.id).filter_by(is_archived=0).filter_by(is_important=1).all()
    unImp_lists = List.query.filter_by(user_id=current_user.id).filter_by(is_archived=0).filter_by(is_important=0).all()
    lists = imp_lists + unImp_lists
    return lists


def getArchivedLists():
    imp_archivedLists = List.query.filter_by(user_id=current_user.id).filter_by(is_archived=1).filter_by(is_important=1).all()
    unImp_archivedLists = List.query.filter_by(user_id=current_user.id).filter_by(is_archived=1).filter_by(is_important=0).all()
    lists = imp_archivedLists + unImp_archivedLists
    return lists


# Function to retrieve in complete tasks of the user, grouped in terms of dates
def getOpenTasks(list_id):
    tasks = Task.query.filter_by(list_id=list_id).filter_by(is_completed=0).order_by(Task.created_on).all()
    return tasks
    

# Function to retrieve all completed tasks of the user, in order of date of completion.
def getCompletedTasks(list_id):
    # get lists of tasks completed by the user in ascending order
    # get all distinct dates available, based on user and status
    # dates = db.session.query(func.DATE(Task.completed_on)).filter(Task.list_id==list_id).filter(Task.is_completed==1).distinct().all()

    dates = db.session.query(func.strftime('%d-%m-%Y', Task.completed_on)).filter(Task.list_id==list_id).filter(Task.is_completed==1).distinct().all()
    # create objects of class TasksBasedOnDates
    taskLists = []
    for date in dates:
        tasks = Task.query.filter(func.strftime('%d-%m-%Y', Task.completed_on) == date[0]).filter(Task.list_id == list_id).filter(Task.is_completed == 1).all()
        taskLists.append(TasksBasedOnDates(date[0], tasks))

    return taskLists


def search_task_by_keywords(keyword):
    required_list_ids = db.session.query(List.id).filter(List.user_id == current_user.id).all()
    required_ids = []
    for list_id in required_list_ids:
        required_ids.append(list_id[0])
    tasks = Task.query.filter(Task.list_id.in_(required_ids)).filter(Task.content.contains(keyword)).all()
    return tasks

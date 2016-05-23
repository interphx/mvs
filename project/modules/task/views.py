import datetime
from flask import render_template, abort
from project.frontend import frontend
from project.util import rights_required

from .model import Task
from project.modules.category import Category
from project.modules.task_comment import TaskComment
from project.modules.task_offer import TaskOffer

@frontend.route('tasks/', methods=['GET'])
@frontend.route('tasks/<category_name>/', methods=['GET'])
def task_list(category_name=None):
    # TODO: subcats
    if (category_name == None):
        category_name = 'all'

    category = Category.query.filter_by(url_name = category_name).one()
    now = datetime.datetime.utcnow()

    # TODO: add pagination
    if (category_name == 'all'):
        tasks_query = Task.query.order_by(Task.created_at.desc())
    else:
        tasks_query = category.tasks_query.order_by(Task.created_at.desc())
    
    tasks = tasks_query.filter_by(status=Task.Status.created).filter(Task.due > now).all()

    return render_template('task/list.html', **{
        'tasks': tasks,
        'selected_category': category,
        'categories': Category.query.all()
    })

@frontend.route('tasks/<int:id>/', methods=['GET'])
def task(id):
    task = Task.query.get(id)
    if (task == None):
        return abort(404)
    return render_template('task/view.html', **{
        'task': task,
        'categories': Category.query.all(),
        'comments': task.comments.order_by(TaskComment.created_at.asc()),
        'offers': task.offers.order_by(TaskOffer.created_at.desc())
    })

@frontend.route('task/new/', methods=['GET'])
@rights_required('user')
def task_new():
    return render_template('task/new.html', **{
        'categories': Category.query.filter(Category.parent.has(url_name='all')).all()
    })

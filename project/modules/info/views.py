from sqlalchemy import func

from urllib.parse import unquote
from flask import render_template, abort, redirect, url_for
from project.frontend import frontend

from project.database import db
from project.util import rights_required

from .model import InfoPage
from .forms import InfoPageForm


@frontend.route('info/', methods=['GET'])
def info():
    return render_template('info/info.html', **{
        'pages': InfoPage.query.order_by(InfoPage.sort_order).all()
    })

@frontend.route('info/<url_name>/', methods=['GET'])
def info_page(url_name):
    url_name = url_name.lower()
    page = InfoPage.query.filter(func.lower(InfoPage.url_name) == func.lower(url_name)).first()
    # url_for повторно заменяет символы % и всё портит
    if page == None:
        page = InfoPage.query.filter(func.lower(InfoPage.url_name) == func.lower(unquote(url_name))).first()
    
    if page == None:
        other = [page.url_name for page in InfoPage.query.all()]
        raise Exception("Page is none, url_name is " + str(url_name) + " others are " + str(other))
    
    return render_template('info/view.html', **{
        'page': page
    })

@rights_required('admin')
@frontend.route('admin/info_new/', methods=['GET', 'POST'])
def new_info_page():
    
    form = InfoPageForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        page = InfoPage(title=title, text=text)
        try:
            db.session.add(page)
            db.session.commit()
            return redirect(url_for('frontend.info_page', url_name=page.url_name))
        except Exception as e:
            db.session.rollback()
            form.title.errors.append(str(e))
            #raise e
    
    return render_template('info/new.html', **{
        'infoPageForm': form
    })

@rights_required('admin')
@frontend.route('admin/info_edit/<int:id>/', methods=['GET', 'POST'])
def edit_info_page(id):
    page = InfoPage.query.get(id)
    if not page:
        abort(404)
    
    form = InfoPageForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        try:
            page.title = title
            page.text = text
            db.session.commit()
            return redirect(url_for('frontend.info_page', url_name=page.url_name))
        except Exception as e:
            db.session.rollback()
            form.title.errors.append(str(e))
            raise e
    
    return render_template('info/edit.html', **{
        'infoPageForm': form,
        'page': page
    })
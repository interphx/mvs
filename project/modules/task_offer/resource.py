import dateutil.parser
from flask import url_for, redirect, render_template
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required, get_commission

from project.modules.user.helpers import notify_user
from project.modules.task.model import Task

from .schema import TaskOfferSchema

from .model import TaskOffer

class TaskOfferConfirmationAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('offer_id', required=True, location=locs, type=int)
        
        args = parser.parse_args()

        offer = TaskOffer.query.get(args['offer_id'])

        if not offer:
            abort(400, message='No task offer with id {}'.format(args['offer_id']))

        if current_user.id != offer.task.customer.id:
            abort(403, message='You cannot accepts offers for others\' tasks')

        task = offer.task
        customer = task.customer
        doer = offer.doer

        task.doer = doer
        task.status = Task.Status.assigned
        
        # Возвращаем снятые залоги всем, кроме выбранного исполнителя и удаляем предложения
        for offer in task.offers:
            if offer.doer.id == doer.id: continue
            offer.doer.balance += get_commission(task.reward or offer.price)
        task.offers.delete()

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        # TODO: SMS
        notify_user(customer, {
            'email': render_template('letters/you_accepted_offer.html', **{
                    'task': task,
                    'doer': doer,
                    'customer': customer
                })
        },
        subject='Вы выбрали исполнителя')

        notify_user(doer, {
            'email': render_template('letters/your_offer_was_accepted.html', **{
                    'task': task,
                    'doer': doer,
                    'customer': customer
                })
        },
        subject='Вас выбрали исполнителем')

        return {}, 200

class TaskOfferAPI(Resource):

    def get(self, id):
        entity = TaskOffer.query.get(id)
        if not entity:
            abort(404, message='No task offer with id {}'.format(id))
        return TaskOfferSchema().dump(entity).data

    def delete(self, id):
        entity = TaskOffer.query.get(id)
        if not entity:
            abort(404, message='No task offer with id {}'.format(id))
        try:
            db.session.delete(entity)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return {}, 204

class TaskOfferListAPI(Resource):

    @api_login_required
    def post(self):

        if not current_user.doer:
            abort(403, message='You must be a doer to create task execution offers')
       
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        parser.add_argument('price', required=False, location=locs, type=int)
        
        args = parser.parse_args()

        #print('YARRRRRRR!')
        #print(args)
        
        task = Task.query.get(args['task_id'])
        
        if not task:
            abort(403, message='No task with id ' + str(args['task_id']))

        if task.reward == None and args['price'] == None:
            abort(400, message='You must specify a price if reward is not specified for task')
        
        # TODO: Более аккуратный подсчёт залога

        current_user.balance -= get_commission(task.reward or int(args['price']))
        offer = TaskOffer(doer_id=current_user.id, **args)
        try:
            db.session.add(offer)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.task_offer', id=offer.id, _external=True), code=303)
    
    @api_login_required
    def get(self):
       # TODO
       pass
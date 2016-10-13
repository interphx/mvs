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

from .schema import TaskPersonalOfferSchema

from .model import TaskPersonalOffer

class TaskPersonalOfferConfirmationAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('offer_id', required=True, location=locs, type=int)
        parser.add_argument('price', required=False, location=locs, type=int)
        
        args = parser.parse_args()

        offer = TaskPersonalOffer.query.get(args['offer_id'])

        if not offer:
            abort(400, message='No task offer with id {}'.format(args['offer_id']))

        if current_user.id != offer.receiver.id:
            abort(403, message='You can only accept your personal offers')

        if offer.task.reward == None and args['price'] == None:
            abort(400, message='You must specify a price if reward is not specified for task')

        task = offer.task
        sender = offer.sender
        receiver = offer.receiver

        task.doer = offer.receiver
        task.status = Task.Status.assigned
        
        # TODO: Move task delegation in a helper
        commission = get_commission(task.reward or int(args['price']))
        if receiver.balance < commission:
            receiver.balance -= commission
        else:
            abort(400, message='У вас недостаточно средств для залога!')
        
        db.session.delete(offer)
        
        # TODO: Перенести в общий хелпер
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
        notify_user(sender, {
            'email': render_template('letters/your_personal_offer_accepted.html', **{
                    'task': task,
                    'doer': receiver,
                    'customer': sender
                })
        },
        subject=receiver.full_name + ' принял ваше предложение')

        notify_user(receiver, {
            'email': render_template('letters/you_accepted_personal_offer.html', **{
                    'task': task,
                    'doer': receiver,
                    'customer': sender
                })
        },
        subject='Вы приняли предложение')

        return {}, 200

class TaskPersonalOfferAPI(Resource):

    def get(self, id):
        entity = TaskPersonalOffer.query.get(id)
        if not entity:
            abort(404, message='No personal task offer with id {}'.format(id))
        return TaskPersonalOfferSchema().dump(entity).data

    def delete(self, id):
        entity = TaskPersonalOffer.query.get(id)
        if not entity:
            abort(404, message='No personal task offer with id {}'.format(id))
        try:
            db.session.delete(entity)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return {}, 204

class TaskPersonalOfferListAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        parser.add_argument('receiver_id', required=True, location=locs)
        
        args = parser.parse_args()

        #print('YARRRRRRR!')
        #print(args)
        
        task = Task.query.get(args['task_id'])
        
        if not task:
            abort(403, message='No task with id ' + str(args['task_id']))
        
        # TODO: Более аккуратный подсчёт залога

        offer = TaskPersonalOffer(sender_id=current_user.id, **args)
        try:
            db.session.add(offer)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.task_personal_offer', id=offer.id, _external=True), code=303)
    
    @api_login_required
    def get(self):
       # TODO
       pass
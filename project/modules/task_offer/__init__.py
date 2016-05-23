from project.rest import rest

from .model import TaskOffer
from .resource import TaskOfferAPI, TaskOfferListAPI, TaskOfferConfirmationAPI
from .schema import TaskOfferSchema

rest.add_resource(TaskOfferAPI, '/task_offers/<int:id>/', endpoint='api.task_offer')
rest.add_resource(TaskOfferListAPI, '/task_offers/', endpoint='api.task_offers')
rest.add_resource(TaskOfferConfirmationAPI, '/task_offer_confirmations/', endpoint='api.task_offer_confirmations')

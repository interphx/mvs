from project.rest import rest

from .model import TaskPersonalOffer
from .resource import TaskPersonalOfferAPI, TaskPersonalOfferListAPI, TaskPersonalOfferConfirmationAPI
from .schema import TaskPersonalOfferSchema

rest.add_resource(TaskPersonalOfferAPI, '/task_personal_offers/<int:id>/', endpoint='api.task_personal_offer')
rest.add_resource(TaskPersonalOfferListAPI, '/task_personal_offers/', endpoint='api.task_personal_offers')
rest.add_resource(TaskPersonalOfferConfirmationAPI, '/task_personal_offer_confirmations/', endpoint='api.task_personal_offer_confirmations')
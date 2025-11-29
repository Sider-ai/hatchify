from app.business.models.messages import MessageTable
from app.business.repositories.message_repository import MessageRepository
from app.business.services.base.generic_service import GenericService


class MessageService(GenericService[MessageTable]):

    def __init__(self):
        super().__init__(MessageTable, MessageRepository)

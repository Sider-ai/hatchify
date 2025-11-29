from app.business.models.messages import MessageTable
from app.business.repositories.base.generic_repository import GenericRepository


class MessageRepository(GenericRepository[MessageTable]):

    def __init__(self):
        super().__init__(MessageTable)

from app.business.models.session import SessionTable
from app.business.repositories.session_repository import SessionRepository
from app.business.services.base.generic_service import GenericService


class SessionService(GenericService[SessionTable]):

    def __init__(self):
        super().__init__(SessionTable, SessionRepository)

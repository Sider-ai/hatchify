from typing import Type, Dict, Any


class RepositoryManager:
    _instances: Dict[Type, Any] = {}

    @classmethod
    def get_repository(cls, repo_class: Type) -> Any:
        if repo_class not in cls._instances:
            cls._instances[repo_class] = repo_class()
        return cls._instances[repo_class]

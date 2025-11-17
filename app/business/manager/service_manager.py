from typing import Type, Dict, Any


class ServiceManager:
    _instances: Dict[Type, Any] = {}

    @classmethod
    def get_service(cls, service_class: Type) -> Any:
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()
        return cls._instances[service_class]

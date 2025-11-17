import os


class Constants:
    class Path:
        ROOT_PATH: str = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        APP_PATH: str = os.path.join(ROOT_PATH, "app")
        LOGS_PATH: str = os.path.join(ROOT_PATH, "logs")
        RESOURCES_PATH: str = os.path.join(ROOT_PATH, "resources")
        ENV_PATH: str = os.path.join(RESOURCES_PATH, ".env")
        YAML_FILE_PATH: str = os.path.join(
            RESOURCES_PATH, f"{os.environ.get('APP_ENV', 'development')}.yaml"
        )


if __name__ == '__main__':
    print(Constants.Path.YAML_FILE_PATH)
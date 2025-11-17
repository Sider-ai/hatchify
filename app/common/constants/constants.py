import os


class Constants:
    class Path:
        ROOT_PATH: str = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        APP_PATH: str = os.path.join(ROOT_PATH, "app")
        RESOURCES_PATH: str = os.path.join(ROOT_PATH, "resources")
        MODELS_TOML: str = os.path.join(RESOURCES_PATH, "models.toml")
        ENV_PATH: str = os.path.join(RESOURCES_PATH, ".env")
        YAML_FILE_PATH: str = os.path.join(
            RESOURCES_PATH, f"{os.environ.get('ENVIRONMENT', 'development')}.yaml"
        )


if __name__ == '__main__':
    print(Constants.Path.YAML_FILE_PATH)
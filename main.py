import asyncio

import uvicorn

from app.common.constants.constants import Constants

if __name__ == "__main__":
    config = uvicorn.Config(
        "app.launch.launch:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        env_file=Constants.Path.ENV_PATH
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())

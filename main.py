import asyncio

import uvicorn

from hatchify.common.constants.constants import Constants
from hatchify.common.settings.settings import get_hatchify_settings

settings = get_hatchify_settings()
if __name__ == "__main__":
    config = uvicorn.Config(
        "hatchify.launch.launch:app",
        host=settings.server.host,
        port=settings.server.port,
        loop="asyncio",
        env_file=Constants.Path.EnvPath
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())

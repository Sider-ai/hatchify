from typing import Optional

from pydantic import Field

from hatchify.common.domain.enums.execution_status import ExecutionStatus
from hatchify.common.domain.enums.execution_type import ExecutionType
from hatchify.common.domain.requests.base import BasePageRequest


class PageExecutionRequest(BasePageRequest):
    ...
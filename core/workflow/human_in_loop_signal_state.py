from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from temporalio import workflow


@dataclass
class HumanInLoopSignalState:
    """Holds a HumanInLoop result and provides an awaitable wait helper."""
    result: Optional[str] = None

    async def wait(self) -> None:
        """Waits until an approval result is set."""
        await workflow.wait_condition(lambda: self.result is not None)

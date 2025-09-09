import asyncio
import logging
from workflow import DSLWorkflow
from core.dsl import task_registry
from core.workflow.make_activity import make_activity

from core.worker import TemporalWorker


logger = logging.getLogger("dsl_worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
activities = [
    make_activity(task_type, handler_cls)
    for task_type, handler_cls in task_registry.task_registry.items()
]


async def main():
    """
    Entrypoint for running the DSL Temporal Worker
    with enterprise-grade features (health, observability, config).
    """
    worker = TemporalWorker(
        workflows=[DSLWorkflow],
        activities=activities,
    )

    logger.info("🚀 DSL Worker starting with %s activities", len(activities))

    try:
        await worker.start()
    except Exception as e:
        logger.exception("Worker crashed: %s", e)
        await worker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

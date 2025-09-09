import asyncio
import random
import json
import sys
from temporalio.client import Client


async def main():
    """
    Load DSL from a JSON file provided as a command-line argument,
    override inputValues with CLI arguments, and start the Temporal workflow.
    """
    if len(sys.argv) < 2:
        print("Usage: python run_dsl.py <dsl_file.json> key1=value1 key2=value2 ...")
        sys.exit(1)

    dsl_file = sys.argv[1]
    overrides = {}

    # Parse key=value pairs from command-line args
    for arg in sys.argv[2:]:
        if "=" not in arg:
            print(f"Invalid argument format: {arg}. Expected key=value.")
            sys.exit(1)
        key, value = arg.split("=", 1)
        # Try to parse numbers properly
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        overrides[key] = value

    # Load DSL definition from the provided JSON file
    with open(dsl_file, "r") as f:
        dsl = json.load(f)

    # Override inputValues
    if "inputValues" not in dsl:
        dsl["inputValues"] = {}
    dsl["inputValues"].update(overrides)

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Start a workflow with DSL
    result = await client.start_workflow(
        "DSLWorkflow",
        dsl,
        id=f"workflow-{random.randint(1000, 9999)}",
        task_queue="dsl-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

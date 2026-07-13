import asyncio
import os
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agents.mcp import MCPServerStdio


class TaskItem(BaseModel):
    id: str
    description: str
    input_data: dict
    status: str = "pending"
    result: str = ""
    error: str = ""
    attempts: int = 0


class TaskState(BaseModel):
    goal: str = ""
    queue: list[TaskItem] = Field(default_factory=list)
    completed: list[TaskItem] = Field(default_factory=list)
    failed: list[TaskItem] = Field(default_factory=list)
    max_retries: int = 3
    max_iterations: int = 100

    @property
    def progress(self) -> float:
        total = len(self.queue) + len(self.completed) + len(self.failed)
        if total == 0:
            return 0.0
        return len(self.completed) / total

    @property
    def should_continue(self) -> bool:
        return (
            len(self.queue) > 0
            and (len(self.completed) + len(self.failed))
                < self.max_iterations
        )

    def next_item(self) -> TaskItem | None:
        if not self.queue:
            return None
        return self.queue.pop(0)

    def record_success(self, item: TaskItem, result: str):
        item.status = "completed"
        item.result = result
        self.completed.append(item)

    def record_failure(self, item: TaskItem, error: str):
        item.attempts += 1
        item.error = error
        if item.attempts < self.max_retries:
            item.status = "retry"
            self.queue.append(item)
        else:
            item.status = "failed"
            self.failed.append(item)


class TaskResult(BaseModel):
    task_id: str
    success: bool
    output: str
    error: str = ""


task_agent = Agent(
    name="Document Transformer",
    instructions="""
You are a document transformation agent.
Given a task with input data containing a file path
and transformation instructions, read the file,
apply the transformation, and write the result.
Report success or failure for each task.
""",
    model="gpt-4o",
    output_type=TaskResult,
)


async def run_task_loop(
    tasks: list[dict], max_retries: int = 3
) -> TaskState:
    filesystem_server = MCPServerStdio(
        name="Filesystem",
        params={
            "command": "npx",
            "args": [
                "-y",
                "@anthropic/filesystem-mcp",
                os.path.abspath("./workspace"),
            ],
        },
    )
    search_server = MCPServerStdio(
        name="Brave Search",
        params={
            "command": "npx",
            "args": ["-y", "@anthropic/brave-search-mcp"],
            "env": {"BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")},
        },
    )

    async with filesystem_server, search_server:
        agent = task_agent.clone(
            mcp_servers=[filesystem_server, search_server]
        )
        state = TaskState(
            goal="Process all document transformations",
            max_retries=max_retries,
        )
        for t in tasks:
            state.queue.append(TaskItem(
                id=t["id"],
                description=t["description"],
                input_data=t["input_data"],
            ))

        while state.should_continue:
            item = state.next_item()
            if item is None:
                break

            task_input = dict(
                task_id=item.id,
                description=item.description,
                input_data=item.input_data,
                attempt=item.attempts + 1,
                previous_error=item.error,
            )
            print(f"Processing task {item.id} "
                  f"(attempt {item.attempts + 1})")

            try:
                result = await Runner.run(
                    agent, input=str(task_input)
                )
                task_result = result.final_output
                if task_result.success:
                    state.record_success(item, task_result.output)
                    print(f"  ✓ {item.id} completed")
                else:
                    state.record_failure(item, task_result.error)
                    print(f"  ✗ {item.id} failed: "
                          f"{task_result.error[:80]}")
            except Exception as e:
                state.record_failure(item, str(e))
                print(f"  ✗ {item.id} exception: {str(e)[:80]}")

            print(f"  Progress: {state.progress:.0%}")

        return state


async def main():
    tasks = [
        {
            "id": "doc-001",
            "description": "Summarize the meeting notes",
            "input_data": {"file": "meeting_notes.txt"},
        },
        {
            "id": "doc-002",
            "description": "Extract action items from the report",
            "input_data": {"file": "quarterly_report.txt"},
        },
        {
            "id": "doc-003",
            "description": "Translate the readme to Spanish",
            "input_data": {"file": "README.md"},
        },
    ]
    state = await run_task_loop(tasks)
    print(f"\n{'='*50}")
    print(f"Completed: {len(state.completed)}/{len(tasks)}")
    print(f"Failed: {len(state.failed)}/{len(tasks)}")
    for item in state.completed:
        print(f"  ✓ {item.id}: {item.result[:100]}")
    for item in state.failed:
        print(f"  ✗ {item.id}: {item.error[:100]}")


asyncio.run(main())

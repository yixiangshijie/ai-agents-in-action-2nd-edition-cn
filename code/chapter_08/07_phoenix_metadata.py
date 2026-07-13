from agents import trace
from openinference.instrumentation import using_metadata, using_session, using_user
from phoenix.otel import register

register(project_name="Agents In Action")  # A

with (
    using_session("s-123"),
    using_user("u-42"),
    using_metadata({"turn_id": "t-1", "intent": "generate_image"}),
):
    with trace("agent-turn"):  # B
        pass  # C
        # ... your agent code here ...

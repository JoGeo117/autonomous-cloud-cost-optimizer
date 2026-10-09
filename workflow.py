"""Supervisor StateGraph Workflow using LangGraph."""

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from agents.monitoring import monitoring_agent_node
from agents.analysis import analysis_agent_node
from agents.recommender import recommendation_engine_node
from agents.execution import execution_agent_node


def build_optimizer_graph():
    """Assembles the LangGraph StateGraph with checkpointing and HITL interruption."""
    workflow = StateGraph(AgentState)

    # 1. Register Worker Nodes
    workflow.add_node("monitoring_agent", monitoring_agent_node)
    workflow.add_node("analysis_agent", analysis_agent_node)
    workflow.add_node("recommendation_engine", recommendation_engine_node)
    workflow.add_node("execution_agent", execution_agent_node)

    # 2. Define Directed Transitions
    workflow.set_entry_point("monitoring_agent")
    workflow.add_edge("monitoring_agent", "analysis_agent")
    workflow.add_edge("analysis_agent", "recommendation_engine")
    workflow.add_edge("recommendation_engine", "execution_agent")
    workflow.add_edge("execution_agent", END)

    # 3. Compile with Checkpointing and HITL Interruption point
    # We interrupt before 'execution_agent' so operators can review Tier 2/3 approvals
    checkpointer = MemorySaver()
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execution_agent"]
    )
    return app

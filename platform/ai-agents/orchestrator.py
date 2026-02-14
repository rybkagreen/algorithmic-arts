"""AI Agent Orchestrator for ALGORITHMIC ARTS platform."""

from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple AI agents and manages their execution flow."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        if not isinstance(agent, BaseAgent):
            raise ValueError("Agent must inherit from BaseAgent")
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name."""
        return self.agents.get(agent_name)
    
    async def execute_single(self, agent_name: str, **kwargs) -> AgentResult:
        """Execute a single agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            return AgentResult(
                success=False,
                data={},
                error=f"Agent '{agent_name}' not found"
            )
        
        try:
            result = await agent.run(**kwargs)
            return AgentResult(success=True, data=result)
        except Exception as e:
            return AgentResult(success=False, data={}, error=str(e))
    
    async def execute_parallel(self, agent_tasks: List[Dict[str, Any]]) -> List[AgentResult]:
        """Execute multiple agents in parallel."""
        import asyncio
        
        tasks = []
        for task in agent_tasks:
            agent_name = task.get("agent")
            kwargs = task.get("kwargs", {})
            tasks.append(self.execute_single(agent_name, **kwargs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(AgentResult(
                    success=False,
                    data={},
                    error=f"Execution failed: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_sequential(self, agent_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute agents in sequence, passing results between them."""
        current_context = {}
        
        for step in agent_sequence:
            agent_name = step.get("agent")
            kwargs = step.get("kwargs", {})
            
            # Merge context into kwargs
            merged_kwargs = {**current_context, **kwargs}
            
            result = await self.execute_single(agent_name, **merged_kwargs)
            
            if not result.success:
                return {
                    "success": False,
                    "error": f"Sequential execution failed at step {agent_name}: {result.error}",
                    "context": current_context
                }
            
            # Update context with result data
            current_context.update(result.data)
        
        return {
            "success": True,
            "context": current_context,
            "final_result": current_context
        }
    
    async def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow based on configuration."""
        workflow_type = workflow_config.get("type", "sequential")
        
        if workflow_type == "sequential":
            return await self.execute_sequential(workflow_config.get("steps", []))
        elif workflow_type == "parallel":
            return await self.execute_parallel(workflow_config.get("tasks", []))
        elif workflow_type == "hybrid":
            return await self._execute_hybrid_workflow(workflow_config)
        else:
            return {
                "success": False,
                "error": f"Unknown workflow type: {workflow_type}"
            }
    
    async def _execute_hybrid_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid workflows with both sequential and parallel steps."""
        result_context = {}
        
        for step in config.get("steps", []):
            step_type = step.get("type", "sequential")
            
            if step_type == "sequential":
                seq_result = await self.execute_sequential(step.get("steps", []))
                if not seq_result["success"]:
                    return seq_result
                result_context.update(seq_result.get("context", {}))
            elif step_type == "parallel":
                parallel_results = await self.execute_parallel(step.get("tasks", []))
                # Combine parallel results
                combined_data = {}
                for i, result in enumerate(parallel_results):
                    if result.success:
                        combined_data[f"task_{i}"] = result.data
                    else:
                        return {
                            "success": False,
                            "error": f"Parallel task {i} failed: {result.error}",
                            "context": result_context
                        }
                result_context.update(combined_data)
        
        return {
            "success": True,
            "context": result_context,
            "final_result": result_context
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution history."""
        return {
            "total_executions": len(self.execution_history),
            "agents_registered": len(self.agents),
            "recent_executions": self.execution_history[-5:] if self.execution_history else []
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
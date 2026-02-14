"""Base AI Agent class for the ALGORITHMIC ARTS platform."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all AI agents in the system."""
    
    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_used = None
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main functionality.
        
        Args:
            **kwargs: Agent-specific parameters
            
        Returns:
            Dict containing results and metadata
        """
        pass
    
    async def preprocess_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data before execution."""
        return input_data
    
    async def postprocess_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess output data after execution."""
        return output_data
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "type": self.__class__.__name__
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the agent with preprocessing, execution, and postprocessing."""
        try:
            self.last_used = datetime.utcnow()
            
            # Preprocess input
            processed_input = await self.preprocess_input(kwargs)
            
            # Execute agent logic
            raw_result = await self.execute(**processed_input)
            
            # Postprocess output
            final_result = await self.postprocess_output(raw_result)
            
            # Add metadata
            final_result["metadata"] = self.get_metadata()
            
            return final_result
            
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}", exc_info=True)
            raise


class AgentResult:
    """Container for agent execution results."""
    
    def __init__(self, success: bool, data: Dict[str, Any], error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }
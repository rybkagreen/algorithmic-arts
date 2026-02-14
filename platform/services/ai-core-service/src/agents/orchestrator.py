from langgraph.graph import StateGraph, END
from .base_agent import AgentState
from .scout_agent import PartnershipScoutAgent
from .analyzer_agent import CompatibilityAnalyzerAgent
from .writer_agent import OutreachWriterAgent
from .enricher_agent import DataEnricherAgent
from .predictor_agent import AnalyticsPredictorAgent

def create_ai_graph(
    scout_agent: PartnershipScoutAgent,
    analyzer_agent: CompatibilityAnalyzerAgent,
    writer_agent: OutreachWriterAgent,
    enricher_agent: DataEnricherAgent,
    predictor_agent: AnalyticsPredictorAgent,
) -> StateGraph:
    """
    Создает LangGraph для мультиагентной системы.
    """
    workflow = StateGraph(AgentState)
    
    # Добавляем узлы
    workflow.add_node("scout", scout_agent.run)
    workflow.add_node("enrich", enricher_agent.run)
    workflow.add_node("analyze", analyzer_agent.run)
    workflow.add_node("write", writer_agent.run)
    workflow.add_node("predict", predictor_agent.run)
    
    # Условные переходы
    def should_notify(state: AgentState) -> str:
        return "notify" if state.should_notify else "end"
    
    def should_enrich(state: AgentState) -> str:
        return "enrich" if state.company_id and not state.enriched_company else "analyze"
    
    # Подключаем узлы
    workflow.set_entry_point("scout")
    workflow.add_edge("scout", "enrich")
    workflow.add_conditional_edges("enrich", should_enrich)
    workflow.add_edge("analyze", "write")
    workflow.add_edge("write", "predict")
    workflow.add_conditional_edges("predict", should_notify)
    
    workflow.add_node("notify", lambda state: state)  # Заглушка для уведомлений
    workflow.add_edge("notify", END)
    workflow.add_edge("end", END)
    
    return workflow.compile()
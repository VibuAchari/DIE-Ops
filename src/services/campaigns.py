"""Application service for campaign recommendation."""
from dataclasses import dataclass
import pandas as pd
from src.decision_engine.actions import build_action_candidates
from src.decision_engine.optimizer import roi_select

@dataclass(frozen=True)
class CampaignRequest:
    budget: float = 5000.0
    margin: float = 0.30

    def validate(self) -> None:
        if self.budget < 0:
            raise ValueError("budget must be >= 0")
        if not 0 <= self.margin <= 1:
            raise ValueError("margin must be between 0 and 1")

class CampaignService:
    """Coordinates scoring, action policy, and budget selection."""
    def __init__(self, scorer, customer_data: pd.DataFrame):
        self._scorer = scorer
        self._customer_data = customer_data

    def recommend(self, request: CampaignRequest) -> dict:
        request.validate()
        scored = self._scorer(self._customer_data.copy())
        candidates = build_action_candidates(scored, margin=request.margin)
        if candidates.empty:
            return {"summary": {"selected_count": 0, "budget_used": 0.0, "expected_profit": 0.0, "avg_profit_per_customer": 0.0}, "selected_customers": []}

        best_idx = candidates.groupby("customer_id")["net_profit"].idxmax()
        candidates = candidates.loc[best_idx].reset_index(drop=True)
        selected_df, _ = roi_select(candidates, budget=request.budget, margin=request.margin)

        expected_profit = float(selected_df["net_profit"].sum())
        budget_used = float(selected_df["cost"].sum())
        selected_count = len(selected_df)
        return {
            "summary": {
                "selected_count": selected_count,
                "budget_used": budget_used,
                "expected_profit": expected_profit,
                "avg_profit_per_customer": expected_profit / selected_count if selected_count else 0.0,
            },
            "selected_customers": selected_df.to_dict(orient="records"),
        }

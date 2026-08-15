"""Application service for campaign recommendation and customer decisions."""

from dataclasses import dataclass
from typing import Callable

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
    """Coordinate scoring, policy selection, and budget optimization."""

    def __init__(
        self,
        scorer: Callable[[pd.DataFrame], pd.DataFrame],
        customer_data: pd.DataFrame,
    ):
        self._scorer = scorer
        self._customer_data = customer_data

    def _customer(self, customer_id: int) -> pd.DataFrame:
        df = self._customer_data[
            self._customer_data["customer_id"] == customer_id
        ].copy()
        if df.empty:
            raise KeyError(customer_id)
        return df

    def score_customer(self, customer_id: int) -> dict:
        row = self._scorer(self._customer(customer_id)).iloc[0]
        return {
            "customer_id": int(row["customer_id"]),
            "churn_prob": float(row["churn_prob"]),
            "uplift": float(row["uplift"]),
            "cltv_raw": float(row["cltv_raw"]),
        }

    def policy_options(self, customer_id: int, margin: float = 0.30) -> list[dict]:
        request = CampaignRequest(margin=margin)
        request.validate()
        candidates = build_action_candidates(
            self._scorer(self._customer(customer_id)),
            margin=margin,
        )
        return candidates.to_dict(orient="records")

    def policy_decision(self, customer_id: int, margin: float = 0.30) -> dict:
        options = self.policy_options(customer_id, margin=margin)
        if not options:
            return {
                "customer_id": customer_id,
                "decision": None,
                "reason": "No profitable intervention available.",
            }

        best = max(options, key=lambda item: item["net_profit"])
        return {
            "customer_id": customer_id,
            "decision": {
                "offer": best["offer"],
                "cost": float(best["cost"]),
                "net_profit": float(best["net_profit"]),
                "roi_ratio": float(best["net_profit"] / best["cost"]),
            },
            "justification": (
                "Policy selects the action that maximizes expected profit "
                "among all available interventions."
            ),
        }

    def recommend(self, request: CampaignRequest) -> dict:
        request.validate()
        scored = self._scorer(self._customer_data.copy())
        candidates = build_action_candidates(scored, margin=request.margin)

        if candidates.empty:
            return {
                "summary": {
                    "selected_count": 0,
                    "budget_used": 0.0,
                    "expected_profit": 0.0,
                    "avg_profit_per_customer": 0.0,
                },
                "selected_customers": [],
            }

        best_idx = candidates.groupby("customer_id")["net_profit"].idxmax()
        candidates = candidates.loc[best_idx].reset_index(drop=True)
        selected_df, _ = roi_select(
            candidates,
            budget=request.budget,
            margin=request.margin,
        )

        expected_profit = float(selected_df["net_profit"].sum())
        budget_used = float(selected_df["cost"].sum())
        selected_count = len(selected_df)

        return {
            "summary": {
                "selected_count": selected_count,
                "budget_used": budget_used,
                "expected_profit": expected_profit,
                "avg_profit_per_customer": (
                    expected_profit / selected_count if selected_count else 0.0
                ),
            },
            "selected_customers": selected_df.to_dict(orient="records"),
        }

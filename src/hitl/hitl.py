"""
Lab 11 — Optional enrichment: Human-in-the-Loop Design
  (Không chấm — tham khảo. Tóm tắt nộp do scripts/grade.py tự sinh,
   không viết report/*.md tay.)
  - Confidence Router
  - 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# Optional enrichment: ConfidenceRouter (không chấm)
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        # Optional: Implement routing logic
        #
        # 1. Check if action_type is in HIGH_RISK_ACTIONS
        #    -> If yes: always escalate (action="escalate", priority="high",
        #       requires_human=True, reason="High-risk action: {action_type}")
        #
        # 2. Check confidence thresholds:
        #    - confidence >= 0.9:
        #      action="auto_send", priority="low",
        #      requires_human=False, reason="High confidence"
        #
        #    - 0.7 <= confidence < 0.9:
        #      action="queue_review", priority="normal",
        #      requires_human=True, reason="Medium confidence — needs review"
        #
        #    - confidence < 0.7:
        #      action="escalate", priority="high",
        #      requires_human=True, reason="Low confidence — escalating"

        # TODO: Replace with implementation
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action: {action_type}",
                priority="high",
                requires_human=True,
            )

        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=confidence,
                reason="High confidence",
                priority="low",
                requires_human=False,
            )
        elif confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=confidence,
                reason="Medium confidence — needs review",
                priority="normal",
                requires_human=True,
            )
        else:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason="Low confidence — escalating",
                priority="high",
                requires_human=True,
            )


# ============================================================
# Optional enrichment: 3 HITL decision points (không chấm)
# Không bắt buộc điền. Tóm tắt bài nộp: chạy scripts/grade.py
# (tự sinh lab_report.md) — không viết report tay.
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
# - approval_path: What approve/reject/timeout decision is recorded?
# - audit_fields: Which correlation ID, intent and proposed action/diff are logged?
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        # "name": "TODO: Name this decision point",
        # "trigger": "TODO: When does this trigger?",
        # "hitl_model": "TODO: human-in-the-loop / human-on-the-loop / human-as-tiebreaker",
        # "context_needed": "TODO: What does the reviewer need to see?",
        # "example": "TODO: Give a concrete example scenario",
        # "approval_path": "TODO: Explain approve, reject and timeout behavior",
        # "audit_fields": "TODO: List correlation ID, intent, diff and reviewer decision",
        "name": "High-Value Money Transfer Approval",
        "trigger": "Customer or RAG-extracted action proposes a money transfer (`transfer_money`) or wire payment exceeding tier thresholds.",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Customer identity & KYC status, source/destination account numbers, transfer amount, recent transaction history, and prompt provenance.",
        "example": "A user asks the assistant to transfer 50,000,000 VND to a new external beneficiary account.",
        "approval_path": "Approve: execute transfer with signed token `HITL-XXXXXXXX`; Reject: cancel transaction and notify customer; Timeout (15m): fail-closed (auto-cancel) and require re-initiation.",
        "audit_fields": "correlation_id, user_id, intent='transfer_money', proposed_diff={'from': acct_a, 'to': acct_b, 'amount': 50000000}, reviewer_id, approval_id, decision, timestamp",
    },
    {
        "id": 2,
        # "name": "TODO: Name this decision point",
        # "trigger": "TODO: When does this trigger?",
        # "hitl_model": "TODO: human-in-the-loop / human-on-the-loop / human-as-tiebreaker",
        # "context_needed": "TODO: What does the reviewer need to see?",
        # "example": "TODO: Give a concrete example scenario",
        # "approval_path": "TODO: Explain approve, reject and timeout behavior",
        # "audit_fields": "TODO: List correlation ID, intent, diff and reviewer decision",
        "name": "Account Closure & Personal Data Modification",
        "trigger": "Request involves `close_account`, `change_password`, `delete_data`, or `update_personal_info`.",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Verified customer session, current vs. proposed account profile diff, outstanding loan/card balances, and fraud risk score.",
        "example": "A customer requests to close their savings account and update their registered phone number and email address.",
        "approval_path": "Approve: apply profile/account state change; Reject: keep existing state and send security alert; Timeout (30m): abort change and lock sensitive action pending callback verification.",
        "audit_fields": "correlation_id, user_id, intent='close_account|update_personal_info', proposed_diff={'status': 'closed', 'phone': '[REDACTED]'}, reviewer_id, approval_id, decision, timestamp",
    },
    {
        "id": 3,
        # "name": "TODO: Name this decision point",
        # "trigger": "TODO: When does this trigger?",
        # "hitl_model": "TODO: human-in-the-loop / human-on-the-loop / human-as-tiebreaker",
        # "context_needed": "TODO: What does the reviewer need to see?",
        # "example": "TODO: Give a concrete example scenario",
        # "approval_path": "TODO: Explain approve, reject and timeout behavior",
        # "audit_fields": "TODO: List correlation ID, intent, diff and reviewer decision",
        "name": "Ambiguous Policy / Borderline Guardrail & Judge Escalation",
        "trigger": "Model confidence is below 0.90 (`0.70 <= confidence < 0.90` queued, `< 0.70` immediate escalation) or safety judge flags borderline policy/loan-eligibility advice.",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "User query, retrieved RAG policy snippets, draft assistant response, confidence score, and guardrail/judge flags.",
        "example": "A customer asks about special debt restructuring terms where the assistant's confidence is 0.65 and the draft cites unverified interest rates.",
        "approval_path": "Approve: release or edit draft response to customer; Reject: replace with standard safe banking fallback and escalate to specialist; Timeout (10m): send safe holding message and assign ticket to support queue.",
        "audit_fields": "correlation_id, user_id, intent='policy_inquiry', proposed_diff={'draft_response': '...', 'edited_response': '...'}, reviewer_id, decision, confidence, timestamp",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()

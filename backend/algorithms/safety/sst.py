"""
SST - SANA Safety & Triage Model
Detects health crises and prevents harm through early intervention
"""
from typing import List, Dict, Tuple, Optional
from uuid import UUID
import logging
from datetime import datetime, timedelta
from statistics import mean

from .models import (
    SSTInput,
    SSTOutput,
    SafetyStatus,
    RiskCategory,
    EscalationPathway,
    RiskIndicator,
    CrisisKeyword,
    SafetyResource,
    ImmediateAction,
    HumanReviewCase,
    HistoricalScore,
    # Legacy imports
    SafetyInput,
    SafetyOutput,
    RiskLevel
)

logger = logging.getLogger(__name__)


class SSTAlgorithm:
    """
    SANA Safety & Triage Model (SST)

    Monitors user health and safety through:
    1. SISM score analysis (current and trends)
    2. Keyword detection for crisis language
    3. Pattern recognition (disengagement, deterioration)
    4. Risk scoring and triage decisions
    5. Escalation pathway determination
    6. Human review case creation
    """

    # Risk thresholds
    SAFE_THRESHOLD = 30
    MONITOR_THRESHOLD = 60
    ESCALATE_THRESHOLD = 85

    # Score thresholds
    CRITICAL_SCORE = 30
    LOW_SCORE = 40

    # Trend thresholds
    RAPID_DECLINE = 20  # Points dropped in 2 weeks
    CHRONIC_LOW_WEEKS = 4

    # Crisis keywords
    CRISIS_KEYWORDS = [
        CrisisKeyword(keyword="suicide", category=RiskCategory.SUICIDAL_IDEATION, severity=10),
        CrisisKeyword(keyword="kill myself", category=RiskCategory.SUICIDAL_IDEATION, severity=10),
        CrisisKeyword(keyword="end it all", category=RiskCategory.SUICIDAL_IDEATION, severity=10),
        CrisisKeyword(keyword="no point living", category=RiskCategory.SUICIDAL_IDEATION, severity=10),
        CrisisKeyword(keyword="self harm", category=RiskCategory.SELF_HARM, severity=9),
        CrisisKeyword(keyword="cut myself", category=RiskCategory.SELF_HARM, severity=9),
        CrisisKeyword(keyword="hurt myself", category=RiskCategory.SELF_HARM, severity=8),
        CrisisKeyword(keyword="can't go on", category=RiskCategory.SEVERE_DEPRESSION, severity=8),
        CrisisKeyword(keyword="want to die", category=RiskCategory.SUICIDAL_IDEATION, severity=9),
        CrisisKeyword(keyword="better off dead", category=RiskCategory.SUICIDAL_IDEATION, severity=9),
        CrisisKeyword(keyword="panic attack", category=RiskCategory.ANXIETY_CRISIS, severity=7),
        CrisisKeyword(keyword="can't breathe", category=RiskCategory.ANXIETY_CRISIS, severity=7),
    ]

    # Safety resources
    SAFETY_RESOURCES = [
        SafetyResource(
            name="Samaritans",
            description="24/7 confidential emotional support",
            contact_method="phone",
            contact_details="116 123 (free)",
            availability="24/7",
            appropriate_for=[
                RiskCategory.SUICIDAL_IDEATION,
                RiskCategory.SEVERE_DEPRESSION,
                RiskCategory.SELF_HARM
            ]
        ),
        SafetyResource(
            name="Shout Crisis Text Line",
            description="24/7 text support for crisis",
            contact_method="text",
            contact_details="Text SHOUT to 85258",
            availability="24/7",
            appropriate_for=[
                RiskCategory.ANXIETY_CRISIS,
                RiskCategory.SEVERE_DEPRESSION,
                RiskCategory.SELF_HARM
            ]
        ),
        SafetyResource(
            name="NHS 111",
            description="Urgent medical advice",
            contact_method="phone",
            contact_details="111",
            availability="24/7",
            appropriate_for=[
                RiskCategory.SEVERE_DEPRESSION,
                RiskCategory.ANXIETY_CRISIS,
                RiskCategory.CHRONIC_PAIN
            ]
        ),
        SafetyResource(
            name="Mind Mental Health Support",
            description="Information and support for mental health",
            contact_method="online",
            contact_details="www.mind.org.uk",
            availability="24/7 (online resources)",
            appropriate_for=[
                RiskCategory.SEVERE_DEPRESSION,
                RiskCategory.ANXIETY_CRISIS
            ]
        ),
    ]

    def __init__(self):
        """Initialize SST"""
        logger.info("SST initialized")

    def analyze_safety(self, sst_input: SSTInput) -> SSTOutput:
        """
        Main safety analysis method

        Args:
            sst_input: Complete user data for safety analysis

        Returns:
            SSTOutput with risk assessment and recommended actions
        """
        logger.info(f"Analyzing safety for user {sst_input.user_id}")

        risk_indicators = []

        # Step 1: Analyze current SISM score
        score_indicators = self._analyze_current_score(
            sst_input.current_sism_score,
            sst_input.current_domain_scores
        )
        risk_indicators.extend(score_indicators)

        # Step 2: Analyze score trends (if historical data available)
        if sst_input.historical_scores:
            trend_indicators = self._analyze_score_trends(
                sst_input.current_sism_score,
                sst_input.historical_scores
            )
            risk_indicators.extend(trend_indicators)

        # Step 3: Keyword detection in text (if available)
        if sst_input.recent_journal_entries or sst_input.questionnaire_free_text:
            all_text = sst_input.recent_journal_entries + sst_input.questionnaire_free_text
            keyword_indicators = self._detect_crisis_keywords(all_text)
            risk_indicators.extend(keyword_indicators)

        # Step 4: Pattern analysis (activity, engagement)
        pattern_indicators = self._analyze_patterns(sst_input)
        risk_indicators.extend(pattern_indicators)

        # Step 5: Calculate overall risk score
        risk_score = self._calculate_risk_score(
            risk_indicators,
            sst_input.current_sism_score
        )

        # Step 6: Determine safety status
        safety_status = self._determine_safety_status(risk_score)

        # Step 7: Identify primary risk category
        risk_category = self._identify_primary_risk_category(risk_indicators)

        # Step 8: Determine escalation pathway
        escalation_pathway = self._determine_escalation_pathway(
            safety_status,
            risk_category,
            risk_indicators
        )

        # Step 9: Generate recommendations
        recommended_action = self._generate_recommended_action(
            safety_status,
            escalation_pathway
        )

        # Step 10: Create immediate actions
        immediate_actions = self._create_immediate_actions(
            safety_status,
            risk_category,
            risk_indicators
        )

        # Step 11: Select appropriate resources
        resources = self._select_resources(risk_category, risk_indicators)

        # Step 12: Determine if human review needed
        requires_review = safety_status in [SafetyStatus.ESCALATE, SafetyStatus.URGENT]

        human_review_case = None
        review_deadline = None

        if requires_review:
            priority = "critical" if safety_status == SafetyStatus.URGENT else "high"
            human_review_case = self._create_review_case(
                sst_input.user_id,
                risk_score,
                safety_status,
                risk_indicators,
                recommended_action,
                escalation_pathway,
                priority
            )

            # Set review deadline
            if safety_status == SafetyStatus.URGENT:
                review_deadline = datetime.utcnow() + timedelta(hours=2)
            else:
                review_deadline = datetime.utcnow() + timedelta(hours=24)

        # Step 13: Generate user-facing message
        user_message = self._generate_user_message(safety_status, risk_category)
        show_banner = safety_status in [SafetyStatus.ESCALATE, SafetyStatus.URGENT]

        # Step 14: Assess score trend
        score_trend, trend_percentage = self._calculate_trend(
            sst_input.current_sism_score,
            sst_input.historical_scores
        )

        # Step 15: Generate primary concerns summary
        primary_concerns = self._summarize_concerns(risk_indicators)

        # Step 16: Calculate confidence in assessment
        confidence = self._calculate_confidence(
            len(risk_indicators),
            len(sst_input.historical_scores),
            bool(sst_input.recent_journal_entries)
        )

        # Build output
        output = SSTOutput(
            user_id=sst_input.user_id,
            safety_status=safety_status,
            risk_score=risk_score,
            risk_category=risk_category,
            risk_indicators=risk_indicators,
            primary_concerns=primary_concerns,
            score_trend=score_trend,
            trend_percentage=trend_percentage,
            recommended_action=recommended_action,
            immediate_actions=immediate_actions,
            escalation_pathway=escalation_pathway,
            resources_to_provide=resources,
            requires_human_review=requires_review,
            human_review_case=human_review_case,
            review_deadline=review_deadline,
            user_message=user_message,
            show_emergency_banner=show_banner,
            confidence=confidence
        )

        logger.info(
            f"Safety analysis complete for user {sst_input.user_id}: "
            f"Status={safety_status.value}, Risk={risk_score:.1f}, "
            f"Review={requires_review}"
        )

        return output

    def _analyze_current_score(
        self,
        overall_score: float,
        domain_scores: Dict[str, float]
    ) -> List[RiskIndicator]:
        """Analyze current SISM score for risk"""
        indicators = []

        # Check overall score
        if overall_score < self.CRITICAL_SCORE:
            indicators.append(RiskIndicator(
                indicator_type="low_score",
                risk_category=RiskCategory.RAPID_DETERIORATION,
                severity=9,
                description=f"Critical overall health score: {overall_score:.1f}",
                evidence={"overall_score": overall_score, "threshold": self.CRITICAL_SCORE}
            ))
        elif overall_score < self.LOW_SCORE:
            indicators.append(RiskIndicator(
                indicator_type="low_score",
                risk_category=RiskCategory.SEVERE_DEPRESSION,
                severity=7,
                description=f"Low overall health score: {overall_score:.1f}",
                evidence={"overall_score": overall_score}
            ))

        # Check domain scores
        emotional_score = domain_scores.get("emotional", 100)
        if emotional_score < 20:
            indicators.append(RiskIndicator(
                indicator_type="low_domain_score",
                risk_category=RiskCategory.SEVERE_DEPRESSION,
                severity=9,
                description=f"Critically low emotional health: {emotional_score:.1f}",
                evidence={"emotional_score": emotional_score}
            ))
        elif emotional_score < 35:
            indicators.append(RiskIndicator(
                indicator_type="low_domain_score",
                risk_category=RiskCategory.ANXIETY_CRISIS,
                severity=7,
                description=f"Low emotional health: {emotional_score:.1f}",
                evidence={"emotional_score": emotional_score}
            ))

        # Check for multiple low domains (complex needs)
        low_domains = [d for d, s in domain_scores.items() if s < 40]
        if len(low_domains) >= 3:
            indicators.append(RiskIndicator(
                indicator_type="multiple_low_domains",
                risk_category=RiskCategory.RAPID_DETERIORATION,
                severity=8,
                description=f"Multiple domains critically low: {', '.join(low_domains)}",
                evidence={"low_domains": low_domains}
            ))

        return indicators

    def _analyze_score_trends(
        self,
        current_score: float,
        historical_scores: List[HistoricalScore]
    ) -> List[RiskIndicator]:
        """Analyze score trends for deterioration"""
        indicators = []

        if len(historical_scores) < 1:
            return indicators

        # Sort by date
        sorted_scores = sorted(historical_scores, key=lambda x: x.recorded_at)

        # Check 2-week deterioration
        two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
        recent_scores = [s for s in sorted_scores if s.recorded_at >= two_weeks_ago]

        if recent_scores:
            earliest_recent = recent_scores[0].overall_score
            score_drop = earliest_recent - current_score

            if score_drop >= self.RAPID_DECLINE:
                indicators.append(RiskIndicator(
                    indicator_type="rapid_decline",
                    risk_category=RiskCategory.RAPID_DETERIORATION,
                    severity=9,
                    description=f"Rapid health decline: dropped {score_drop:.1f} points in 2 weeks",
                    evidence={
                        "previous_score": earliest_recent,
                        "current_score": current_score,
                        "drop": score_drop
                    }
                ))

        # Check chronic low scores
        four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
        chronic_period = [s for s in sorted_scores if s.recorded_at >= four_weeks_ago]

        if len(chronic_period) >= 3:
            avg_score = mean([s.overall_score for s in chronic_period])
            if avg_score < self.LOW_SCORE:
                indicators.append(RiskIndicator(
                    indicator_type="chronic_low",
                    risk_category=RiskCategory.SEVERE_DEPRESSION,
                    severity=7,
                    description=f"Chronically low scores: averaging {avg_score:.1f} for 4+ weeks",
                    evidence={"average_score": avg_score, "weeks": 4}
                ))

        return indicators

    def _detect_crisis_keywords(self, text_list: List[str]) -> List[RiskIndicator]:
        """Detect crisis keywords in user text"""
        indicators = []

        # Combine all text
        all_text = " ".join(text_list).lower()

        # Check each crisis keyword
        for crisis_keyword in self.CRISIS_KEYWORDS:
            if crisis_keyword.keyword.lower() in all_text:
                indicators.append(RiskIndicator(
                    indicator_type="keyword_detected",
                    risk_category=crisis_keyword.category,
                    severity=crisis_keyword.severity,
                    description=f"Crisis keyword detected: '{crisis_keyword.keyword}'",
                    evidence={"keyword": crisis_keyword.keyword}
                ))

        return indicators

    def _analyze_patterns(self, sst_input: SSTInput) -> List[RiskIndicator]:
        """Analyze behavioral patterns"""
        indicators = []

        # Check for disengagement
        if sst_input.days_since_last_activity and sst_input.days_since_last_activity > 14:
            indicators.append(RiskIndicator(
                indicator_type="disengagement",
                risk_category=RiskCategory.EXTREME_ISOLATION,
                severity=6,
                description=f"No activity for {sst_input.days_since_last_activity} days",
                evidence={"days_inactive": sst_input.days_since_last_activity}
            ))

        # Check for missed appointments
        if sst_input.missed_practitioner_appointments > 2:
            indicators.append(RiskIndicator(
                indicator_type="missed_appointments",
                risk_category=RiskCategory.SEVERE_DEPRESSION,
                severity=5,
                description=f"Missed {sst_input.missed_practitioner_appointments} appointments",
                evidence={"missed_count": sst_input.missed_practitioner_appointments}
            ))

        # Check for declined interventions
        if sst_input.declined_interventions > 3:
            indicators.append(RiskIndicator(
                indicator_type="declined_interventions",
                risk_category=RiskCategory.SEVERE_DEPRESSION,
                severity=5,
                description=f"Declined {sst_input.declined_interventions} recommended interventions",
                evidence={"declined_count": sst_input.declined_interventions}
            ))

        return indicators

    def _calculate_risk_score(
        self,
        risk_indicators: List[RiskIndicator],
        current_sism_score: float
    ) -> float:
        """Calculate overall risk score"""
        if not risk_indicators:
            # Base risk on SISM score alone
            return max(0, 100 - current_sism_score)

        # Weight components
        sism_weight = 0.40
        indicator_weight = 0.60

        # SISM contribution (inverse - lower score = higher risk)
        sism_risk = (100 - current_sism_score) * sism_weight

        # Indicator contribution
        max_severity = max(ind.severity for ind in risk_indicators)
        indicator_count_factor = min(1.0, len(risk_indicators) / 5)  # Cap at 5 indicators

        indicator_risk = (max_severity * 10) * indicator_count_factor * indicator_weight

        total_risk = sism_risk + indicator_risk

        return min(100, max(0, total_risk))

    def _determine_safety_status(self, risk_score: float) -> SafetyStatus:
        """Determine safety status from risk score"""
        if risk_score >= self.ESCALATE_THRESHOLD:
            return SafetyStatus.URGENT
        elif risk_score >= self.MONITOR_THRESHOLD:
            return SafetyStatus.ESCALATE
        elif risk_score >= self.SAFE_THRESHOLD:
            return SafetyStatus.MONITOR
        else:
            return SafetyStatus.SAFE

    def _identify_primary_risk_category(
        self,
        risk_indicators: List[RiskIndicator]
    ) -> Optional[RiskCategory]:
        """Identify primary risk category"""
        if not risk_indicators:
            return None

        # Find highest severity indicator
        highest_severity_indicator = max(risk_indicators, key=lambda x: x.severity)
        return highest_severity_indicator.risk_category

    def _determine_escalation_pathway(
        self,
        safety_status: SafetyStatus,
        risk_category: Optional[RiskCategory],
        risk_indicators: List[RiskIndicator]
    ) -> EscalationPathway:
        """Determine where to escalate"""
        if safety_status == SafetyStatus.SAFE:
            return EscalationPathway.NO_ESCALATION

        # Check for suicidal ideation (highest priority)
        has_suicidal = any(
            ind.risk_category == RiskCategory.SUICIDAL_IDEATION
            for ind in risk_indicators
        )
        if has_suicidal:
            return EscalationPathway.SAMARITANS

        # Urgent cases
        if safety_status == SafetyStatus.URGENT:
            if risk_category in [RiskCategory.SEVERE_DEPRESSION, RiskCategory.ANXIETY_CRISIS]:
                return EscalationPathway.NHS_111
            elif risk_category == RiskCategory.SELF_HARM:
                return EscalationPathway.SAMARITANS
            else:
                return EscalationPathway.SANA_REVIEWER

        # Escalate cases
        if safety_status == SafetyStatus.ESCALATE:
            return EscalationPathway.SANA_REVIEWER

        # Monitor cases
        if safety_status == SafetyStatus.MONITOR:
            return EscalationPathway.NO_ESCALATION

        return EscalationPathway.NO_ESCALATION

    def _generate_recommended_action(
        self,
        safety_status: SafetyStatus,
        escalation_pathway: EscalationPathway
    ) -> str:
        """Generate recommended action text"""
        actions = {
            SafetyStatus.SAFE: "Continue monitoring user health scores. No immediate action required.",
            SafetyStatus.MONITOR: "Check in with user within 7 days. Provide additional resources and support.",
            SafetyStatus.ESCALATE: "Human review required within 24 hours. Assess need for professional referral.",
            SafetyStatus.URGENT: "URGENT: Immediate human review required. Contact user and provide crisis resources."
        }

        action = actions.get(safety_status, "")

        if escalation_pathway != EscalationPathway.NO_ESCALATION:
            action += f" Escalation pathway: {escalation_pathway.value.replace('_', ' ').title()}."

        return action

    def _create_immediate_actions(
        self,
        safety_status: SafetyStatus,
        risk_category: Optional[RiskCategory],
        risk_indicators: List[RiskIndicator]
    ) -> List[ImmediateAction]:
        """Create immediate actions to take"""
        actions = []

        if safety_status == SafetyStatus.URGENT:
            actions.append(ImmediateAction(
                action_type="display_message",
                message="We're concerned about your wellbeing. Please reach out to Samaritans (116 123) for immediate support.",
                urgency="critical",
                requires_acknowledgment=True
            ))

            actions.append(ImmediateAction(
                action_type="send_notification",
                message="URGENT: User requires immediate safety review",
                urgency="critical",
                requires_acknowledgment=False
            ))

        elif safety_status == SafetyStatus.ESCALATE:
            actions.append(ImmediateAction(
                action_type="display_message",
                message="We've noticed your health scores have declined. We're here to support you. Please review these resources.",
                urgency="high",
                requires_acknowledgment=False
            ))

        elif safety_status == SafetyStatus.MONITOR:
            actions.append(ImmediateAction(
                action_type="display_message",
                message="Your wellbeing is important to us. Here are some additional resources that might help.",
                urgency="medium",
                requires_acknowledgment=False
            ))

        return actions

    def _select_resources(
        self,
        risk_category: Optional[RiskCategory],
        risk_indicators: List[RiskIndicator]
    ) -> List[SafetyResource]:
        """Select appropriate resources for user"""
        if not risk_category:
            return []

        # Find resources appropriate for risk category
        relevant_resources = [
            resource for resource in self.SAFETY_RESOURCES
            if risk_category in resource.appropriate_for
        ]

        return relevant_resources[:3]  # Top 3 most relevant

    def _create_review_case(
        self,
        user_id: UUID,
        risk_score: float,
        safety_status: SafetyStatus,
        risk_indicators: List[RiskIndicator],
        recommended_action: str,
        escalation_pathway: EscalationPathway,
        priority: str
    ) -> HumanReviewCase:
        """Create human review case"""
        return HumanReviewCase(
            user_id=user_id,
            risk_score=risk_score,
            safety_status=safety_status,
            risk_indicators=risk_indicators,
            recommended_action=recommended_action,
            escalation_pathway=escalation_pathway,
            priority=priority
        )

    def _generate_user_message(
        self,
        safety_status: SafetyStatus,
        risk_category: Optional[RiskCategory]
    ) -> Optional[str]:
        """Generate message to show user"""
        if safety_status == SafetyStatus.SAFE:
            return None

        if safety_status == SafetyStatus.URGENT:
            return (
                "We're concerned about your wellbeing and want to help. "
                "Please reach out to Samaritans on 116 123 (free, 24/7) for confidential support. "
                "You don't have to face this alone."
            )

        if safety_status == SafetyStatus.ESCALATE:
            return (
                "We've noticed your health scores have declined and want to support you. "
                "A member of our care team will reach out within 24 hours. "
                "In the meantime, here are some resources that may help."
            )

        if safety_status == SafetyStatus.MONITOR:
            return (
                "Your wellbeing matters to us. We're here to support your health journey. "
                "Please explore these additional resources that might be helpful."
            )

        return None

    def _calculate_trend(
        self,
        current_score: float,
        historical_scores: List[HistoricalScore]
    ) -> Tuple[str, Optional[float]]:
        """Calculate score trend"""
        if not historical_scores:
            return "unknown", None

        sorted_scores = sorted(historical_scores, key=lambda x: x.recorded_at)

        if len(sorted_scores) < 1:
            return "insufficient_data", None

        # Compare to 2 weeks ago
        two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
        old_scores = [s for s in sorted_scores if s.recorded_at <= two_weeks_ago]

        if not old_scores:
            # Use the oldest available score
            old_score = sorted_scores[0].overall_score
        else:
            old_score = old_scores[-1].overall_score

        change = current_score - old_score
        percentage = (change / old_score) * 100 if old_score > 0 else 0

        if change >= 15:
            trend = "improving"
        elif change <= -20:
            trend = "rapidly_declining"
        elif change <= -10:
            trend = "declining"
        else:
            trend = "stable"

        return trend, round(percentage, 1)

    def _summarize_concerns(self, risk_indicators: List[RiskIndicator]) -> List[str]:
        """Summarize primary concerns"""
        if not risk_indicators:
            return []

        # Group by category
        concerns_by_category = {}
        for indicator in risk_indicators:
            category = indicator.risk_category.value
            if category not in concerns_by_category:
                concerns_by_category[category] = []
            concerns_by_category[category].append(indicator)

        # Summarize top concerns
        summaries = []
        for category, indicators in sorted(
            concerns_by_category.items(),
            key=lambda x: max(ind.severity for ind in x[1]),
            reverse=True
        )[:3]:  # Top 3 categories
            summaries.append(
                f"{category.replace('_', ' ').title()}: "
                f"{len(indicators)} indicator(s) detected"
            )

        return summaries

    def _calculate_confidence(
        self,
        indicator_count: int,
        historical_count: int,
        has_text_data: bool
    ) -> float:
        """Calculate confidence in assessment"""
        confidence = 50.0  # Base confidence

        # More indicators = higher confidence
        confidence += min(30, indicator_count * 6)

        # Historical data improves confidence
        confidence += min(15, historical_count * 3)

        # Text analysis improves confidence
        if has_text_data:
            confidence += 5

        return min(100, confidence)


# Legacy class for backwards compatibility
class SSTMonitor:
    """SANA Safety & Triage Model - Legacy interface."""

    def __init__(self):
        """Initialize the SST monitor."""
        self._sst = SSTAlgorithm()

    def assess(self, input_data: SafetyInput) -> SafetyOutput:
        """Legacy assessment method."""
        return SafetyOutput(
            user_id=input_data.user_id,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            flags=[],
            recommendations=[],
            requires_immediate_action=False
        )


def assess_safety(
    user_id: UUID,
    health_data: Dict,
    recent_responses: List[Dict] = None
) -> SafetyOutput:
    """Legacy safety assessment function."""
    monitor = SSTMonitor()
    input_data = SafetyInput(
        user_id=user_id,
        health_data=health_data,
        recent_responses=recent_responses or []
    )
    return monitor.assess(input_data)

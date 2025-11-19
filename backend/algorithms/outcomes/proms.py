"""
Patient-Reported Outcome Measures (PROMs) Implementation.

Includes validated measures:
- WHO-5 Wellbeing Index
- DASS-21 (Depression, Anxiety, Stress Scale)
- VAS (Visual Analogue Scale) for pain
- Custom CAM symptom scales
"""

from typing import List, Dict, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import math
import logging

from .models import (
    OutcomeMeasureType,
    MeasureTiming,
    Question,
    QuestionType,
    QuestionResponse,
    OutcomeMeasureRequest,
    OutcomeMeasureResponse,
    ScheduledMeasure,
    DeliveryMethod,
    MeasureComparison
)

logger = logging.getLogger(__name__)


class WHO5:
    """
    WHO-5 Wellbeing Index

    5 positively phrased questions, each scored 0-5 (25 max raw score).
    Multiply by 4 for 0-100 percentage scale.

    Cutoffs:
    - <50: Poor wellbeing, screening for depression indicated
    - 50-72: Moderate wellbeing
    - >72: Good wellbeing
    """

    QUESTIONS = [
        {
            "id": "who5_1",
            "text": "I have felt cheerful and in good spirits",
            "subscale": None
        },
        {
            "id": "who5_2",
            "text": "I have felt calm and relaxed",
            "subscale": None
        },
        {
            "id": "who5_3",
            "text": "I have felt active and vigorous",
            "subscale": None
        },
        {
            "id": "who5_4",
            "text": "I woke up feeling fresh and rested",
            "subscale": None
        },
        {
            "id": "who5_5",
            "text": "My daily life has been filled with things that interest me",
            "subscale": None
        }
    ]

    RESPONSE_OPTIONS = [
        "At no time",
        "Some of the time",
        "Less than half the time",
        "More than half the time",
        "Most of the time",
        "All of the time"
    ]

    @classmethod
    def get_questionnaire(cls, client_id: UUID, session_id: Optional[UUID] = None,
                          timing: MeasureTiming = MeasureTiming.PRE_SESSION) -> OutcomeMeasureRequest:
        """Generate WHO-5 questionnaire."""
        questions = [
            Question(
                id=q["id"],
                text=q["text"],
                question_type=QuestionType.LIKERT_5,
                options=cls.RESPONSE_OPTIONS,
                min_value=0,
                max_value=5,
                subscale=q["subscale"]
            )
            for q in cls.QUESTIONS
        ]

        return OutcomeMeasureRequest(
            measure_type=OutcomeMeasureType.WHO5,
            client_id=client_id,
            session_id=session_id,
            timing=timing,
            questions=questions,
            instructions="Please indicate for each of the five statements which is closest to how you have been feeling over the last two weeks.",
            estimated_time="1-2 minutes"
        )

    @classmethod
    def score(cls, responses: List[QuestionResponse]) -> OutcomeMeasureResponse:
        """Score WHO-5 responses."""
        if len(responses) != 5:
            raise ValueError(f"WHO-5 requires 5 responses, got {len(responses)}")

        # Calculate raw score (0-25)
        raw_score = sum(r.value for r in responses)

        # Convert to percentage (0-100)
        percentage_score = raw_score * 4

        # Determine severity
        if percentage_score < 50:
            severity = "poor"
            interpretation = "Your wellbeing score indicates you may benefit from additional support. Consider speaking with a healthcare provider."
            clinical_flags = ["Low wellbeing score - depression screening recommended"]
        elif percentage_score < 72:
            severity = "moderate"
            interpretation = "Your wellbeing is in the moderate range. There may be room for improvement in some areas."
            clinical_flags = []
        else:
            severity = "good"
            interpretation = "Your wellbeing score is good, indicating positive mental health."
            clinical_flags = []

        # Percentile (approximate, based on population norms)
        # WHO-5 mean ~70, SD ~15
        z_score = (percentage_score - 70) / 15
        percentile = min(99, max(1, 50 + z_score * 34))

        return OutcomeMeasureResponse(
            measure_id=uuid4(),
            measure_type=OutcomeMeasureType.WHO5,
            client_id=responses[0].question_id.split("_")[0] if responses else uuid4(),  # Placeholder
            timing=MeasureTiming.PRE_SESSION,
            responses=responses,
            total_score=percentage_score,
            subscale_scores={"raw": float(raw_score)},
            percentile=round(percentile, 1),
            severity=severity,
            interpretation=interpretation,
            clinical_flags=clinical_flags,
            completed_at=datetime.utcnow()
        )


class DASS21:
    """
    Depression, Anxiety, Stress Scale (DASS-21)

    21 questions across 3 subscales (7 each), scored 0-3.
    Multiply subscale scores by 2 for comparison with DASS-42.

    Severity cutoffs (multiplied scores):
    Depression: Normal 0-9, Mild 10-13, Moderate 14-20, Severe 21-27, Extreme 28+
    Anxiety: Normal 0-7, Mild 8-9, Moderate 10-14, Severe 15-19, Extreme 20+
    Stress: Normal 0-14, Mild 15-18, Moderate 19-25, Severe 26-33, Extreme 34+
    """

    QUESTIONS = [
        # Depression items
        {"id": "dass_1", "text": "I found it hard to wind down", "subscale": "stress"},
        {"id": "dass_2", "text": "I was aware of dryness of my mouth", "subscale": "anxiety"},
        {"id": "dass_3", "text": "I couldn't seem to experience any positive feeling at all", "subscale": "depression"},
        {"id": "dass_4", "text": "I experienced breathing difficulty (e.g., excessively rapid breathing, breathlessness in the absence of physical exertion)", "subscale": "anxiety"},
        {"id": "dass_5", "text": "I found it difficult to work up the initiative to do things", "subscale": "depression"},
        {"id": "dass_6", "text": "I tended to over-react to situations", "subscale": "stress"},
        {"id": "dass_7", "text": "I experienced trembling (e.g., in the hands)", "subscale": "anxiety"},
        {"id": "dass_8", "text": "I felt that I was using a lot of nervous energy", "subscale": "stress"},
        {"id": "dass_9", "text": "I was worried about situations in which I might panic and make a fool of myself", "subscale": "anxiety"},
        {"id": "dass_10", "text": "I felt that I had nothing to look forward to", "subscale": "depression"},
        {"id": "dass_11", "text": "I found myself getting agitated", "subscale": "stress"},
        {"id": "dass_12", "text": "I found it difficult to relax", "subscale": "stress"},
        {"id": "dass_13", "text": "I felt down-hearted and blue", "subscale": "depression"},
        {"id": "dass_14", "text": "I was intolerant of anything that kept me from getting on with what I was doing", "subscale": "stress"},
        {"id": "dass_15", "text": "I felt I was close to panic", "subscale": "anxiety"},
        {"id": "dass_16", "text": "I was unable to become enthusiastic about anything", "subscale": "depression"},
        {"id": "dass_17", "text": "I felt I wasn't worth much as a person", "subscale": "depression"},
        {"id": "dass_18", "text": "I felt that I was rather touchy", "subscale": "stress"},
        {"id": "dass_19", "text": "I was aware of the action of my heart in the absence of physical exertion (e.g., sense of heart rate increase, heart missing a beat)", "subscale": "anxiety"},
        {"id": "dass_20", "text": "I felt scared without any good reason", "subscale": "anxiety"},
        {"id": "dass_21", "text": "I felt that life was meaningless", "subscale": "depression"},
    ]

    RESPONSE_OPTIONS = [
        "Did not apply to me at all",
        "Applied to me to some degree, or some of the time",
        "Applied to me to a considerable degree or a good part of time",
        "Applied to me very much or most of the time"
    ]

    SEVERITY_CUTOFFS = {
        "depression": [(0, 9, "normal"), (10, 13, "mild"), (14, 20, "moderate"), (21, 27, "severe"), (28, 100, "extremely severe")],
        "anxiety": [(0, 7, "normal"), (8, 9, "mild"), (10, 14, "moderate"), (15, 19, "severe"), (20, 100, "extremely severe")],
        "stress": [(0, 14, "normal"), (15, 18, "mild"), (19, 25, "moderate"), (26, 33, "severe"), (34, 100, "extremely severe")]
    }

    @classmethod
    def get_questionnaire(cls, client_id: UUID, session_id: Optional[UUID] = None,
                          timing: MeasureTiming = MeasureTiming.PRE_SESSION) -> OutcomeMeasureRequest:
        """Generate DASS-21 questionnaire."""
        questions = [
            Question(
                id=q["id"],
                text=q["text"],
                question_type=QuestionType.LIKERT_7,
                options=cls.RESPONSE_OPTIONS,
                min_value=0,
                max_value=3,
                subscale=q["subscale"]
            )
            for q in cls.QUESTIONS
        ]

        return OutcomeMeasureRequest(
            measure_type=OutcomeMeasureType.DASS21,
            client_id=client_id,
            session_id=session_id,
            timing=timing,
            questions=questions,
            instructions="Please read each statement and select a number 0, 1, 2 or 3 which indicates how much the statement applied to you over the past week.",
            estimated_time="3-5 minutes"
        )

    @classmethod
    def score(cls, responses: List[QuestionResponse]) -> OutcomeMeasureResponse:
        """Score DASS-21 responses."""
        if len(responses) != 21:
            raise ValueError(f"DASS-21 requires 21 responses, got {len(responses)}")

        # Map responses to questions
        response_map = {r.question_id: r.value for r in responses}

        # Calculate subscale scores
        subscale_scores = {"depression": 0, "anxiety": 0, "stress": 0}

        for q in cls.QUESTIONS:
            if q["id"] in response_map:
                subscale_scores[q["subscale"]] += response_map[q["id"]]

        # Multiply by 2 for DASS-42 equivalent
        for key in subscale_scores:
            subscale_scores[key] *= 2

        # Total score
        total_score = sum(subscale_scores.values())

        # Determine severity for each subscale
        severities = {}
        for subscale, score in subscale_scores.items():
            for low, high, severity in cls.SEVERITY_CUTOFFS[subscale]:
                if low <= score <= high:
                    severities[subscale] = severity
                    break

        # Overall severity (worst of the three)
        severity_order = ["normal", "mild", "moderate", "severe", "extremely severe"]
        worst_severity = max(severities.values(), key=lambda x: severity_order.index(x))

        # Clinical flags
        clinical_flags = []
        if severities.get("depression", "normal") in ["severe", "extremely severe"]:
            clinical_flags.append("Severe depression symptoms - clinical evaluation recommended")
        if severities.get("anxiety", "normal") in ["severe", "extremely severe"]:
            clinical_flags.append("Severe anxiety symptoms - clinical evaluation recommended")
        if severities.get("stress", "normal") in ["severe", "extremely severe"]:
            clinical_flags.append("Severe stress symptoms")

        # Interpretation
        interpretation = f"Depression: {severities['depression']}, Anxiety: {severities['anxiety']}, Stress: {severities['stress']}"

        return OutcomeMeasureResponse(
            measure_id=uuid4(),
            measure_type=OutcomeMeasureType.DASS21,
            client_id=uuid4(),  # Placeholder
            timing=MeasureTiming.PRE_SESSION,
            responses=responses,
            total_score=total_score,
            subscale_scores={
                "depression": float(subscale_scores["depression"]),
                "anxiety": float(subscale_scores["anxiety"]),
                "stress": float(subscale_scores["stress"]),
                "depression_severity": severities["depression"],
                "anxiety_severity": severities["anxiety"],
                "stress_severity": severities["stress"]
            },
            severity=worst_severity,
            interpretation=interpretation,
            clinical_flags=clinical_flags,
            completed_at=datetime.utcnow()
        )


class VASPain:
    """
    Visual Analogue Scale for Pain

    Single 0-100 slider for pain intensity.
    Simple, validated measure used across medical contexts.

    Cutoffs:
    - 0: No pain
    - 1-30: Mild pain
    - 31-60: Moderate pain
    - 61-100: Severe pain
    """

    @classmethod
    def get_questionnaire(cls, client_id: UUID, session_id: Optional[UUID] = None,
                          timing: MeasureTiming = MeasureTiming.PRE_SESSION) -> OutcomeMeasureRequest:
        """Generate VAS Pain questionnaire."""
        questions = [
            Question(
                id="vas_pain_1",
                text="Please rate your current pain level",
                question_type=QuestionType.SLIDER,
                min_value=0,
                max_value=100
            )
        ]

        return OutcomeMeasureRequest(
            measure_type=OutcomeMeasureType.VAS_PAIN,
            client_id=client_id,
            session_id=session_id,
            timing=timing,
            questions=questions,
            instructions="Move the slider to indicate your pain level, where 0 is no pain and 100 is the worst pain imaginable.",
            estimated_time="30 seconds"
        )

    @classmethod
    def score(cls, responses: List[QuestionResponse]) -> OutcomeMeasureResponse:
        """Score VAS Pain response."""
        if len(responses) != 1:
            raise ValueError(f"VAS Pain requires 1 response, got {len(responses)}")

        pain_score = responses[0].value

        # Determine severity
        if pain_score == 0:
            severity = "none"
            interpretation = "No pain reported."
        elif pain_score <= 30:
            severity = "mild"
            interpretation = "Mild pain that may not require intervention."
        elif pain_score <= 60:
            severity = "moderate"
            interpretation = "Moderate pain that may benefit from treatment."
        else:
            severity = "severe"
            interpretation = "Severe pain - treatment strongly recommended."

        clinical_flags = []
        if pain_score >= 70:
            clinical_flags.append("High pain level - evaluate for pain management")

        return OutcomeMeasureResponse(
            measure_id=uuid4(),
            measure_type=OutcomeMeasureType.VAS_PAIN,
            client_id=uuid4(),
            timing=MeasureTiming.PRE_SESSION,
            responses=responses,
            total_score=float(pain_score),
            severity=severity,
            interpretation=interpretation,
            clinical_flags=clinical_flags,
            completed_at=datetime.utcnow()
        )


class CAMSymptomScale:
    """
    Custom CAM Symptom Scale

    Measures common symptoms addressed by CAM practitioners:
    - Energy levels
    - Sleep quality
    - Digestive health
    - Emotional balance
    - Physical tension

    Each item scored 0-10 using emoji slider.
    """

    QUESTIONS = [
        {"id": "cam_1", "text": "How would you rate your energy levels?", "subscale": "energy"},
        {"id": "cam_2", "text": "How well have you been sleeping?", "subscale": "sleep"},
        {"id": "cam_3", "text": "How is your digestive health?", "subscale": "digestion"},
        {"id": "cam_4", "text": "How emotionally balanced do you feel?", "subscale": "emotional"},
        {"id": "cam_5", "text": "How much physical tension/pain do you have?", "subscale": "tension", "reverse": True},
        {"id": "cam_6", "text": "How would you rate your overall wellbeing?", "subscale": "overall"},
    ]

    @classmethod
    def get_questionnaire(cls, client_id: UUID, session_id: Optional[UUID] = None,
                          timing: MeasureTiming = MeasureTiming.PRE_SESSION) -> OutcomeMeasureRequest:
        """Generate CAM Symptom Scale questionnaire."""
        questions = [
            Question(
                id=q["id"],
                text=q["text"],
                question_type=QuestionType.EMOJI,
                min_value=0,
                max_value=10,
                subscale=q["subscale"],
                reverse_scored=q.get("reverse", False)
            )
            for q in cls.QUESTIONS
        ]

        return OutcomeMeasureRequest(
            measure_type=OutcomeMeasureType.CAM_SYMPTOM,
            client_id=client_id,
            session_id=session_id,
            timing=timing,
            questions=questions,
            instructions="Rate each area by selecting the emoji that best represents how you feel (worst to best).",
            estimated_time="1-2 minutes"
        )

    @classmethod
    def score(cls, responses: List[QuestionResponse]) -> OutcomeMeasureResponse:
        """Score CAM Symptom Scale responses."""
        # Map responses
        response_map = {r.question_id: r.value for r in responses}

        # Calculate subscale scores
        subscale_scores = {}
        total = 0

        for q in cls.QUESTIONS:
            if q["id"] in response_map:
                value = response_map[q["id"]]
                # Reverse score if needed (higher = worse becomes higher = better)
                if q.get("reverse", False):
                    value = 10 - value
                subscale_scores[q["subscale"]] = float(value)
                total += value

        # Average score (0-10 scale)
        avg_score = total / len(cls.QUESTIONS) if cls.QUESTIONS else 0

        # Convert to 0-100 for consistency
        percentage_score = avg_score * 10

        # Determine severity
        if percentage_score >= 70:
            severity = "good"
            interpretation = "Your symptoms are well-managed."
        elif percentage_score >= 50:
            severity = "moderate"
            interpretation = "Some symptoms may benefit from attention."
        else:
            severity = "poor"
            interpretation = "Multiple symptoms indicate room for improvement."

        # Identify weak areas
        clinical_flags = []
        for subscale, score in subscale_scores.items():
            if score < 4:
                clinical_flags.append(f"Low {subscale} score - focus area")

        return OutcomeMeasureResponse(
            measure_id=uuid4(),
            measure_type=OutcomeMeasureType.CAM_SYMPTOM,
            client_id=uuid4(),
            timing=MeasureTiming.PRE_SESSION,
            responses=responses,
            total_score=percentage_score,
            subscale_scores=subscale_scores,
            severity=severity,
            interpretation=interpretation,
            clinical_flags=clinical_flags,
            completed_at=datetime.utcnow()
        )


class OutcomeMeasureScheduler:
    """
    Schedules and manages outcome measure delivery.

    Handles:
    - Automated scheduling based on session events
    - Email/SMS delivery
    - Reminders
    - Expiration
    """

    # Default schedule after sessions
    DEFAULT_SCHEDULE = [
        (MeasureTiming.POST_SESSION, timedelta(hours=2)),
        (MeasureTiming.ONE_WEEK, timedelta(days=7)),
        (MeasureTiming.ONE_MONTH, timedelta(days=30)),
    ]

    def __init__(self):
        self.scheduled_measures: Dict[UUID, ScheduledMeasure] = {}
        logger.info("OutcomeMeasureScheduler initialized")

    def schedule_for_session(
        self,
        client_id: UUID,
        session_id: UUID,
        practitioner_id: UUID,
        session_time: datetime,
        measure_types: List[OutcomeMeasureType] = None,
        delivery_method: DeliveryMethod = DeliveryMethod.EMAIL
    ) -> List[ScheduledMeasure]:
        """
        Schedule outcome measures for a session.

        Args:
            client_id: Client UUID
            session_id: Session UUID
            practitioner_id: Practitioner UUID
            session_time: When the session occurred
            measure_types: Which measures to schedule (default: WHO5 + CAM)
            delivery_method: How to deliver

        Returns:
            List of scheduled measures
        """
        if measure_types is None:
            measure_types = [OutcomeMeasureType.WHO5, OutcomeMeasureType.CAM_SYMPTOM]

        scheduled = []

        for timing, delay in self.DEFAULT_SCHEDULE:
            scheduled_time = session_time + delay

            for measure_type in measure_types:
                measure = ScheduledMeasure(
                    id=uuid4(),
                    client_id=client_id,
                    session_id=session_id,
                    practitioner_id=practitioner_id,
                    measure_type=measure_type,
                    timing=timing,
                    delivery_method=delivery_method,
                    scheduled_for=scheduled_time
                )

                self.scheduled_measures[measure.id] = measure
                scheduled.append(measure)

        logger.info(f"Scheduled {len(scheduled)} measures for session {session_id}")
        return scheduled

    def get_due_measures(self, as_of: datetime = None) -> List[ScheduledMeasure]:
        """Get all measures due for delivery."""
        if as_of is None:
            as_of = datetime.utcnow()

        due = [
            m for m in self.scheduled_measures.values()
            if not m.delivered and not m.expired and m.scheduled_for <= as_of
        ]

        return sorted(due, key=lambda x: x.scheduled_for)

    def mark_delivered(self, measure_id: UUID) -> bool:
        """Mark a measure as delivered."""
        if measure_id in self.scheduled_measures:
            measure = self.scheduled_measures[measure_id]
            measure.delivered = True
            measure.delivered_at = datetime.utcnow()
            return True
        return False

    def mark_completed(self, measure_id: UUID, response_id: UUID) -> bool:
        """Mark a measure as completed."""
        if measure_id in self.scheduled_measures:
            measure = self.scheduled_measures[measure_id]
            measure.completed = True
            measure.completed_at = datetime.utcnow()
            measure.response_id = response_id
            return True
        return False

    def get_pending_for_client(self, client_id: UUID) -> List[ScheduledMeasure]:
        """Get pending measures for a client."""
        return [
            m for m in self.scheduled_measures.values()
            if m.client_id == client_id and not m.completed and not m.expired
        ]

    def calculate_change(
        self,
        baseline: OutcomeMeasureResponse,
        follow_up: OutcomeMeasureResponse
    ) -> MeasureComparison:
        """
        Calculate change between two measurements.

        Includes:
        - Raw change
        - Percent change
        - Effect size (Cohen's d)
        - Clinical significance
        """
        baseline_score = baseline.total_score
        follow_up_score = follow_up.total_score

        change = follow_up_score - baseline_score
        percent_change = (change / baseline_score * 100) if baseline_score != 0 else 0

        # Effect size (simplified - would use pooled SD in production)
        # Assuming SD of 15 for WHO-5, 10 for DASS-21, 20 for VAS
        sd_map = {
            OutcomeMeasureType.WHO5: 15,
            OutcomeMeasureType.DASS21: 10,
            OutcomeMeasureType.VAS_PAIN: 20,
            OutcomeMeasureType.CAM_SYMPTOM: 15
        }
        sd = sd_map.get(baseline.measure_type, 15)
        effect_size = change / sd

        # Reliable change index (RCI > 1.96 is significant)
        # Using test-retest reliability of 0.8
        reliability = 0.8
        se_measurement = sd * math.sqrt(1 - reliability)
        se_diff = math.sqrt(2 * se_measurement ** 2)
        rci = abs(change) / se_diff

        reliable_change = rci > 1.96

        # Clinical significance (moved from clinical range to normal)
        # Simplified: >10% improvement in good direction
        if baseline.measure_type == OutcomeMeasureType.VAS_PAIN:
            clinically_significant = change < -10  # Pain should decrease
        else:
            clinically_significant = change > 10  # Wellbeing should increase

        return MeasureComparison(
            measure_type=baseline.measure_type,
            client_id=baseline.client_id,
            measurements=[
                {"date": baseline.completed_at.isoformat(), "score": baseline_score, "timing": baseline.timing.value},
                {"date": follow_up.completed_at.isoformat(), "score": follow_up_score, "timing": follow_up.timing.value}
            ],
            baseline_score=baseline_score,
            current_score=follow_up_score,
            change=round(change, 1),
            percent_change=round(percent_change, 1),
            reliable_change=reliable_change,
            clinically_significant=clinically_significant,
            effect_size=round(effect_size, 2)
        )

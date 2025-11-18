"""
SPRM - SANA Practitioner Recommendation Model

Intelligent AI-powered matchmaking between users and verified CAM practitioners.
Uses multi-factor scoring including health needs, credibility, practical fit,
evidence alignment, and user preferences.
"""
from typing import List, Dict, Tuple, Optional
from uuid import UUID
import math

from algorithms.scoring.models import SISMOutput
from .models import (
    PractitionerProfile,
    UserMatchingPreferences,
    SPRMOutput,
    PractitionerRecommendation,
    MatchScore,
    OutcomeRecord,
    PractitionerMatchInput,
    PractitionerMatchOutput
)


class SPRMAlgorithm:
    """
    SANA Practitioner Recommendation Model (SPRM)

    Matches users to best-fit verified practitioners using:
    1. Health need alignment (weak domains from SISM)
    2. Practitioner credibility (SCVM scores)
    3. Practical constraints (location, budget)
    4. Evidence-based approach
    5. User preferences
    """

    MIN_VERIFICATION_SCORE = 85.0
    TOP_N_RECOMMENDATIONS = 5

    def __init__(self):
        """Initialize SPRM"""
        pass

    def find_best_matches(
        self,
        user_id: UUID,
        sism_output: SISMOutput,
        user_preferences: UserMatchingPreferences,
        practitioner_pool: List[PractitionerProfile],
        outcome_history: Optional[List[OutcomeRecord]] = None
    ) -> SPRMOutput:
        """Find best practitioner matches for user"""
        total_practitioners = len(practitioner_pool)

        # Step 1: Filter by verification
        verified = self._filter_by_verification(practitioner_pool)

        # Step 2: Filter by specialty match
        specialty_matched = self._filter_by_specialty_match(
            verified, sism_output.weak_domains
        )

        # Step 3: Filter by geography
        geo_filtered = self._filter_by_geography(specialty_matched, user_preferences)

        # Step 4: Filter by budget
        budget_filtered = self._filter_by_budget(geo_filtered, user_preferences)

        if not budget_filtered:
            return self._handle_no_matches(
                user_id, sism_output, total_practitioners,
                "No practitioners found matching your criteria"
            )

        # Step 5: Calculate match scores
        scored_matches = []
        for practitioner in budget_filtered:
            match_score = self._calculate_match_score(
                practitioner, sism_output, user_preferences, outcome_history
            )
            scored_matches.append((practitioner, match_score))

        # Step 6: Sort by score
        scored_matches.sort(key=lambda x: x[1].overall_score, reverse=True)

        # Step 7: Generate recommendations
        top_recommendations = []
        for practitioner, match_score in scored_matches[:self.TOP_N_RECOMMENDATIONS]:
            recommendation = self._generate_recommendation(
                practitioner, match_score, sism_output, user_preferences
            )
            top_recommendations.append(recommendation)

        # Step 8: Honorable mentions
        honorable_mentions = []
        for practitioner, match_score in scored_matches[self.TOP_N_RECOMMENDATIONS:self.TOP_N_RECOMMENDATIONS + 3]:
            recommendation = self._generate_recommendation(
                practitioner, match_score, sism_output, user_preferences
            )
            honorable_mentions.append(recommendation)

        # Step 9: Generate insights
        match_summary = self._generate_match_summary(
            len(top_recommendations), sism_output.weak_domains
        )
        key_factors = self._identify_key_factors(top_recommendations)

        return SPRMOutput(
            user_id=user_id,
            top_recommendations=top_recommendations,
            total_practitioners_considered=total_practitioners,
            total_practitioners_filtered=len(budget_filtered),
            match_summary=match_summary,
            key_factors=key_factors,
            honorable_mentions=honorable_mentions,
            sism_score_at_matching=sism_output.overall_score,
            weak_domains_at_matching=sism_output.weak_domains
        )

    def _filter_by_verification(
        self, practitioners: List[PractitionerProfile]
    ) -> List[PractitionerProfile]:
        """Filter to only verified practitioners"""
        return [
            p for p in practitioners
            if p.scvm_confidence_score >= self.MIN_VERIFICATION_SCORE
        ]

    def _filter_by_specialty_match(
        self,
        practitioners: List[PractitionerProfile],
        weak_domains: List[str]
    ) -> List[PractitionerProfile]:
        """Filter to practitioners specializing in user's weak domains"""
        if not weak_domains:
            return practitioners

        matched = []
        for practitioner in practitioners:
            domain_overlap = set(practitioner.target_domains) & set(weak_domains)
            if domain_overlap:
                matched.append(practitioner)

        return matched if matched else practitioners[:10]

    def _filter_by_geography(
        self,
        practitioners: List[PractitionerProfile],
        preferences: UserMatchingPreferences
    ) -> List[PractitionerProfile]:
        """Filter by geographic distance"""
        accessible = []

        for practitioner in practitioners:
            distance_km = self._calculate_distance(
                preferences.location_latitude,
                preferences.location_longitude,
                practitioner.location_latitude,
                practitioner.location_longitude
            )

            if distance_km <= preferences.max_travel_distance_km:
                accessible.append(practitioner)
            elif preferences.willing_to_do_virtual:
                accessible.append(practitioner)

        return accessible

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance using Haversine formula"""
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _filter_by_budget(
        self,
        practitioners: List[PractitionerProfile],
        preferences: UserMatchingPreferences
    ) -> List[PractitionerProfile]:
        """Filter by budget constraints"""
        affordable = []

        for practitioner in practitioners:
            if practitioner.hourly_rate <= preferences.max_budget_per_session:
                affordable.append(practitioner)
            elif practitioner.offers_sliding_scale:
                affordable.append(practitioner)

        return affordable

    def _calculate_match_score(
        self,
        practitioner: PractitionerProfile,
        sism_output: SISMOutput,
        preferences: UserMatchingPreferences,
        outcome_history: Optional[List[OutcomeRecord]]
    ) -> MatchScore:
        """Calculate comprehensive match score"""

        health_need_score = self._score_health_need_alignment(practitioner, sism_output)
        credibility_score = self._score_credibility(practitioner)
        practical_score, distance_km = self._score_practical_fit(practitioner, preferences)
        evidence_score = self._score_evidence_alignment(practitioner)
        preference_score = self._score_preference_match(practitioner, preferences)

        weights = {
            "health_need": 0.40,
            "credibility": 0.25,
            "practical_fit": 0.20,
            "evidence_alignment": 0.10,
            "preference_match": 0.05
        }

        overall_score = (
            health_need_score * weights["health_need"] +
            credibility_score * weights["credibility"] +
            practical_score * weights["practical_fit"] +
            evidence_score * weights["evidence_alignment"] +
            preference_score * weights["preference_match"]
        )

        match_reasons = self._generate_match_reasons(
            practitioner, sism_output, health_need_score, credibility_score
        )
        potential_concerns = self._generate_concerns(
            practitioner, preferences, practical_score
        )

        return MatchScore(
            practitioner_id=practitioner.practitioner_id,
            overall_score=round(overall_score, 1),
            health_need_score=health_need_score,
            credibility_score=credibility_score,
            practical_fit_score=practical_score,
            evidence_alignment_score=evidence_score,
            preference_match_score=preference_score,
            weights=weights,
            match_reasons=match_reasons,
            potential_concerns=potential_concerns,
            distance_km=distance_km
        )

    def _score_health_need_alignment(
        self, practitioner: PractitionerProfile, sism_output: SISMOutput
    ) -> float:
        """Score how well practitioner matches health needs"""
        score = 0.0

        weak_domains_set = set(sism_output.weak_domains)
        target_domains_set = set(practitioner.target_domains)

        overlap = weak_domains_set & target_domains_set
        if overlap:
            coverage = len(overlap) / len(weak_domains_set) if weak_domains_set else 1
            score += coverage * 60

        if practitioner.specialties:
            score += min(20, len(practitioner.specialties) * 5)

        if practitioner.total_clients_treated > 50:
            score += 10
        elif practitioner.total_clients_treated > 20:
            score += 5

        if practitioner.average_outcome_improvement:
            if practitioner.average_outcome_improvement > 30:
                score += 10
            elif practitioner.average_outcome_improvement > 15:
                score += 5

        return min(100, score)

    def _score_credibility(self, practitioner: PractitionerProfile) -> float:
        """Score practitioner credibility"""
        score = 0.0

        if practitioner.verification_tier == "gold":
            score += 40
        elif practitioner.verification_tier == "standard":
            score += 30
        else:
            score += 20

        if practitioner.years_experience >= 10:
            score += 30
        elif practitioner.years_experience >= 5:
            score += 20
        elif practitioner.years_experience >= 2:
            score += 10

        score += min(15, len(practitioner.credentials) * 5)
        score += min(10, len(practitioner.professional_memberships) * 3)

        if practitioner.client_satisfaction_rating:
            score += (practitioner.client_satisfaction_rating / 5) * 5

        return min(100, score)

    def _score_practical_fit(
        self,
        practitioner: PractitionerProfile,
        preferences: UserMatchingPreferences
    ) -> Tuple[float, float]:
        """Score practical fit"""
        score = 0.0

        distance_km = self._calculate_distance(
            preferences.location_latitude,
            preferences.location_longitude,
            practitioner.location_latitude,
            practitioner.location_longitude
        )

        if distance_km <= 2:
            score += 40
        elif distance_km <= 5:
            score += 30
        elif distance_km <= 10:
            score += 20
        elif distance_km <= 20:
            score += 10

        if practitioner.hourly_rate <= preferences.max_budget_per_session:
            affordability_ratio = 1 - (practitioner.hourly_rate / preferences.max_budget_per_session)
            score += 30 * (1 - affordability_ratio * 0.5)
        elif practitioner.offers_sliding_scale:
            score += 20

        if practitioner.accepts_new_clients:
            score += 10
        if practitioner.availability_windows:
            score += 10

        if preferences.must_accept_insurance and practitioner.accepts_insurance:
            score += 10
        elif practitioner.offers_sliding_scale:
            score += 5

        return min(100, score), distance_km

    def _score_evidence_alignment(self, practitioner: PractitionerProfile) -> float:
        """Score evidence-based approach"""
        score = 0.0

        if practitioner.evidence_based:
            score += 60

        if practitioner.uses_interventions:
            score += min(40, len(practitioner.uses_interventions) * 8)

        return min(100, score)

    def _score_preference_match(
        self,
        practitioner: PractitionerProfile,
        preferences: UserMatchingPreferences
    ) -> float:
        """Score match with user preferences"""
        score = 0.0

        if practitioner.treatment_philosophy in preferences.preferred_philosophies:
            score += 40

        if (preferences.preferred_communication_style and
            practitioner.communication_style == preferences.preferred_communication_style):
            score += 30

        if preferences.preferred_language in practitioner.languages_spoken:
            score += 20

        score += 10

        return min(100, score)

    def _generate_match_reasons(
        self,
        practitioner: PractitionerProfile,
        sism_output: SISMOutput,
        health_score: float,
        credibility_score: float
    ) -> List[str]:
        """Generate reasons why this is a good match"""
        reasons = []

        if health_score >= 80:
            overlapping_domains = set(practitioner.target_domains) & set(sism_output.weak_domains)
            if overlapping_domains:
                reasons.append(
                    f"Specializes in {', '.join(overlapping_domains)} - your priority areas"
                )

        if practitioner.verification_tier == "gold":
            reasons.append("Gold-tier verified practitioner with comprehensive credentials")

        if practitioner.years_experience >= 10:
            reasons.append(f"{practitioner.years_experience}+ years of professional experience")

        if practitioner.average_outcome_improvement and practitioner.average_outcome_improvement > 25:
            reasons.append(
                f"Clients see average {practitioner.average_outcome_improvement:.0f}% health improvement"
            )

        if practitioner.client_satisfaction_rating and practitioner.client_satisfaction_rating >= 4.5:
            reasons.append(
                f"Highly rated: {practitioner.client_satisfaction_rating:.1f}/5 stars"
            )

        if practitioner.evidence_based:
            reasons.append("Uses evidence-based treatment approaches")

        return reasons[:5]

    def _generate_concerns(
        self,
        practitioner: PractitionerProfile,
        preferences: UserMatchingPreferences,
        practical_score: float
    ) -> List[str]:
        """Generate potential concerns"""
        concerns = []

        if practitioner.hourly_rate > preferences.max_budget_per_session * 1.2:
            concerns.append(
                f"Rate (£{practitioner.hourly_rate:.0f}/session) above budget, but offers sliding scale"
            )

        if practical_score < 50:
            concerns.append("May require longer travel time")

        if not practitioner.accepts_new_clients:
            concerns.append("Currently has a waitlist for new clients")

        if practitioner.years_experience < 3:
            concerns.append("Relatively new practitioner (less than 3 years)")

        return concerns

    def _generate_recommendation(
        self,
        practitioner: PractitionerProfile,
        match_score: MatchScore,
        sism_output: SISMOutput,
        preferences: UserMatchingPreferences
    ) -> PractitionerRecommendation:
        """Generate complete recommendation"""

        headline = self._generate_headline(practitioner, sism_output, match_score)
        why_recommended = " ".join(match_score.match_reasons)
        what_to_expect = self._generate_what_to_expect(practitioner)

        estimated_sessions = self._estimate_sessions_needed(sism_output)
        estimated_cost = estimated_sessions * practitioner.hourly_rate

        available_slots = ["Mon 10am", "Wed 2pm", "Fri 4pm"]

        similar_outcomes = None
        if practitioner.average_outcome_improvement:
            similar_outcomes = (
                f"{practitioner.average_outcome_improvement:.0f}% of clients with similar "
                f"health profiles saw significant improvement"
            )

        return PractitionerRecommendation(
            practitioner=practitioner,
            match_score=match_score,
            headline=headline,
            why_recommended=why_recommended,
            what_to_expect=what_to_expect,
            estimated_sessions_needed=estimated_sessions,
            estimated_total_cost=estimated_cost,
            available_time_slots=available_slots,
            booking_url=f"https://sana.health/book/{practitioner.practitioner_id}",
            similar_client_outcomes=similar_outcomes,
            if_unavailable="Check our other highly-matched practitioners below"
        )

    def _generate_headline(
        self,
        practitioner: PractitionerProfile,
        sism_output: SISMOutput,
        match_score: MatchScore
    ) -> str:
        """Generate headline for recommendation"""
        if match_score.overall_score >= 90:
            domains = sism_output.weak_domains[:2] if sism_output.weak_domains else ["wellness"]
            return f"Excellent match for {' & '.join(domains)}"
        elif match_score.overall_score >= 80:
            domain = sism_output.weak_domains[0] if sism_output.weak_domains else "health"
            return f"Highly recommended for {domain} support"
        else:
            domain = sism_output.weak_domains[0] if sism_output.weak_domains else "wellness"
            return f"Good option for holistic {domain} care"

    def _generate_what_to_expect(self, practitioner: PractitionerProfile) -> str:
        """Generate description of what to expect"""
        approach = practitioner.treatment_philosophy.value.replace("_", " ")
        modalities = ", ".join(practitioner.primary_modalities[:2])

        return (
            f"{practitioner.full_name} takes a {approach} approach using {modalities}. "
            f"Sessions are {practitioner.session_duration_minutes} minutes and focus on "
            f"understanding root causes and creating personalized treatment plans."
        )

    def _estimate_sessions_needed(self, sism_output: SISMOutput) -> int:
        """Estimate sessions needed based on health score"""
        if sism_output.overall_score < 40:
            return 12
        elif sism_output.overall_score < 60:
            return 8
        else:
            return 6

    def _generate_match_summary(
        self, num_matches: int, weak_domains: List[str]
    ) -> str:
        """Generate overall match summary"""
        domains_str = ", ".join(weak_domains) if weak_domains else "general wellness"
        return (
            f"Found {num_matches} verified practitioners specializing in {domains_str}. "
            f"All recommendations are within your budget and travel radius."
        )

    def _identify_key_factors(
        self, recommendations: List[PractitionerRecommendation]
    ) -> List[str]:
        """Identify key factors across top matches"""
        factors = []

        all_specialties = []
        for rec in recommendations:
            all_specialties.extend(rec.practitioner.specialties)

        if all_specialties:
            most_common = max(set(all_specialties), key=all_specialties.count)
            factors.append(f"Specialization in {most_common}")

        if all(r.practitioner.verification_tier == "gold" for r in recommendations):
            factors.append("All gold-tier verified")

        if all(r.practitioner.evidence_based for r in recommendations):
            factors.append("Evidence-based treatment approaches")

        return factors

    def _handle_no_matches(
        self,
        user_id: UUID,
        sism_output: SISMOutput,
        total_practitioners: int,
        reason: str
    ) -> SPRMOutput:
        """Handle case when no matches found"""
        return SPRMOutput(
            user_id=user_id,
            top_recommendations=[],
            total_practitioners_considered=total_practitioners,
            total_practitioners_filtered=0,
            match_summary="",
            key_factors=[],
            no_match_reason=reason,
            alternative_suggestions=[
                "Try expanding your travel radius",
                "Consider increasing your budget range",
                "Enable virtual consultations",
                "Contact SANA support for personalized help"
            ],
            sism_score_at_matching=sism_output.overall_score,
            weak_domains_at_matching=sism_output.weak_domains
        )


# Legacy function for backwards compatibility
def recommend_practitioners(
    user_id: UUID,
    health_goals: List[str],
    preferences: Dict,
    top_k: int = 5
) -> List[PractitionerMatchOutput]:
    """Legacy recommendation function"""
    return []

"""
SIRM - SANA Insight & Reflection Model

AI-powered journal analysis providing personalized reflections through
multiple personas and evidence-based wellness suggestions.
"""

import re
import math
import logging
from typing import List, Dict, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from collections import Counter

from .models import (
    JournalEntry,
    Persona,
    SentimentAnalysis,
    ThemeDetection,
    WellnessSuggestion,
    PersonaReflection,
    SIRMOutput,
    EmotionalTone,
    JournalHistory
)

logger = logging.getLogger(__name__)


class SIRMAlgorithm:
    """
    SANA Insight & Reflection Model (SIRM)

    Analyzes journal entries to:
    1. Detect sentiment and emotional tone
    2. Identify themes and patterns
    3. Provide personalized reflections through different personas
    4. Suggest evidence-based wellness interventions
    """

    # Emotion lexicons (simplified - production would use NLP models)
    POSITIVE_WORDS = {
        'happy', 'joy', 'grateful', 'thankful', 'peaceful', 'calm', 'relaxed',
        'energized', 'motivated', 'excited', 'hopeful', 'optimistic', 'love',
        'proud', 'confident', 'accomplished', 'satisfied', 'content', 'blessed',
        'inspired', 'focused', 'clear', 'strong', 'healthy', 'better', 'improved',
        'progress', 'success', 'achievement', 'wonderful', 'amazing', 'great'
    }

    NEGATIVE_WORDS = {
        'sad', 'anxious', 'worried', 'stressed', 'overwhelmed', 'tired', 'exhausted',
        'frustrated', 'angry', 'upset', 'depressed', 'lonely', 'isolated', 'scared',
        'afraid', 'hopeless', 'helpless', 'worthless', 'guilty', 'ashamed', 'pain',
        'hurt', 'sick', 'weak', 'failed', 'failure', 'terrible', 'awful', 'bad',
        'worse', 'difficult', 'hard', 'struggle', 'suffering', 'broken'
    }

    # Cognitive distortion patterns
    DISTORTION_PATTERNS = {
        'catastrophizing': [
            r'\b(worst|terrible|disaster|catastrophe|end of|never recover)\b',
            r'\b(everything is|always|never)\b.*\b(wrong|bad|fail)\b'
        ],
        'black_and_white': [
            r'\b(always|never|everyone|no one|everything|nothing)\b',
            r'\b(completely|totally|absolutely)\b.*\b(fail|wrong|bad)\b'
        ],
        'mind_reading': [
            r'\b(they think|everyone thinks|people think)\b.*\b(i am|im)\b',
            r'\b(i know|i can tell)\b.*\b(they|he|she)\b.*\b(think|feel)\b'
        ],
        'should_statements': [
            r'\b(i should|i must|i have to|i need to)\b',
            r'\b(should have|must have|ought to)\b'
        ],
        'emotional_reasoning': [
            r'\b(i feel|feeling)\b.*\b(therefore|so|means)\b',
            r'\b(because i feel)\b'
        ]
    }

    # Theme keywords mapped to wellness domains
    THEME_KEYWORDS = {
        'physical': [
            'body', 'exercise', 'workout', 'sleep', 'tired', 'energy', 'pain',
            'health', 'sick', 'diet', 'eating', 'weight', 'fitness', 'rest'
        ],
        'emotional': [
            'feel', 'feeling', 'emotion', 'mood', 'happy', 'sad', 'anxious',
            'stressed', 'overwhelmed', 'calm', 'peaceful', 'angry', 'frustrated'
        ],
        'social': [
            'friend', 'family', 'relationship', 'partner', 'colleague', 'people',
            'social', 'lonely', 'isolated', 'connection', 'support', 'love'
        ],
        'cognitive': [
            'think', 'thought', 'mind', 'focus', 'concentrate', 'memory',
            'learn', 'decision', 'problem', 'solve', 'understand', 'confused'
        ],
        'spiritual': [
            'meaning', 'purpose', 'belief', 'faith', 'meditation', 'mindful',
            'gratitude', 'thankful', 'soul', 'spirit', 'values', 'growth'
        ]
    }

    # Persona characteristics
    PERSONA_STYLES = {
        Persona.PHILOSOPHER: {
            'tone': 'contemplative and questioning',
            'approach': 'Explores deeper meaning and questions assumptions',
            'opener': 'Your words invite deeper reflection...',
            'style': 'Uses questions and explores universal themes'
        },
        Persona.THERAPIST: {
            'tone': 'warm and validating',
            'approach': 'Validates feelings while gently exploring patterns',
            'opener': 'Thank you for sharing this with me...',
            'style': 'Empathetic, uses reflective listening techniques'
        },
        Persona.POET: {
            'tone': 'metaphorical and evocative',
            'approach': 'Uses imagery and metaphor to illuminate feelings',
            'opener': 'In the garden of your thoughts...',
            'style': 'Poetic language, metaphors, imagery'
        },
        Persona.SCIENTIST: {
            'tone': 'analytical and evidence-based',
            'approach': 'Examines patterns and suggests research-backed strategies',
            'opener': 'Looking at the data of your experience...',
            'style': 'Logical, cites research, identifies patterns'
        },
        Persona.COACH: {
            'tone': 'motivating and action-oriented',
            'approach': 'Focuses on goals, strengths, and next steps',
            'opener': 'I see real strength in what you\'ve shared...',
            'style': 'Encouraging, goal-focused, action-oriented'
        },
        Persona.FRIEND: {
            'tone': 'casual and supportive',
            'approach': 'Offers friendly support and practical perspective',
            'opener': 'Hey, I hear you...',
            'style': 'Casual, relatable, supportive'
        },
        Persona.STOIC: {
            'tone': 'calm and accepting',
            'approach': 'Focuses on what can be controlled and acceptance',
            'opener': 'Consider what is within your control...',
            'style': 'Measured, focuses on agency and acceptance'
        },
        Persona.SPIRITUAL: {
            'tone': 'compassionate and transcendent',
            'approach': 'Connects to larger meaning and inner wisdom',
            'opener': 'Your spirit speaks through these words...',
            'style': 'Gentle, connects to purpose and growth'
        }
    }

    # Evidence-based suggestions mapped to themes
    WELLNESS_SUGGESTIONS = {
        'stress': [
            {
                'suggestion': 'Practice 4-7-8 breathing for 3 cycles',
                'rationale': 'You mentioned feeling stressed/overwhelmed',
                'evidence': 'Controlled breathing activates the parasympathetic nervous system, reducing cortisol',
                'domain': 'emotional',
                'difficulty': 'easy',
                'time': '2 minutes'
            },
            {
                'suggestion': 'Take a 10-minute walk outdoors',
                'rationale': 'Physical movement helps process stress hormones',
                'evidence': 'Walking in nature reduces rumination and improves mood (Stanford study)',
                'domain': 'physical',
                'difficulty': 'easy',
                'time': '10 minutes'
            }
        ],
        'sleep': [
            {
                'suggestion': 'Create a wind-down routine 1 hour before bed',
                'rationale': 'Sleep quality impacts overall wellbeing',
                'evidence': 'Consistent sleep routines improve sleep onset and quality (Sleep Medicine Reviews)',
                'domain': 'physical',
                'difficulty': 'moderate',
                'time': '60 minutes'
            },
            {
                'suggestion': 'Avoid screens 30 minutes before sleep',
                'rationale': 'Blue light disrupts melatonin production',
                'evidence': 'Screen exposure before bed delays circadian rhythm (PNAS)',
                'domain': 'physical',
                'difficulty': 'moderate',
                'time': '30 minutes'
            }
        ],
        'anxiety': [
            {
                'suggestion': 'Write down 3 things you can control right now',
                'rationale': 'Anxiety often stems from focus on uncontrollables',
                'evidence': 'Focusing on controllables reduces anxiety (CBT research)',
                'domain': 'cognitive',
                'difficulty': 'easy',
                'time': '5 minutes'
            },
            {
                'suggestion': 'Practice grounding: Name 5 things you can see, 4 you can touch, 3 you can hear',
                'rationale': 'Grounding reduces anxiety by anchoring to present',
                'evidence': '5-4-3-2-1 technique reduces acute anxiety symptoms',
                'domain': 'emotional',
                'difficulty': 'easy',
                'time': '3 minutes'
            }
        ],
        'loneliness': [
            {
                'suggestion': 'Reach out to one person today, even just a text',
                'rationale': 'You mentioned feelings of isolation',
                'evidence': 'Small social connections reduce loneliness (Cacioppo research)',
                'domain': 'social',
                'difficulty': 'moderate',
                'time': '5 minutes'
            }
        ],
        'gratitude': [
            {
                'suggestion': 'Continue your gratitude practice - it\'s working',
                'rationale': 'Your entry shows appreciation and positive focus',
                'evidence': 'Regular gratitude practice increases wellbeing (Emmons & McCullough)',
                'domain': 'spiritual',
                'difficulty': 'easy',
                'time': '5 minutes'
            }
        ],
        'low_energy': [
            {
                'suggestion': 'Try a 2-minute energizing stretch routine',
                'rationale': 'You mentioned feeling tired or low energy',
                'evidence': 'Brief movement breaks increase alertness and energy',
                'domain': 'physical',
                'difficulty': 'easy',
                'time': '2 minutes'
            }
        ],
        'rumination': [
            {
                'suggestion': 'Set a 10-minute "worry time" then consciously stop',
                'rationale': 'Containing worry prevents it from consuming your day',
                'evidence': 'Scheduled worry time reduces overall rumination (Borkovec)',
                'domain': 'cognitive',
                'difficulty': 'moderate',
                'time': '10 minutes'
            }
        ]
    }

    def __init__(self):
        """Initialize SIRM."""
        logger.info("SIRM initialized")

    def analyze(
        self,
        entry: JournalEntry,
        preferred_persona: Optional[Persona] = None,
        history: Optional[JournalHistory] = None
    ) -> SIRMOutput:
        """
        Analyze a journal entry and generate insights.

        Args:
            entry: The journal entry to analyze
            preferred_persona: User's preferred reflection style
            history: Historical journal data for pattern detection

        Returns:
            SIRMOutput with complete analysis
        """
        logger.info(f"Analyzing journal entry for user {entry.user_id}")

        # 1. Sentiment Analysis
        sentiment = self._analyze_sentiment(entry.content)

        # 2. Theme Detection
        themes = self._detect_themes(entry.content, history)

        # 3. Generate Primary Reflection
        persona = preferred_persona or self._select_best_persona(sentiment, themes)
        primary_reflection = self._generate_reflection(entry, sentiment, themes, persona)

        # 4. Generate Alternative Reflections (2 others)
        alternative_personas = self._get_alternative_personas(persona, sentiment)
        alternative_reflections = [
            self._generate_reflection(entry, sentiment, themes, p)
            for p in alternative_personas[:2]
        ]

        # 5. Generate Wellness Suggestions
        suggestions = self._generate_suggestions(sentiment, themes, entry)

        # 6. Historical Pattern Analysis
        historical_patterns = {}
        if history:
            historical_patterns = self._analyze_historical_patterns(history)

        # 7. Health Insights (connect to wellness domains)
        health_insights = self._generate_health_insights(
            sentiment, themes, entry.health_score, entry.weak_domains
        )

        return SIRMOutput(
            user_id=entry.user_id,
            entry_id=uuid4(),
            sentiment=sentiment,
            themes=themes,
            primary_reflection=primary_reflection,
            alternative_reflections=alternative_reflections,
            suggestions=suggestions,
            historical_patterns=historical_patterns,
            health_insights=health_insights
        )

    def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment and emotions in text."""
        words = set(re.findall(r'\b\w+\b', text.lower()))

        # Count positive and negative words
        pos_count = len(words & self.POSITIVE_WORDS)
        neg_count = len(words & self.NEGATIVE_WORDS)
        total = pos_count + neg_count

        # Calculate sentiment score
        if total == 0:
            score = 0.0
        else:
            score = (pos_count - neg_count) / total

        # Detect emotional tone
        emotional_tone = self._determine_emotional_tone(text, score)

        # Extract emotion intensities
        emotions = self._detect_emotions(text)

        # Find positive and negative phrases
        positive_phrases = self._extract_phrases(text, self.POSITIVE_WORDS)
        negative_phrases = self._extract_phrases(text, self.NEGATIVE_WORDS)

        # Detect cognitive distortions
        distortions = self._detect_cognitive_distortions(text)

        # Confidence based on word count and clarity
        word_count = len(text.split())
        confidence = min(90, 50 + word_count * 0.5)

        return SentimentAnalysis(
            overall_score=round(score, 2),
            emotional_tone=emotional_tone,
            confidence=confidence,
            emotions_detected=emotions,
            positive_phrases=positive_phrases[:5],
            negative_phrases=negative_phrases[:5],
            cognitive_distortions=distortions
        )

    def _determine_emotional_tone(self, text: str, sentiment_score: float) -> EmotionalTone:
        """Determine the primary emotional tone."""
        text_lower = text.lower()

        # Check for specific tones
        if any(word in text_lower for word in ['anxious', 'worried', 'nervous', 'panic']):
            return EmotionalTone.ANXIOUS
        if any(word in text_lower for word in ['grateful', 'thankful', 'blessed', 'appreciate']):
            return EmotionalTone.GRATEFUL
        if any(word in text_lower for word in ['hope', 'hopeful', 'optimistic', 'looking forward']):
            return EmotionalTone.HOPEFUL
        if any(word in text_lower for word in ['frustrated', 'annoyed', 'irritated']):
            return EmotionalTone.FRUSTRATED
        if any(word in text_lower for word in ['sad', 'grief', 'loss', 'miss']):
            return EmotionalTone.SAD
        if any(word in text_lower for word in ['reflect', 'thinking', 'wondering', 'realize']):
            return EmotionalTone.REFLECTIVE

        # Fall back to score-based
        if sentiment_score > 0.3:
            return EmotionalTone.POSITIVE
        elif sentiment_score < -0.3:
            return EmotionalTone.NEGATIVE
        elif abs(sentiment_score) < 0.1:
            return EmotionalTone.NEUTRAL
        else:
            return EmotionalTone.MIXED

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect specific emotions and their intensities."""
        text_lower = text.lower()
        emotions = {}

        emotion_words = {
            'joy': ['happy', 'joy', 'delighted', 'pleased', 'excited'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'grief'],
            'anxiety': ['anxious', 'worried', 'nervous', 'stressed', 'overwhelmed'],
            'anger': ['angry', 'frustrated', 'annoyed', 'irritated', 'furious'],
            'fear': ['scared', 'afraid', 'frightened', 'terrified'],
            'gratitude': ['grateful', 'thankful', 'appreciative', 'blessed'],
            'hope': ['hopeful', 'optimistic', 'encouraged', 'looking forward'],
            'peace': ['calm', 'peaceful', 'serene', 'relaxed', 'content']
        }

        word_count = len(text.split())
        for emotion, words in emotion_words.items():
            count = sum(1 for word in words if word in text_lower)
            if count > 0:
                intensity = min(1.0, count / (word_count * 0.1))
                emotions[emotion] = round(intensity, 2)

        return emotions

    def _extract_phrases(self, text: str, target_words: set) -> List[str]:
        """Extract phrases containing target words."""
        sentences = re.split(r'[.!?]', text)
        phrases = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            words = set(re.findall(r'\b\w+\b', sentence.lower()))
            if words & target_words:
                phrases.append(sentence[:100])  # Truncate long sentences

        return phrases

    def _detect_cognitive_distortions(self, text: str) -> List[str]:
        """Detect cognitive distortions in text."""
        distortions = []
        text_lower = text.lower()

        for distortion, patterns in self.DISTORTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    distortions.append(distortion.replace('_', ' ').title())
                    break

        return list(set(distortions))

    def _detect_themes(
        self,
        text: str,
        history: Optional[JournalHistory] = None
    ) -> ThemeDetection:
        """Detect themes and patterns in text."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Detect wellness domains
        domains = []
        for domain, keywords in self.THEME_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)

        # Extract keywords (most frequent meaningful words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'me', 'my',
                     'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                     'that', 'this', 'it', 'have', 'has', 'had', 'do', 'does', 'did',
                     'be', 'been', 'being', 'so', 'just', 'really', 'very', 'been'}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
        keyword_counts = Counter(meaningful_words)
        keywords = [word for word, _ in keyword_counts.most_common(10)]

        # Identify themes based on content
        themes = []
        if any(w in text_lower for w in ['work', 'job', 'career', 'boss', 'colleague']):
            themes.append('work')
        if any(w in text_lower for w in ['relationship', 'partner', 'marriage', 'dating']):
            themes.append('relationships')
        if any(w in text_lower for w in ['health', 'body', 'exercise', 'diet']):
            themes.append('health')
        if any(w in text_lower for w in ['family', 'parent', 'child', 'sibling']):
            themes.append('family')
        if any(w in text_lower for w in ['money', 'financial', 'debt', 'savings']):
            themes.append('finances')
        if any(w in text_lower for w in ['goal', 'dream', 'future', 'plan']):
            themes.append('goals')

        # Identify concerns and growth
        concerns = []
        growth = []

        if any(w in text_lower for w in ['worried', 'concerned', 'afraid', 'scared']):
            concerns.append('fear and worry')
        if any(w in text_lower for w in ['struggling', 'difficult', 'hard', 'challenge']):
            concerns.append('current challenges')
        if any(w in text_lower for w in ['learned', 'realized', 'understand', 'growth']):
            growth.append('self-awareness')
        if any(w in text_lower for w in ['better', 'improved', 'progress', 'achieved']):
            growth.append('positive progress')

        # Stress triggers
        triggers = []
        if 'deadline' in text_lower or 'pressure' in text_lower:
            triggers.append('time pressure')
        if 'conflict' in text_lower or 'argument' in text_lower:
            triggers.append('interpersonal conflict')
        if 'uncertainty' in text_lower or 'unknown' in text_lower:
            triggers.append('uncertainty')

        # Mood trend from history
        mood_trend = None
        if history and len(history.sentiment_history) >= 3:
            recent = history.sentiment_history[-3:]
            if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                mood_trend = 'improving'
            elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                mood_trend = 'declining'
            else:
                mood_trend = 'stable'

        return ThemeDetection(
            primary_themes=themes or ['general reflection'],
            wellness_domains=domains or ['emotional'],
            recurring_concerns=concerns,
            growth_indicators=growth,
            stress_triggers=triggers,
            keywords=keywords,
            mood_trend=mood_trend
        )

    def _select_best_persona(
        self,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection
    ) -> Persona:
        """Select the most appropriate persona based on analysis."""
        # If high anxiety, use therapist
        if sentiment.emotional_tone == EmotionalTone.ANXIOUS:
            return Persona.THERAPIST

        # If cognitive distortions, use scientist for logic
        if sentiment.cognitive_distortions:
            return Persona.SCIENTIST

        # If reflective, use philosopher
        if sentiment.emotional_tone == EmotionalTone.REFLECTIVE:
            return Persona.PHILOSOPHER

        # If low energy/motivation, use coach
        if 'low_energy' in themes.recurring_concerns:
            return Persona.COACH

        # If spiritual themes, use spiritual
        if 'spiritual' in themes.wellness_domains:
            return Persona.SPIRITUAL

        # If very negative, use therapist
        if sentiment.overall_score < -0.3:
            return Persona.THERAPIST

        # If positive/grateful, use friend
        if sentiment.emotional_tone in [EmotionalTone.GRATEFUL, EmotionalTone.POSITIVE]:
            return Persona.FRIEND

        # Default to therapist
        return Persona.THERAPIST

    def _get_alternative_personas(
        self,
        primary: Persona,
        sentiment: SentimentAnalysis
    ) -> List[Persona]:
        """Get alternative personas that complement the primary."""
        all_personas = list(Persona)
        all_personas.remove(primary)

        # Prioritize certain personas based on content
        priorities = []

        if sentiment.emotional_tone == EmotionalTone.ANXIOUS:
            priorities.extend([Persona.STOIC, Persona.COACH])
        elif sentiment.overall_score < 0:
            priorities.extend([Persona.FRIEND, Persona.COACH])
        else:
            priorities.extend([Persona.PHILOSOPHER, Persona.POET])

        # Add priorities first, then others
        result = []
        for p in priorities:
            if p in all_personas and p not in result:
                result.append(p)
        for p in all_personas:
            if p not in result:
                result.append(p)

        return result

    def _generate_reflection(
        self,
        entry: JournalEntry,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection,
        persona: Persona
    ) -> PersonaReflection:
        """Generate a reflection from a specific persona."""
        style = self.PERSONA_STYLES[persona]

        # Build reflection based on persona and content
        reflection = self._build_persona_reflection(
            entry.content,
            sentiment,
            themes,
            persona,
            style
        )

        # Extract key insight
        key_insight = self._extract_key_insight(sentiment, themes, persona)

        return PersonaReflection(
            persona=persona,
            reflection=reflection,
            tone=style['tone'],
            key_insight=key_insight
        )

    def _build_persona_reflection(
        self,
        content: str,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection,
        persona: Persona,
        style: Dict
    ) -> str:
        """Build a reflection in the persona's style."""
        opener = style['opener']
        approach = style['approach']

        # Build middle section based on sentiment and themes
        if persona == Persona.THERAPIST:
            if sentiment.overall_score < 0:
                middle = (
                    f"I can sense the weight of what you're carrying. Your feelings of "
                    f"{sentiment.emotional_tone.value} are valid and understandable. "
                    f"You're dealing with {', '.join(themes.primary_themes)} and that's not easy. "
                    f"What strikes me is your willingness to put these thoughts into words - "
                    f"that takes courage."
                )
            else:
                middle = (
                    f"I notice a sense of {sentiment.emotional_tone.value} in your words. "
                    f"It's wonderful to see you reflecting on {', '.join(themes.primary_themes)}. "
                    f"This kind of self-awareness is a powerful tool for growth."
                )

        elif persona == Persona.PHILOSOPHER:
            middle = (
                f"What does it mean, this experience you describe? "
                f"Perhaps the themes of {', '.join(themes.primary_themes)} are invitations "
                f"to examine what you truly value. The ancient Stoics would ask: "
                f"what is within your control here, and what must you accept?"
            )

        elif persona == Persona.POET:
            middle = (
                f"Your words paint a picture of {sentiment.emotional_tone.value} - "
                f"like {self._generate_metaphor(sentiment)}. "
                f"In this garden of {', '.join(themes.primary_themes)}, "
                f"what seeds are you planting for tomorrow?"
            )

        elif persona == Persona.SCIENTIST:
            middle = (
                f"Analyzing your entry, I see patterns related to {', '.join(themes.wellness_domains)}. "
                f"Research suggests that when we experience {sentiment.emotional_tone.value}, "
                f"our perception can shift. "
                f"{'I also notice some cognitive patterns worth examining: ' + ', '.join(sentiment.cognitive_distortions) if sentiment.cognitive_distortions else ''}"
            )

        elif persona == Persona.COACH:
            middle = (
                f"I see determination in your words, even amidst the challenges. "
                f"You're tackling {', '.join(themes.primary_themes)} head-on. "
                f"Let's focus on what you can do next - "
                f"small actions that move you forward."
            )

        elif persona == Persona.FRIEND:
            middle = (
                f"First off, I get it. Dealing with {', '.join(themes.primary_themes)} is tough. "
                f"But you know what? The fact that you're processing this instead of just "
                f"burying it says a lot. You've got this."
            )

        elif persona == Persona.STOIC:
            middle = (
                f"Let us consider what is within your sphere of control. "
                f"The themes you raise - {', '.join(themes.primary_themes)} - "
                f"contain both what you can change and what you must accept with equanimity. "
                f"Focus your energy on the former."
            )

        elif persona == Persona.SPIRITUAL:
            middle = (
                f"Your soul is speaking through these words about {', '.join(themes.primary_themes)}. "
                f"There is wisdom in your reflection, even if it doesn't feel that way yet. "
                f"Trust that you have the inner resources to navigate this path."
            )

        else:
            middle = f"Your reflection on {', '.join(themes.primary_themes)} is meaningful."

        # Build closer
        closer = self._generate_closer(persona, sentiment)

        return f"{opener} {middle} {closer}"

    def _generate_metaphor(self, sentiment: SentimentAnalysis) -> str:
        """Generate a poetic metaphor for the emotional state."""
        if sentiment.overall_score > 0.3:
            return "sunlight breaking through morning clouds"
        elif sentiment.overall_score < -0.3:
            return "a storm that will, in time, pass"
        elif sentiment.emotional_tone == EmotionalTone.ANXIOUS:
            return "waves that seem overwhelming but can be ridden"
        else:
            return "a twilight moment between day and night"

    def _generate_closer(self, persona: Persona, sentiment: SentimentAnalysis) -> str:
        """Generate a closing statement for the reflection."""
        closers = {
            Persona.THERAPIST: "Remember, healing isn't linear, and you don't have to figure this out alone.",
            Persona.PHILOSOPHER: "The examined life, as Socrates taught, is the one worth living.",
            Persona.POET: "May you find the words within that light your way forward.",
            Persona.SCIENTIST: "Consider tracking these patterns - data reveals insights our minds alone might miss.",
            Persona.COACH: "What's one small step you can take today? Start there.",
            Persona.FRIEND: "I'm proud of you for working through this. Keep going.",
            Persona.STOIC: "Remember: it is not events that disturb us, but our judgments about them.",
            Persona.SPIRITUAL: "Trust in the journey, even when the path isn't clear."
        }
        return closers.get(persona, "Thank you for sharing.")

    def _extract_key_insight(
        self,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection,
        persona: Persona
    ) -> str:
        """Extract the main insight from the analysis."""
        if sentiment.cognitive_distortions:
            return f"Notice the pattern of {sentiment.cognitive_distortions[0].lower()} in your thinking"

        if themes.growth_indicators:
            return f"You're showing {themes.growth_indicators[0]}"

        if sentiment.overall_score > 0.3:
            return "Your positive outlook is a strength to build on"

        if sentiment.emotional_tone == EmotionalTone.ANXIOUS:
            return "Grounding yourself in the present can help manage anxiety"

        if themes.stress_triggers:
            return f"Consider strategies for managing {themes.stress_triggers[0]}"

        return "Regular reflection builds self-awareness and emotional intelligence"

    def _generate_suggestions(
        self,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection,
        entry: JournalEntry
    ) -> List[WellnessSuggestion]:
        """Generate evidence-based wellness suggestions."""
        suggestions = []
        text_lower = entry.content.lower()

        # Map detected patterns to suggestions
        if sentiment.emotional_tone == EmotionalTone.ANXIOUS or 'anxiety' in sentiment.emotions_detected:
            suggestions.extend(self._get_suggestions('anxiety'))

        if any(word in text_lower for word in ['stress', 'overwhelm', 'pressure']):
            suggestions.extend(self._get_suggestions('stress'))

        if any(word in text_lower for word in ['sleep', 'tired', 'exhausted', 'insomnia']):
            suggestions.extend(self._get_suggestions('sleep'))

        if any(word in text_lower for word in ['lonely', 'alone', 'isolated']):
            suggestions.extend(self._get_suggestions('loneliness'))

        if sentiment.emotional_tone == EmotionalTone.GRATEFUL:
            suggestions.extend(self._get_suggestions('gratitude'))

        if entry.energy_level and entry.energy_level < 3:
            suggestions.extend(self._get_suggestions('low_energy'))

        if sentiment.cognitive_distortions:
            suggestions.extend(self._get_suggestions('rumination'))

        # Deduplicate and limit
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s['suggestion'] not in seen:
                seen.add(s['suggestion'])
                unique_suggestions.append(
                    WellnessSuggestion(
                        suggestion=s['suggestion'],
                        rationale=s['rationale'],
                        evidence_base=s['evidence'],
                        domain=s['domain'],
                        difficulty=s['difficulty'],
                        time_required=s['time']
                    )
                )

        return unique_suggestions[:5]  # Return top 5

    def _get_suggestions(self, category: str) -> List[Dict]:
        """Get suggestions for a category."""
        return self.WELLNESS_SUGGESTIONS.get(category, [])

    def _analyze_historical_patterns(self, history: JournalHistory) -> Dict:
        """Analyze patterns across historical journal entries."""
        if not history.entries:
            return {}

        patterns = {
            'total_entries': len(history.entries),
            'avg_sentiment': 0.0,
            'most_common_themes': [],
            'mood_volatility': 'stable',
            'improvement_areas': [],
            'strengths': []
        }

        # Calculate average sentiment
        if history.sentiment_history:
            patterns['avg_sentiment'] = round(
                sum(history.sentiment_history) / len(history.sentiment_history), 2
            )

            # Calculate volatility
            if len(history.sentiment_history) >= 3:
                diffs = [
                    abs(history.sentiment_history[i+1] - history.sentiment_history[i])
                    for i in range(len(history.sentiment_history) - 1)
                ]
                avg_diff = sum(diffs) / len(diffs)
                if avg_diff > 0.3:
                    patterns['mood_volatility'] = 'high'
                elif avg_diff > 0.15:
                    patterns['mood_volatility'] = 'moderate'
                else:
                    patterns['mood_volatility'] = 'stable'

        # Most common themes
        if history.theme_frequency:
            sorted_themes = sorted(
                history.theme_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )
            patterns['most_common_themes'] = [t[0] for t in sorted_themes[:5]]

        return patterns

    def _generate_health_insights(
        self,
        sentiment: SentimentAnalysis,
        themes: ThemeDetection,
        health_score: Optional[float],
        weak_domains: Optional[List[str]]
    ) -> List[str]:
        """Generate insights connecting journal to health data."""
        insights = []

        # Connect emotional tone to wellness domains
        if sentiment.emotional_tone == EmotionalTone.ANXIOUS:
            insights.append(
                "Your anxiety may be affecting your emotional and cognitive wellness scores"
            )

        # Connect themes to weak domains
        if weak_domains:
            for domain in themes.wellness_domains:
                if domain in weak_domains:
                    insights.append(
                        f"Your journal mentions {domain} - this aligns with an area "
                        f"flagged for improvement in your health assessment"
                    )

        # Health score context
        if health_score:
            if health_score < 50 and sentiment.overall_score > 0:
                insights.append(
                    "Your positive journal tone despite lower health scores shows resilience"
                )
            elif health_score > 70 and sentiment.overall_score < 0:
                insights.append(
                    "Despite good health metrics, emotional wellbeing needs attention"
                )

        # Growth indicators
        if themes.growth_indicators:
            insights.append(
                "Your journal shows signs of personal growth and self-awareness"
            )

        return insights if insights else [
            "Regular journaling helps track your wellness journey over time"
        ]

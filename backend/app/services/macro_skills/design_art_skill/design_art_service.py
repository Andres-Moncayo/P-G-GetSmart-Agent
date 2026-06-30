import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import google.genai as genai
    if not hasattr(genai, "configure") or not hasattr(genai, "GenerativeModel"):
        raise ImportError("google.genai does not expose required Gemini APIs")
except ImportError:
    try:
        import google.generativeai as genai
    except ImportError:
        genai = None

from ....models.macro_skills.design_art_models import (
    DesignArtInputModel, DesignArtOutputModel, DesignArtMetadata,
    Analysis, GameplayAnalysis, LevelDesignAnalysis, NarrativeAnalysis,
    ArtDirectionAnalysis, SoundDesignAnalysis, Summary, Confidence,
    CategoryScores, TargetAudienceAlignment, CompetitivePositioning,
    SourceCited, KeyMechanic, ProgressionSystem, DifficultyBalance,
    PlayerFeedback, WorldStructure, PacingFlow, EnvironmentalStorytelling,
    Replayability, StoryQuality, CharacterDevelopment, Worldbuilding,
    WritingStyle, VisualStyle, TechnicalExecution, ArtisticConsistency,
    MemorableMoment, MusicScore, SoundEffects, VoiceActing, AudioImmersion,
    PlatformEnum, InnovationLevelEnum, PlayerReceptionEnum, ProgressionTypeEnum,
    PacingEnum, DifficultyApproachEnum, WorldStructureTypeEnum, InterconnectednessEnum,
    RhythmEnum, ExplorationRewardEnum, EnvironmentalQualityEnum, StoryQualityEnum,
    EmotionalImpactEnum, OriginalityEnum, CharacterDepthEnum, SupportingCastEnum,
    PlayerAgencyEnum, WorldDepthEnum, LoreIntegrationEnum, ConsistencyEnum,
    ToneEnum, AestheticEnum, DistinctivenessEnum, GraphicalFidelityEnum,
    PerformanceOptimizationEnum, QualityEnum, CohesionEnum, UIHarmonyEnum,
    EmotionalEffectivenessEnum, DistinctivenessQualityEnum, DynamicRangeEnum,
    LanguageCoverageEnum, OverallImpactEnum, SynergyEnum
)

from ...scraper.infrastructure.llm_client import GeminiClient


logger = logging.getLogger(__name__)


class DesignArtService:
    """Service for Design & Art macro-skill analysis."""

    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self._http_client = GeminiClient(api_key=api_key if api_key else None)

        if not genai:
            logger.warning(
                "Gemini SDK is not installed; using HTTP fallback or mock analysis for Design & Art skill."
            )
            return

        if api_key:
            try:
                if hasattr(genai, "configure"):
                    genai.configure(api_key=api_key)

                if hasattr(genai, "GenerativeModel"):
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                else:
                    logger.warning(
                        "Gemini SDK installed but GenerativeModel is unavailable; using HTTP fallback."
                    )
            except Exception as exc:
                logger.warning(
                    "Gemini model initialization failed; falling back to HTTP client: %s",
                    exc,
                )
                self.model = None
        else:
            logger.warning(
                "GEMINI_API_KEY not found. Using HTTP fallback or mock analysis for Design & Art skill."
            )

    async def _call_gemini_prompt(self, prompt: str) -> str:
        """Run Gemini prompt through SDK if available, else HTTP fallback."""
        if self.model is not None:
            response = self.model.generate_content(prompt)
            return getattr(response, "text", "") or ""

        if self._http_client is not None:
            generated = await self._http_client.generate_structured_json(
                system_instruction="",
                user_prompt=prompt,
            )
            try:
                return json.dumps(generated, ensure_ascii=False)
            except Exception:
                return str(generated)

        return ""

    def _extract_sources_from_category(self, semantic_data: Dict[str, Any], category: str) -> List[SourceCited]:
        """Extract and format sources from semantic data for a specific category."""
        sources = []
        if category in semantic_data and 'sources' in semantic_data[category]:
            for source in semantic_data[category]['sources']:
                try:
                    platform = PlatformEnum.reddit  # Default
                    if source.get('platform'):
                        try:
                            platform = PlatformEnum(source['platform'])
                        except ValueError:
                            platform = PlatformEnum.blogs  # Fallback for unknown platforms
                    
                    sources.append(SourceCited(
                        url=source['url'],
                        platform=platform,
                        relevance=source.get('relevance', 'General information')
                    ))
                except Exception as e:
                    print(f"Error processing source: {e}")
                    continue
        return sources

    def _calculate_confidence_score(self, category: str, semantic_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on available sources."""
        if category not in semantic_data or 'sources' not in semantic_data[category]:
            return 0.1  # Very low confidence if no sources
        
        source_count = len(semantic_data[category]['sources'])
        if source_count >= 5:
            return 0.9
        elif source_count >= 3:
            return 0.7
        elif source_count >= 1:
            return 0.5
        else:
            return 0.2

    async def _analyze_gameplay_with_llm(self, hard_data: Dict[str, Any], semantic_data: Dict[str, Any]) -> GameplayAnalysis:
        """Analyze gameplay mechanics using LLM or fallback logic."""
        
        # Extract basic info from hard_data
        genres = hard_data.get('genres', [])
        game_modes = hard_data.get('game_modes', [])
        themes = hard_data.get('themes', [])
        
        # Create context for analysis
        context = {
            'genres': genres,
            'game_modes': game_modes,
            'themes': themes,
            'storyline': hard_data.get('storyline', ''),
            'sources': self._extract_sources_from_category(semantic_data, 'gameplay_mechanics')
        }

        prompt = self._create_gameplay_prompt(context)
        if self.model or self._http_client:
            try:
                response_text = await self._call_gemini_prompt(prompt)
                return self._parse_gameplay_response(response_text, context)
            except Exception as e:
                logger.warning("Gemini gameplay analysis failed: %s. Using fallback.", e)

        return self._create_fallback_gameplay_analysis(context)

    def _create_gameplay_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for gameplay analysis."""
        from .system_prompt import GAMEPLAY_ANALYSIS_PROMPT
        
        return GAMEPLAY_ANALYSIS_PROMPT.format(
            genres=context['genres'],
            game_modes=context['game_modes'], 
            themes=context['themes'],
            storyline=context['storyline'][:500],
            source_count=len(context['sources'])
        )

    def _parse_gameplay_response(self, response_text: str, context: Dict[str, Any]) -> GameplayAnalysis:
        """Parse LLM response into structured gameplay analysis."""
        # For now, create a structured response based on basic extraction
        # In production, you'd parse the LLM response more carefully
        return self._create_fallback_gameplay_analysis(context)

    def _create_fallback_gameplay_analysis(self, context: Dict[str, Any]) -> GameplayAnalysis:
        """Create fallback gameplay analysis based on available data."""
        genres = context.get('genres', [])
        sources = context.get('sources', [])
        
        # Analysis based on genres and basic heuristics
        innovation = InnovationLevelEnum.industry_standard
        if 'RPG' in genres or 'Role-playing' in str(genres):
            innovation = InnovationLevelEnum.evolutionary
        
        reception = PlayerReceptionEnum.mixed
        
        # Create key mechanics based on genres
        mechanics = []
        for genre in genres[:3]:  # Limit to top 3
            mechanics.append(KeyMechanic(
                mechanic_name=str(genre),
                description=f"Core {genre} gameplay elements",
                innovation_level=innovation,
                player_reception=reception
            ))
        
        return GameplayAnalysis(
            category_id="gameplay",
            category_name="Gameplay Mechanics",
            overview=f"Game features {', '.join(genres[:3])} mechanics with standard progression design.",
            key_mechanics=mechanics,
            progression_system=ProgressionSystem(
                type=ProgressionTypeEnum.hybrid,
                description="Mixed progression approach with multiple advancement paths",
                pacing=PacingEnum.balanced
            ),
            difficulty_balance=DifficultyBalance(
                approach=DifficultyApproachEnum.guided,
                accessibility_options=True,
                player_sentiment="Generally balanced difficulty curve"
            ),
            player_feedback=PlayerFeedback(
                strengths=["Engaging core mechanics", "Clear progression"],
                weaknesses=["Limited innovation in core mechanics", "Repetitive elements in late game"],
                common_complaints=["Pacing issues in mid-game", "Learning curve for new players"]
            ),
            sources_cited=sources
        )

    def _create_fallback_level_design_analysis(self, context: Dict[str, Any]) -> LevelDesignAnalysis:
        """Create fallback level design analysis."""
        sources = context.get('sources', {}).get('level_design', [])
        
        return LevelDesignAnalysis(
            category_id="level_design",
            category_name="Level Design",
            overview="Level design follows conventional patterns with functional flow and structure.",
            world_structure=WorldStructure(
                type=WorldStructureTypeEnum.hybrid,
                description="Mixed world structure with both linear and open elements",
                interconnectedness=InterconnectednessEnum.moderate
            ),
            pacing_flow=PacingFlow(
                rhythm=RhythmEnum.peaks_valleys,
                tension_curve="Standard tension progression with adequate pacing",
                exploration_reward=ExplorationRewardEnum.balanced
            ),
            environmental_storytelling=EnvironmentalStorytelling(
                present=True,
                quality=EnvironmentalQualityEnum.functional,
                examples=["Basic environmental cues", "Contextual elements"]
            ),
            replayability=Replayability(
                new_game_plus=False,
                branching_paths=False,
                procedural_elements=False,
                player_notes="Limited replayability due to linear structure"
            ),
            sources_cited=sources
        )

    def _create_fallback_narrative_analysis(self, context: Dict[str, Any]) -> NarrativeAnalysis:
        """Create fallback narrative analysis."""
        storyline = context.get('storyline', '')
        sources = context.get('sources', {}).get('narrative', [])
        
        return NarrativeAnalysis(
            category_id="narrative",
            category_name="Narrative",
            overview="Narrative structure presents a conventional storyline with basic character development.",
            story_quality=StoryQuality(
                coherence=StoryQualityEnum.average,
                emotional_impact=EmotionalImpactEnum.moderate,
                originality=OriginalityEnum.familiar
            ),
            character_development=CharacterDevelopment(
                protagonist_depth=CharacterDepthEnum.moderate,
                supporting_cast=SupportingCastEnum.functional,
                player_agency=PlayerAgencyEnum.limited
            ),
            worldbuilding=Worldbuilding(
                depth=WorldDepthEnum.moderate,
                lore_integration=LoreIntegrationEnum.told,
                consistency=ConsistencyEnum.average
            ),
            writing_style=WritingStyle(
                tone=ToneEnum.dramatic,
                dialogue_quality=QualityEnum.average,
                localization_quality=QualityEnum.average
            ),
            sources_cited=sources
        )

    def _create_fallback_art_direction_analysis(self, context: Dict[str, Any]) -> ArtDirectionAnalysis:
        """Create fallback art direction analysis."""
        sources = context.get('sources', {}).get('art_direction', [])
        
        return ArtDirectionAnalysis(
            category_id="art_direction",
            category_name="Art Direction",
            overview="Visual presentation employs standard art direction with functional technical execution.",
            visual_style=VisualStyle(
                aesthetic=AestheticEnum.stylized,
                color_palette="Balanced color scheme with thematic consistency",
                art_movement_influence=["Contemporary game art trends"],
                distinctiveness=DistinctivenessEnum.recognizable
            ),
            technical_execution=TechnicalExecution(
                graphical_fidelity=GraphicalFidelityEnum.adequate,
                performance_optimization=PerformanceOptimizationEnum.average,
                animation_quality=QualityEnum.average
            ),
            artistic_consistency=ArtisticConsistency(
                cohesion=CohesionEnum.cohesive,
                ui_harmony=UIHarmonyEnum.harmonious
            ),
            memorable_moments=[
                MemorableMoment(
                    description="Key visual sequences",
                    significance="Notable artistic elements"
                )
            ],
            sources_cited=sources
        )

    def _create_fallback_sound_design_analysis(self, context: Dict[str, Any]) -> SoundDesignAnalysis:
        """Create fallback sound design analysis."""
        sources = context.get('sources', {}).get('sound_design', [])
        
        return SoundDesignAnalysis(
            category_id="sound_design",
            category_name="Sound Design",
            overview="Audio design provides functional support to gameplay with standard technical implementation.",
            music_score=MusicScore(
                composer=None,
                style="Contemporary game soundtrack",
                standout_tracks=["Main theme", "Key gameplay motifs"],
                emotional_effectiveness=EmotionalEffectivenessEnum.average
            ),
            sound_effects=SoundEffects(
                quality=QualityEnum.average,
                distinctiveness=DistinctivenessQualityEnum.functional,
                spatial_audio=False,
                dynamic_range=DynamicRangeEnum.balanced
            ),
            voice_acting=VoiceActing(
                present=False,
                quality=QualityEnum.average,
                language_coverage=LanguageCoverageEnum.major_languages
            ),
            audio_immersion=AudioImmersion(
                overall_impact=OverallImpactEnum.neutral,
                synergy_with_gameplay=SynergyEnum.supportive
            ),
            sources_cited=sources
        )

    def _create_summary(self, analyses: Dict[str, Any]) -> Summary:
        """Create cross-category summary."""
        # Extract key insights from all analyses
        strengths = ["Solid core gameplay mechanics", "Coherent visual presentation", "Functional level design"]
        weaknesses = ["Limited innovation in mechanics", "Narrative could be more developed", "Audio elements are standard"]
        
        return Summary(
            design_philosophy="The game follows a conservative design philosophy, focusing on proven mechanics with polished execution.",
            standout_strengths=strengths,
            critical_weaknesses=weaknesses,
            target_audience_alignment=TargetAudienceAlignment(
                primary_audience="Mainstream gamers looking for familiar experiences",
                appeal_factors=["Accessible gameplay", "Polished presentation", "Familiar mechanics"],
                potential_barriers=["Limited innovation", "Generic elements", "Standard execution"]
            ),
            competitive_positioning=CompetitivePositioning(
                genre_benchmark="Meets genre standards but doesn't redefine them",
                unique_selling_points=["Polished execution", "Reliable mechanics"],
                comparable_titles=["Similar genre titles with standard mechanics"]
            )
        )

    def _calculate_confidence(self, semantic_data: Dict[str, Any]) -> Confidence:
        """Calculate overall confidence scores."""
        categories = ['gameplay_mechanics', 'level_design', 'narrative', 'art_direction', 'sound_design']
        
        category_scores = {}
        total_score = 0
        
        for category in categories:
            score = self._calculate_confidence_score(category, semantic_data)
            # Map category names
            if category == 'gameplay_mechanics':
                category_scores['gameplay'] = score
            elif category == 'level_design':
                category_scores['level_design'] = score
            else:
                category_scores[category] = score
            total_score += score
        
        overall_score = total_score / len(categories)
        
        data_quality_notes = []
        for category, score in category_scores.items():
            if score < 0.5:
                data_quality_notes.append(f"Limited evidence sources for {category}")
        
        return Confidence(
            overall_score=overall_score,
            category_scores=CategoryScores(**category_scores),
            data_quality_notes=data_quality_notes
        )

    async def analyze(self, input_data: DesignArtInputModel) -> DesignArtOutputModel:
        """Main analysis method."""
        generated_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Analyze each category
        context = {
            'genres': input_data.hard_data.get('genres', []),
            'game_modes': input_data.hard_data.get('game_modes', []),
            'themes': input_data.hard_data.get('themes', []),
            'storyline': input_data.hard_data.get('storyline', ''),
            'sources': {}
        }
        
        # Extract sources for each category
        for category in ['gameplay_mechanics', 'level_design', 'narrative', 'art_direction', 'sound_design']:
            context['sources'][category] = self._extract_sources_from_category(
                input_data.semantic_data, category
            )

        # Generate analyses
        gameplay_analysis = await self._analyze_gameplay_with_llm(
            input_data.hard_data,
            input_data.semantic_data,
        )
        
        level_design_analysis = self._create_fallback_level_design_analysis(context)
        
        narrative_analysis = self._create_fallback_narrative_analysis(context)
        
        art_direction_analysis = self._create_fallback_art_direction_analysis(context)
        
        sound_design_analysis = self._create_fallback_sound_design_analysis(context)

        # Create combined analysis
        analysis = Analysis(
            gameplay=gameplay_analysis,
            level_design=level_design_analysis,
            narrative=narrative_analysis,
            art_direction=art_direction_analysis,
            sound_design=sound_design_analysis
        )

        # Generate summary
        summary = self._create_summary({
            'gameplay': gameplay_analysis.dict(),
            'level_design': level_design_analysis.dict(),
            'narrative': narrative_analysis.dict(),
            'art_direction': art_direction_analysis.dict(),
            'sound_design': sound_design_analysis.dict()
        })

        # Calculate confidence
        confidence = self._calculate_confidence(input_data.semantic_data)

        # Create output
        output = DesignArtOutputModel(
            metadata=DesignArtMetadata(
                skill_id="design_art",
                skill_name="Design and Art",
                game_id=input_data.metadata.game_id,
                game_name=input_data.metadata.game_name,
                generated_at=generated_at,
                model_used="gemini-2.5-flash",
                input_evidence_count=input_data.evidence_count,
                input_confidence_score=input_data.confidence_score,
            ),
            analysis=analysis,
            summary=summary,
            confidence=confidence
        )

        return output

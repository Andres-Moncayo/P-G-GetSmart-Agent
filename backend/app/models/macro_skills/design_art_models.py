from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class PlatformEnum(str, Enum):
    reddit = "reddit"
    youtube = "youtube"
    blogs = "blogs"
    press = "press"
    steam_reviews = "steam_reviews"
    forums = "forums"


class InnovationLevelEnum(str, Enum):
    industry_standard = "industry_standard"
    evolutionary = "evolutionary"
    revolutionary = "revolutionary"


class PlayerReceptionEnum(str, Enum):
    negative = "negative"
    mixed = "mixed"
    positive = "positive"
    acclaimed = "acclaimed"


class ProgressionTypeEnum(str, Enum):
    linear = "linear"
    branching = "branching"
    open_ended = "open_ended"
    skill_tree = "skill_tree"
    hybrid = "hybrid"


class PacingEnum(str, Enum):
    too_slow = "too_slow"
    balanced = "balanced"
    too_fast = "too_fast"
    uneven = "uneven"


class DifficultyApproachEnum(str, Enum):
    handholding = "handholding"
    guided = "guided"
    challenging = "challenging"
    punishing = "punishing"
    adaptive = "adaptive"


class WorldStructureTypeEnum(str, Enum):
    linear = "linear"
    hub_based = "hub_based"
    open_world = "open_world"
    procedural = "procedural"
    hybrid = "hybrid"


class InterconnectednessEnum(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class RhythmEnum(str, Enum):
    constant = "constant"
    peaks_valleys = "peaks_valleys"
    player_driven = "player_driven"


class ExplorationRewardEnum(str, Enum):
    sparse = "sparse"
    balanced = "balanced"
    generous = "generous"
    overwhelming = "overwhelming"


class EnvironmentalQualityEnum(str, Enum):
    minimal = "minimal"
    functional = "functional"
    immersive = "immersive"
    masterful = "masterful"


class StoryQualityEnum(str, Enum):
    poor = "poor"
    average = "average"
    good = "good"
    excellent = "excellent"


class EmotionalImpactEnum(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    exceptional = "exceptional"


class OriginalityEnum(str, Enum):
    derivative = "derivative"
    familiar = "familiar"
    fresh = "fresh"
    groundbreaking = "groundbreaking"


class CharacterDepthEnum(str, Enum):
    shallow = "shallow"
    moderate = "moderate"
    deep = "deep"
    complex = "complex"


class SupportingCastEnum(str, Enum):
    forgettable = "forgettable"
    functional = "functional"
    memorable = "memorable"
    iconic = "iconic"


class PlayerAgencyEnum(str, Enum):
    none = "none"
    limited = "limited"
    meaningful = "meaningful"
    full = "full"


class WorldDepthEnum(str, Enum):
    surface = "surface"
    moderate = "moderate"
    deep = "deep"
    encyclopedic = "encyclopedic"


class LoreIntegrationEnum(str, Enum):
    told = "told"
    shown = "shown"
    environmental = "environmental"
    player_discovered = "player_discovered"


class ConsistencyEnum(str, Enum):
    poor = "poor"
    average = "average"
    good = "good"
    excellent = "excellent"


class ToneEnum(str, Enum):
    light = "light"
    dramatic = "dramatic"
    dark = "dark"
    humorous = "humorous"
    epic = "epic"


class AestheticEnum(str, Enum):
    realistic = "realistic"
    stylized = "stylized"
    cartoon = "cartoon"
    pixel_art = "pixel_art"
    minimalist = "minimalist"
    photorealistic = "photorealistic"
    other = "other"


class DistinctivenessEnum(str, Enum):
    generic = "generic"
    recognizable = "recognizable"
    iconic = "iconic"
    genre_defining = "genre_defining"


class GraphicalFidelityEnum(str, Enum):
    dated = "dated"
    adequate = "adequate"
    good = "good"
    cutting_edge = "cutting_edge"


class PerformanceOptimizationEnum(str, Enum):
    poor = "poor"
    average = "average"
    good = "good"
    excellent = "excellent"


class QualityEnum(str, Enum):
    poor = "poor"
    average = "average"
    good = "good"
    excellent = "excellent"


class CohesionEnum(str, Enum):
    fragmented = "fragmented"
    inconsistent = "inconsistent"
    cohesive = "cohesive"
    seamless = "seamless"


class UIHarmonyEnum(str, Enum):
    clashing = "clashing"
    neutral = "neutral"
    harmonious = "harmonious"


class EmotionalEffectivenessEnum(str, Enum):
    poor = "poor"
    average = "average"
    good = "good"
    excellent = "excellent"
    legendary = "legendary"


class DistinctivenessQualityEnum(str, Enum):
    generic = "generic"
    functional = "functional"
    distinctive = "distinctive"
    iconic = "iconic"


class DynamicRangeEnum(str, Enum):
    compressed = "compressed"
    balanced = "balanced"
    expansive = "expansive"


class LanguageCoverageEnum(str, Enum):
    limited = "limited"
    major_languages = "major_languages"
    extensive = "extensive"


class OverallImpactEnum(str, Enum):
    distracting = "distracting"
    neutral = "neutral"
    immersive = "immersive"
    transformative = "transformative"


class SynergyEnum(str, Enum):
    detracting = "detracting"
    neutral = "neutral"
    supportive = "supportive"
    enhancing = "enhancing"


class SemanticSource(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    snippet: Optional[str] = None
    platform: Optional[str] = None
    relevance: Optional[str] = None


class SemanticCategory(BaseModel):
    sources: List[SemanticSource] = Field(default_factory=list)


class MiniContextMetadata(BaseModel):
    game_id: str
    game_name: str
    macro_skill: Optional[str] = "Design and Art"
    worker_id: Optional[str] = "scraper_design_art"
    data_sources: Optional[List[str]] = Field(default_factory=list)


class DesignArtInputModel(BaseModel):
    metadata: MiniContextMetadata
    hard_data: Dict[str, Any] = Field(default_factory=dict)
    semantic_data: Dict[str, Any] = Field(default_factory=dict)
    evidence_count: int
    confidence_score: float


class SourceCited(BaseModel):
    url: HttpUrl
    platform: PlatformEnum
    relevance: str


class KeyMechanic(BaseModel):
    mechanic_name: str
    description: str
    innovation_level: InnovationLevelEnum
    player_reception: PlayerReceptionEnum


class ProgressionSystem(BaseModel):
    type: ProgressionTypeEnum
    description: str
    pacing: PacingEnum


class DifficultyBalance(BaseModel):
    approach: DifficultyApproachEnum
    accessibility_options: bool
    player_sentiment: str


class PlayerFeedback(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    common_complaints: List[str] = Field(default_factory=list)


class GameplayAnalysis(BaseModel):
    category_id: Literal["gameplay"]
    category_name: Literal["Gameplay Mechanics"]
    overview: str
    key_mechanics: List[KeyMechanic] = Field(default_factory=list)
    progression_system: ProgressionSystem
    difficulty_balance: DifficultyBalance
    player_feedback: PlayerFeedback
    sources_cited: List[SourceCited] = Field(default_factory=list)


class WorldStructure(BaseModel):
    type: WorldStructureTypeEnum
    description: str
    interconnectedness: InterconnectednessEnum


class PacingFlow(BaseModel):
    rhythm: RhythmEnum
    tension_curve: str
    exploration_reward: ExplorationRewardEnum


class EnvironmentalStorytelling(BaseModel):
    present: bool
    quality: EnvironmentalQualityEnum
    examples: List[str] = Field(default_factory=list)


class Replayability(BaseModel):
    new_game_plus: bool
    branching_paths: bool
    procedural_elements: bool
    player_notes: str


class LevelDesignAnalysis(BaseModel):
    category_id: Literal["level_design"]
    category_name: Literal["Level Design"]
    overview: str
    world_structure: WorldStructure
    pacing_flow: PacingFlow
    environmental_storytelling: EnvironmentalStorytelling
    replayability: Replayability
    sources_cited: List[SourceCited] = Field(default_factory=list)


class StoryQuality(BaseModel):
    coherence: StoryQualityEnum
    emotional_impact: EmotionalImpactEnum
    originality: OriginalityEnum


class CharacterDevelopment(BaseModel):
    protagonist_depth: CharacterDepthEnum
    supporting_cast: SupportingCastEnum
    player_agency: PlayerAgencyEnum


class Worldbuilding(BaseModel):
    depth: WorldDepthEnum
    lore_integration: LoreIntegrationEnum
    consistency: ConsistencyEnum


class WritingStyle(BaseModel):
    tone: ToneEnum
    dialogue_quality: QualityEnum
    localization_quality: QualityEnum


class NarrativeAnalysis(BaseModel):
    category_id: Literal["narrative"]
    category_name: Literal["Narrative"]
    overview: str
    story_quality: StoryQuality
    character_development: CharacterDevelopment
    worldbuilding: Worldbuilding
    writing_style: WritingStyle
    sources_cited: List[SourceCited] = Field(default_factory=list)


class VisualStyle(BaseModel):
    aesthetic: AestheticEnum
    color_palette: str
    art_movement_influence: List[str] = Field(default_factory=list)
    distinctiveness: DistinctivenessEnum


class TechnicalExecution(BaseModel):
    graphical_fidelity: GraphicalFidelityEnum
    performance_optimization: PerformanceOptimizationEnum
    animation_quality: QualityEnum


class ArtisticConsistency(BaseModel):
    cohesion: CohesionEnum
    ui_harmony: UIHarmonyEnum


class MemorableMoment(BaseModel):
    description: str
    significance: str


class ArtDirectionAnalysis(BaseModel):
    category_id: Literal["art_direction"]
    category_name: Literal["Art Direction"]
    overview: str
    visual_style: VisualStyle
    technical_execution: TechnicalExecution
    artistic_consistency: ArtisticConsistency
    memorable_moments: List[MemorableMoment] = Field(default_factory=list)
    sources_cited: List[SourceCited] = Field(default_factory=list)


class MusicScore(BaseModel):
    composer: Optional[str]
    style: str
    standout_tracks: List[str] = Field(default_factory=list)
    emotional_effectiveness: EmotionalEffectivenessEnum


class SoundEffects(BaseModel):
    quality: QualityEnum
    distinctiveness: DistinctivenessQualityEnum
    spatial_audio: bool
    dynamic_range: DynamicRangeEnum


class VoiceActing(BaseModel):
    present: bool
    quality: QualityEnum
    language_coverage: LanguageCoverageEnum


class AudioImmersion(BaseModel):
    overall_impact: OverallImpactEnum
    synergy_with_gameplay: SynergyEnum


class SoundDesignAnalysis(BaseModel):
    category_id: Literal["sound_design"]
    category_name: Literal["Sound Design"]
    overview: str
    music_score: MusicScore
    sound_effects: SoundEffects
    voice_acting: VoiceActing
    audio_immersion: AudioImmersion
    sources_cited: List[SourceCited] = Field(default_factory=list)


class Analysis(BaseModel):
    gameplay: GameplayAnalysis
    level_design: LevelDesignAnalysis
    narrative: NarrativeAnalysis
    art_direction: ArtDirectionAnalysis
    sound_design: SoundDesignAnalysis


class TargetAudienceAlignment(BaseModel):
    primary_audience: str
    appeal_factors: List[str] = Field(default_factory=list)
    potential_barriers: List[str] = Field(default_factory=list)


class CompetitivePositioning(BaseModel):
    genre_benchmark: str
    unique_selling_points: List[str] = Field(default_factory=list)
    comparable_titles: List[str] = Field(default_factory=list)


class Summary(BaseModel):
    design_philosophy: str
    standout_strengths: List[str] = Field(default_factory=list)
    critical_weaknesses: List[str] = Field(default_factory=list)
    target_audience_alignment: TargetAudienceAlignment
    competitive_positioning: CompetitivePositioning


class CategoryScores(BaseModel):
    gameplay: float = Field(ge=0.0, le=1.0)
    level_design: float = Field(ge=0.0, le=1.0)
    narrative: float = Field(ge=0.0, le=1.0)
    art_direction: float = Field(ge=0.0, le=1.0)
    sound_design: float = Field(ge=0.0, le=1.0)


class Confidence(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    category_scores: CategoryScores
    data_quality_notes: List[str] = Field(default_factory=list)


class DesignArtMetadata(BaseModel):
    skill_id: Literal["design_art"]
    skill_name: Literal["Design and Art"]
    game_id: str
    game_name: str
    generated_at: str
    model_used: Literal["gemini-2.5-flash"]
    input_evidence_count: int = Field(ge=0)
    input_confidence_score: float = Field(ge=0.0, le=1.0)


class DesignArtOutputModel(BaseModel):
    metadata: DesignArtMetadata
    analysis: Analysis
    summary: Summary
    confidence: Confidence
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "skill_id": "design_art",
                    "skill_name": "Design and Art",
                    "game_id": "00000000-0000-0000-0000-000000000000",
                    "game_name": "Example Game",
                    "generated_at": "2026-06-19T00:00:00Z",
                    "model_used": "gemini-2.5-flash",
                    "input_evidence_count": 0,
                    "input_confidence_score": 0.0,
                },
                "analysis": {},
                "summary": {},
                "confidence": {},
            }
        }
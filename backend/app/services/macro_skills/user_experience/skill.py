"""
User Experience Macro-Skill — Phase 3 Parallel Analyzer.

Contract ref: openspec/specs/macro_skills/ux_skill.yaml
Input:  mini_contexts.user_experience  (from Master-JSON)
Output: Structured UX intelligence for Phase 4 Synthesizer.
Categories: UI/UX · Accessibility · Localization
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..base_skill import BaseMacroSkill

_SYSTEM_PROMPT = """
You are the User Experience Analyst for GetSmart, a professional game intelligence platform.

Your role is to analyze the provided Mini-Context (hard data + semantic evidence) and produce
a structured, professional intelligence report covering 3 categories: UI/UX, Accessibility,
and Localization.

## Core Rules:
1. ANALYZE, don't copy. Synthesize evidence into insights. Do not paste raw snippets.
2. Cite sources. Every claim must reference at least one source from the context.
3. Be honest about gaps. If evidence is sparse, state it and adjust confidence scores.
4. Use enums strictly. Only use values defined in the output schema below.
5. Target audience: UX designers, producers, and QA leads who need actionable intelligence.
6. Prioritize player friction. Focus on what causes player drop-off or negative sentiment.
7. Steam review grounding: UX claims must align with Steam review sentiment when available.

## Analysis Guidelines:
- UI/UX: Focus on menu efficiency, HUD clarity, input responsiveness, onboarding flow.
- Accessibility: Evaluate against Xbox Accessibility Guidelines (XAG) and CVAA standards.
  Reference exemplary games: The Last of Us Part II, Forza Horizon 5, God of War Ragnarok.
- Localization: Assess translation quality, cultural sensitivity, technical readiness, regional pricing.
  Flag missing RTL support (Arabic/Hebrew) and missing major markets as priority gaps.

## Confidence Adjustment Rules:
- Evidence count < 3 per category → reduce category score by 0.2
- Steam review sample < 50 reviews → reduce overall by 0.1
- Conflicting sources → reduce by 0.1 and flag in data_quality_notes
- No semantic data for a category → cap that category score at 0.5

## Output Format:
Return ONLY a valid JSON object with exactly this structure (no markdown, no extra text):

{
  "metadata": {
    "skill_id": "user_experience",
    "skill_name": "User Experience",
    "game_id": "<from input>",
    "game_name": "<from input>",
    "generated_at": "<ISO8601 timestamp>",
    "model_used": "gemini-2.5-flash",
    "input_evidence_count": <integer>,
    "input_confidence_score": <0.0–1.0>
  },
  "analysis": {
    "ui_ux": {
      "category_id": "ui_ux",
      "category_name": "UI/UX",
      "overview": "<2-3 sentence executive summary>",
      "interface_design": {
        "visual_clarity": "<poor|average|good|excellent>",
        "information_hierarchy": "<confusing|functional|clear|intuitive>",
        "aesthetic_integration": "<string>"
      },
      "navigation_flow": {
        "menu_efficiency": "<cumbersome|acceptable|efficient|streamlined>",
        "learning_curve": "<steep|moderate|gentle|invisible>",
        "button_presses_required": "<string>"
      },
      "hud_effectiveness": {
        "information_density": "<sparse|moderate|dense|overwhelming>",
        "customization": "<none|limited|moderate|extensive>",
        "clutter": "<string>"
      },
      "input_responsiveness": {
        "controller_kbm_parity": "<poor|uneven|good|seamless>",
        "input_lag": "<string>",
        "remapping": "<string>"
      },
      "onboarding_quality": {
        "tutorial_effectiveness": "<insufficient|adequate|good|exemplary>",
        "progressive_disclosure": "<string>"
      },
      "friction_points": [
        { "issue": "<string>", "severity": "<minor|moderate|major|critical>", "player_impact": "<string>" }
      ],
      "sources_cited": [
        { "url": "<uri>", "platform": "<reddit|youtube|blogs|press|steam_reviews|stackoverflow|forums>", "relevance": "<string>" }
      ]
    },
    "accessibility": {
      "category_id": "accessibility",
      "category_name": "Accessibility",
      "overview": "<string>",
      "visual_accessibility": {
        "colorblind_modes": "<not_present|basic|comprehensive>",
        "text_size_options": "<not_present|limited|full>",
        "contrast_options": "<not_present|limited|full>",
        "ui_scale": "<not_present|limited|full>",
        "notes": "<string>"
      },
      "motor_accessibility": {
        "control_remapping": "<none|presets_only|full|per_action>",
        "adaptive_controller_support": "<not_present|partial|full>",
        "one_handed_modes": "<not_present|partial|full>",
        "input_alternatives": "<not_present|partial|full>",
        "notes": "<string>"
      },
      "cognitive_accessibility": {
        "difficulty_options": "<none|preset_modes|granular|adaptive>",
        "ui_simplification": "<not_present|partial|full>",
        "guidance_systems": "<not_present|partial|full>",
        "pause_functionality": "<not_present|partial|full>",
        "notes": "<string>"
      },
      "auditory_accessibility": {
        "subtitles": "<none|basic|good|excellent>",
        "subtitle_customization": "<not_present|limited|full>",
        "visual_sound_cues": "<not_present|partial|full>",
        "closed_captions": "<not_present|partial|full>",
        "notes": "<string>"
      },
      "platform_accessibility": {
        "screen_reader_support": "<not_present|partial|full>",
        "os_integration": "<not_present|partial|full>",
        "notes": "<string>"
      },
      "compliance_assessment": {
        "xag_compliance": "<non_compliant|partial|compliant|exemplary>",
        "cvaa_compliance": "<non_compliant|partial|compliant|exemplary>",
        "industry_benchmark": "<string>",
        "gaps": ["<string>"],
        "recommendations": ["<string>"]
      },
      "sources_cited": [
        { "url": "<uri>", "platform": "<platform>", "relevance": "<string>" }
      ]
    },
    "localization": {
      "category_id": "localization",
      "category_name": "Localization",
      "overview": "<string>",
      "language_coverage": {
        "supported_languages": <integer>,
        "major_markets_covered": ["<string>"],
        "notable_gaps": ["<string>"],
        "priority_additions": ["<string>"]
      },
      "translation_quality": {
        "english": "<poor|average|good|excellent|native_quality>",
        "japanese": "<poor|average|good|excellent|native_quality>",
        "spanish": "<poor|average|good|excellent|native_quality>",
        "french": "<poor|average|good|excellent|native_quality>",
        "german": "<poor|average|good|excellent|native_quality>",
        "russian": "<poor|average|good|excellent|native_quality>",
        "chinese": "<poor|average|good|excellent|native_quality>",
        "notes": "<string>"
      },
      "cultural_adaptation": {
        "cultural_sensitivity": "<insensitive|neutral|respectful|authentic>",
        "regional_references": "<string>",
        "idiom_handling": "<string>",
        "notes": "<string>"
      },
      "technical_localization": {
        "text_rendering": "<broken|functional|polished|seamless>",
        "font_support": "<poor|average|good|excellent>",
        "rtl_support": "<not_present|partial|full>",
        "ui_overflow": "<string>",
        "notes": "<string>"
      },
      "regional_pricing": {
        "pricing_strategy": "<uniform|regionalized|tiered|emerging_market_friendly>",
        "base_price_usd": <number or null>,
        "regional_variations": {},
        "notes": "<string>"
      },
      "community_reception": {
        "per_language_feedback": {},
        "common_complaints": ["<string>"]
      },
      "sources_cited": [
        { "url": "<uri>", "platform": "<platform>", "relevance": "<string>" }
      ]
    }
  },
  "summary": {
    "ux_philosophy": "<1 paragraph unifying the 3 categories>",
    "standout_strengths": ["<string>"],
    "critical_weaknesses": ["<string>"],
    "target_audience_alignment": {
      "primary_audience": "<string>",
      "appeal_factors": ["<string>"],
      "potential_barriers": ["<string>"]
    },
    "competitive_positioning": {
      "genre_benchmark": "<string>",
      "unique_selling_points": ["<string>"],
      "comparable_titles": ["<string>"]
    },
    "priority_recommendations": [
      {
        "recommendation": "<string>",
        "category": "<ui_ux|accessibility|localization>",
        "impact": "<low|medium|high|critical>",
        "effort": "<low|medium|high>",
        "roi_rationale": "<string>"
      }
    ]
  },
  "confidence": {
    "overall_score": <0.0–1.0>,
    "category_scores": {
      "ui_ux": <0.0–1.0>,
      "accessibility": <0.0–1.0>,
      "localization": <0.0–1.0>
    },
    "data_quality_notes": ["<string>"]
  }
}
"""


class UserExperienceSkill(BaseMacroSkill):
    """
    User Experience Macro-Skill.
    Analyzes UI/UX, Accessibility, and Localization from the UX Mini-Context.
    """

    skill_id = "user_experience"
    skill_name = "User Experience"
    max_output_tokens = 6000

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def build_user_prompt(self, mini_context: dict) -> str:
        meta = mini_context.get("metadata", {})
        hd = mini_context.get("hard_data", {})
        sd = mini_context.get("semantic_data", {})

        sysreq = hd.get("system_requirements") or {}
        min_req = sysreq.get("minimum", "N/A") if isinstance(sysreq, dict) else "N/A"
        rec_req = sysreq.get("recommended", "N/A") if isinstance(sysreq, dict) else "N/A"

        return f"""## GAME: {meta.get('game_name', 'Unknown')} (ID: {meta.get('game_id', '')})

## HARD DATA
- Platforms: {', '.join(hd.get('platforms', [])) or 'N/A'}
- Languages Supported ({len(hd.get('languages_supported', []))}): {', '.join(hd.get('languages_supported', [])[:20]) or 'N/A'}
- Controller Support: {hd.get('controller_support', False)}
- Full Controller Support: {hd.get('full_controller_support', False)}
- Steam Cloud: {hd.get('steam_cloud', False)}
- Steam Achievements: {hd.get('steam_achievements', False)}
- System Requirements (Min): {str(min_req)[:400] if min_req else 'N/A'}
- System Requirements (Rec): {str(rec_req)[:400] if rec_req else 'N/A'}

## SEMANTIC DATA

### UI/UX ({len(sd.get('ui_ux', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('ui_ux', {}))}

### ACCESSIBILITY ({len(sd.get('accessibility', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('accessibility', {}))}

### LOCALIZATION ({len(sd.get('localization', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('localization', {}))}

## STEAM REVIEWS SAMPLE
{self._fmt_reviews(sd.get('steam_reviews_sample'))}

## CONTEXT METRICS
- Total Evidence Count: {mini_context.get('evidence_count', 0)}
- Input Confidence Score: {mini_context.get('confidence_score', 0.0)}
- Data Sources: {', '.join(meta.get('data_sources', []))}

Analyze the data above and return the structured JSON intelligence report.
"""

    @staticmethod
    def _fmt_sources(category: dict) -> str:
        sources = category.get("sources", [])
        if not sources:
            return "  (no sources available)"
        lines = []
        for i, s in enumerate(sources, 1):
            lines.append(f"  [{i}] {s.get('title', 'No title')}")
            lines.append(f"      URL: {s.get('url', '')}")
            lines.append(f"      Platform: {s.get('platform', '')}")
            lines.append(f"      Snippet: {s.get('snippet', '')[:350]}")
        return "\n".join(lines)

    @staticmethod
    def _fmt_reviews(reviews: dict | None) -> str:
        if not reviews:
            return "  (no Steam reviews available)"
        pos = reviews.get("positive_count", 0)
        neg = reviews.get("negative_count", 0)
        score = reviews.get("review_score")
        samples = reviews.get("sample_reviews", [])[:5]
        lines = [
            f"  Positive: {pos:,} | Negative: {neg:,} | Score: {score or 'N/A'}",
            "",
            "  Sample Reviews:",
        ]
        for r in samples:
            sentiment = "POSITIVE" if r.get("voted_up") else "NEGATIVE"
            lang = r.get("language", "?")
            hrs = r.get("playtime_hours") or 0
            text = r.get("review", "")[:250]
            lines.append(f"  [{sentiment}] [{lang}, {hrs:.0f}h playtime] {text}")
        return "\n".join(lines)

    def _fallback_output(self, game_id: str, game_name: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "metadata": {
                "skill_id": "user_experience",
                "skill_name": "User Experience",
                "game_id": game_id,
                "game_name": game_name,
                "generated_at": now,
                "model_used": self.model_name,
            },
            "analysis": {
                "ui_ux": {
                    "category_id": "ui_ux",
                    "category_name": "UI/UX",
                    "overview": "Analysis failed",
                    "error": True,
                },
                "accessibility": {
                    "category_id": "accessibility",
                    "category_name": "Accessibility",
                    "overview": "Analysis failed",
                    "error": True,
                },
                "localization": {
                    "category_id": "localization",
                    "category_name": "Localization",
                    "overview": "Analysis failed",
                    "error": True,
                },
            },
            "summary": {
                "ux_philosophy": "Analysis could not be completed due to system error.",
                "standout_strengths": [],
                "critical_weaknesses": [],
                "priority_recommendations": [],
            },
            "confidence": {
                "overall_score": 0.0,
                "category_scores": {"ui_ux": 0.0, "accessibility": 0.0, "localization": 0.0},
                "data_quality_notes": ["System error prevented analysis."],
            },
        }

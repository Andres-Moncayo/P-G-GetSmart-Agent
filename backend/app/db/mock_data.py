import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from app.models import Report, Game, Facets, FacetCount, Pagination, ReportListResponse

# Helper class to simulate database rows
class MockRow:
    def __init__(self, data: Dict[str, Any]):
        self.__dict__.update(data)
        
    def __getattr__(self, name):
        return None

# Helper function to generate high-quality structured macro skills
def get_mock_structured_skills(game_name: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
    # Tailor some descriptions slightly per game if needed, or provide high-quality generic ones
    return [
        {
            "skill_key": "design_art",
            "skill_label": "Design & Art",
            "score": scores.get("Design & Art", 9.0),
            "confidence_raw": 0.95,
            "summary": f"La dirección artística de {game_name} destaca de manera sobresaliente. Presenta una estética visual sumamente pulida, una paleta de colores bien equilibrada y un diseño de personajes/entornos que consolida perfectamente su identidad visual.",
            "strengths": [
                "Dirección de arte única y memorable.",
                "Excelente uso de la iluminación y efectos de postprocesamiento.",
                "Coherencia estética en todos los niveles del juego."
            ],
            "weaknesses": [
                "Ciertas texturas secundarias muestran baja resolución en acercamientos.",
                "Consumo elevado de recursos gráficos en configuraciones ultra."
            ],
            "key_findings": [
                "La identidad visual del juego ha sido clave para su posicionamiento en redes.",
                "El diseño ambiental apoya de forma orgánica la narrativa del juego."
            ],
            "risks": [
                "Incompatibilidad de shaders en ciertos modelos de GPU antiguos."
            ],
            "opportunities": [
                "Lanzamiento de un libro de arte digital o skins estéticas exclusivas."
            ],
            "evidence_count": 15
        },
        {
            "skill_key": "user_experience",
            "skill_label": "User Experience",
            "score": scores.get("User Experience", 8.8),
            "confidence_raw": 0.92,
            "summary": f"La interfaz y el flujo del jugador en {game_name} están diseñados intuitivamente. Los menús son de fácil acceso, la curva de aprendizaje está bien balanceada y el sistema de tutoría se integra de manera orgánica con el juego.",
            "strengths": [
                "Interfaz limpia y minimalista que no obstruye la visibilidad.",
                "Controles altamente responsivos y personalizables.",
                "Curva de aprendizaje fluida tanto para novatos como para veteranos."
            ],
            "weaknesses": [
                "Falta de opciones avanzadas de accesibilidad (e.g., modos de daltonismo detallados).",
                "Ciertos submenús de configuración requieren demasiados clics para navegar."
            ],
            "key_findings": [
                "Los jugadores reportan una alta satisfacción con la respuesta inmediata de los controles.",
                "El flujo de onboarding inicial reduce considerablemente la tasa de abandono prematuro."
            ],
            "risks": [
                "Frustración potencial en consolas si el mapeado de botones por defecto no se optimiza."
            ],
            "opportunities": [
                "Implementar un HUD dinámico personalizable por el usuario."
            ],
            "evidence_count": 12
        },
        {
            "skill_key": "tech_systems",
            "skill_label": "Technology Systems",
            "score": scores.get("Technology Systems", 8.5),
            "confidence_raw": 0.89,
            "summary": f"El apartado tecnológico y de optimización de {game_name} demuestra bases sólidas. Se destaca por una tasa de refresco estable y tiempos de carga reducidos gracias a un buen manejo de memoria y streaming de assets.",
            "strengths": [
                "Estabilidad de FPS en situaciones de alto procesamiento.",
                "Excelente compresión de archivos reduciendo el peso de instalación.",
                "Manejo eficiente del streaming de texturas sin pop-in notable."
            ],
            "weaknesses": [
                "Bugs menores en la detección de colisiones de ciertos objetos del entorno.",
                "El motor físico muestra comportamientos erráticos bajo situaciones extremas de estrés."
            ],
            "key_findings": [
                "La tasa de frames promedio se mantiene estable en el percentil 95.",
                "La carga asíncrona de assets reduce los tiempos de pantalla de carga a la mitad."
            ],
            "risks": [
                "Posibles cuellos de botella en CPUs de gamas bajas al procesar físicas concurrentes."
            ],
            "opportunities": [
                "Migración/Actualización a la versión más reciente del motor gráfico para soporte nativo de Ray Tracing."
            ],
            "evidence_count": 18
        },
        {
            "skill_key": "strategy_market",
            "skill_label": "Strategy Market",
            "score": scores.get("Strategy Market", 9.2),
            "confidence_raw": 0.94,
            "summary": f"Estratégicamente, {game_name} goza de un excelente posicionamiento de mercado. Su modelo de negocio se alinea con las demandas actuales de su audiencia objetivo y presenta un alto potencial de monetización recurrente.",
            "strengths": [
                "Fuerte retención de usuarios a través de eventos estacionales.",
                "Estrategia de precios competitiva y atractiva frente a rivales directos.",
                "Excelente recepción crítica que impulsa las ventas orgánicas."
            ],
            "weaknesses": [
                "Dependencia excesiva de un nicho particular de jugadores.",
                "Poca visibilidad de marketing en mercados asiáticos emergentes."
            ],
            "key_findings": [
                "El ROI de las campañas de marketing de influencers ha sido superior al promedio histórico.",
                "Existe una correlación directa entre el soporte continuo y la estabilidad de ventas mensuales."
            ],
            "risks": [
                "Saturación de competidores directos lanzando propuestas similares en el mismo trimestre."
            ],
            "opportunities": [
                "Expandir la franquicia a plataformas móviles o servicios de suscripción en la nube."
            ],
            "evidence_count": 14
        }
    ]

# Initial mock data representing DB rows with 10 highly detailed games and their macro skills
MOCK_REPORTS_DB: List[Dict[str, Any]] = [
    {
        "id": uuid.UUID("b995247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.95,
        "game_name": "Ark: Survival Evolved",
        "game_slug": "ark-survival-evolved",
        "release_year": 2017,
        "primary_genre": "Adventure",
        "primary_platform": "PC",
        "developer_name": "Studio Wildcard",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1vce.png",
        "all_genres": ["Adventure", "Indie", "RPG", "Simulator"],
        "all_platforms": ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch"],
        "tags": ["Survival", "Dinosaur", "Open World"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 5, 0),
        "report_date": date(2026, 7, 1),
        "markdown_content": """# Ark: Survival Evolved - Análisis Integral

## Resumen Ejecutivo
Ark: Survival Evolved es uno de los títulos más representativos del género de supervivencia en mundo abierto. Con una propuesta basada en la domesticación de dinosaurios y el desarrollo tecnológico desde la edad de piedra hasta el armamento futurista (TEK), el juego ha capturado a una audiencia global inmensa.

## Análisis Temático
* **Supervivencia Extrema:** Gestión de recursos básicos, hambre, sed, clima y peligros biológicos.
* **Domesticación y Crianza (Taming):** El núcleo del juego, ofreciendo más de 100 criaturas con comportamientos únicos.
* **Progresión de Tribus:** Fuerte énfasis en el juego cooperativo y competitivo (PvP/PvE).

## Recomendaciones Estratégicas
1. **Optimización del Rendimiento:** Mejorar la carga de assets y las caídas de frames en consolas de anterior generación.
2. **Combate al Hackeo:** Fortalecer el sistema antitrampas en los servidores oficiales PvP.""",
        "executive_summary_jsonb": {
            "summary": "Un sandbox masivo de supervivencia y domesticación de dinosaurios con una progresión tecnológica única.",
            "verdict": "Altamente exitoso comercialmente, pero con constantes desafíos de optimización técnica y balance PvP."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 8.0, "User Experience": 7.5, "Technology Systems": 6.8, "Strategy Market": 8.5},
            "structured_skills": get_mock_structured_skills("Ark: Survival Evolved", {"Design & Art": 8.0, "User Experience": 7.5, "Technology Systems": 6.8, "Strategy Market": 8.5})
        },
        "confidence_analysis_jsonb": {
            "score": 0.95,
            "notes": "Acceso a fuentes de API oficiales completas y datos de scraping limpios."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["La comunidad es el principal motor del juego a través de mods.", "El modelo de DLCs expande la historia de manera exitosa."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Optimizar la infraestructura de servidores oficiales.", "Estabilizar las físicas de construcción masiva."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Pérdida de base de jugadores si el soporte para mods desaparece.", "Altos tiempos de carga ahuyentan a jugadores nuevos."]
        },
        "appendices_jsonb": {
            "sources": ["IGDB", "RAWG", "Steam Reviews"],
            "analyst": "GetSmart AI Orchestrator"
        }
    },
    {
        "id": uuid.UUID("c225247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.98,
        "game_name": "Hades",
        "game_slug": "hades",
        "release_year": 2020,
        "primary_genre": "Indie",
        "primary_platform": "PC",
        "developer_name": "Supergiant Games",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1v7f.png",
        "all_genres": ["Indie", "Action", "RPG"],
        "all_platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
        "tags": ["Roguelike", "Action", "Mythology"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 3, 15, 30, 0),
        "updated_at": datetime(2026, 7, 3, 15, 35, 0),
        "report_date": date(2026, 7, 3),
        "markdown_content": "# Hades - Análisis de Obra Maestra Roguelike\n\n## Resumen Ejecutivo\nHades es un roguelike de acción y exploración de mazmorras que combina los mejores aspectos de los títulos anteriores de Supergiant, incluido el combate rápido de Bastion y la profunda atmósfera de Pyre.\n\n## Análisis Temático\n* **Narrativa Roguelike:** Muerte no como penalización, sino como avance de la historia.\n* **Dirección de Arte y Música:** Estilo visual deslumbrante dibujado a mano y banda sonora dinámica.\n\n## Recomendaciones\n1. Continuar expandiendo la franquicia respetando el diseño de personajes del Inframundo.",
        "executive_summary_jsonb": {
            "summary": "Un exponente perfecto de cómo fusionar narrativa rica y jugabilidad roguelike adictiva.",
            "verdict": "Catalogado unánimemente como uno de los mejores juegos de la década por su ritmo de progresión."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.8, "User Experience": 9.6, "Technology Systems": 9.4, "Strategy Market": 9.5},
            "structured_skills": get_mock_structured_skills("Hades", {"Design & Art": 9.8, "User Experience": 9.6, "Technology Systems": 9.4, "Strategy Market": 9.5})
        },
        "confidence_analysis_jsonb": {
            "score": 0.98,
            "notes": "Puntaje máximo de datos y excelente consistencia en reseñas y ventas."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["Innovación al introducir diálogo dinámico adaptado a los intentos de escape del jugador."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Aprovechar el motor propietario para futuros desarrollos multiplataforma fluidos."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Dificultad inicial puede frustrar a jugadores no experimentados en el género roguelike."]
        },
        "appendices_jsonb": {
            "awards": ["Game of the Year - Golden Joystick Awards 2020", "Best Indie - TGA 2020"]
        }
    },
    {
        "id": uuid.UUID("d335247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.91,
        "game_name": "Cyberpunk 2077",
        "game_slug": "cyberpunk-2077",
        "release_year": 2020,
        "primary_genre": "RPG",
        "primary_platform": "PC",
        "developer_name": "CD PROJEKT RED",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2m76.png",
        "all_genres": ["RPG", "Action", "Sci-Fi"],
        "all_platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
        "tags": ["Cyberpunk", "Open World", "Sci-Fi"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 6, 11, 0, 0),
        "updated_at": datetime(2026, 7, 6, 11, 0, 0),
        "report_date": date(2026, 7, 6),
        "markdown_content": "# Cyberpunk 2077 - Redención en Night City\n\n## Resumen Ejecutivo\nTras un lanzamiento polémico y técnicamente comprometido, Cyberpunk 2077 logró convertirse en uno de los mundos abiertos de acción-RPG más inmersivos y bellos de la industria gracias a la actualización 2.0 y su expansión Phantom Liberty.\n\n## Análisis Temático\n* **Distopía Corporativa:** Night City como protagonista central.\n* **Personalización y Cyberware:** Modificación corporal que impacta directamente el estilo de juego.",
        "executive_summary_jsonb": {
            "summary": "Un ambicioso RPG de acción en primera persona que explora el transhumanismo en una distopía futurista.",
            "verdict": "Un gran ejemplo de redención técnica y de soporte post-lanzamiento en la industria de los videojuegos."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.4, "User Experience": 8.5, "Technology Systems": 8.0, "Strategy Market": 9.0},
            "structured_skills": get_mock_structured_skills("Cyberpunk 2077", {"Design & Art": 9.4, "User Experience": 8.5, "Technology Systems": 8.0, "Strategy Market": 9.0})
        },
        "confidence_analysis_jsonb": {
            "score": 0.91,
            "notes": "Datos estables recopilados tras múltiples parches y la salida del DLC Phantom Liberty."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["El cambio a REDengine trajo retos de desarrollo masivos que retrasaron el juego por años."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Enfocar la próxima entrega en Unreal Engine 5 para mitigar deuda técnica."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Expectativas infladas para la secuela debido al largo camino de parches del primer juego."]
        },
        "appendices_jsonb": {
            "release_patches": ["Update 1.5 (Next-gen)", "Update 2.0 (Combate vehícular)", "Phantom Liberty DLC"]
        }
    },
    {
        "id": uuid.UUID("e445247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.96,
        "game_name": "The Witcher 3: Wild Hunt",
        "game_slug": "the-witcher-3-wild-hunt",
        "release_year": 2015,
        "primary_genre": "RPG",
        "primary_platform": "PC",
        "developer_name": "CD PROJEKT RED",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1sf5.png",
        "all_genres": ["RPG", "Action", "Adventure"],
        "all_platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
        "tags": ["Fantasy", "Open World", "Story Rich"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 5, 9, 15, 0),
        "updated_at": datetime(2026, 7, 5, 9, 20, 0),
        "report_date": date(2026, 7, 5),
        "markdown_content": "# The Witcher 3: Wild Hunt - El Estándar de los RPG de Mundo Abierto\n\n## Resumen Ejecutivo\nGeralt de Rivia emprende su búsqueda más personal en un continente desgarrado por la guerra y acechado por la cacería salvaje.\n\n## Análisis Temático\n* **Cazador de Monstruos:** Preparación alquímica, bestiario y contratos complejos.\n* **Moralidad Gris:** Decisiones sin respuestas fáciles que alteran el destino de reinos enteros.",
        "executive_summary_jsonb": {
            "summary": "Una de las cumbres del diseño de misiones y mundos abiertos de fantasía oscura.",
            "verdict": "Un clásico moderno indispensable con una de las mejores narrativas secundarias de la historia."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.5, "User Experience": 9.2, "Technology Systems": 8.8, "Strategy Market": 9.4},
            "structured_skills": get_mock_structured_skills("The Witcher 3: Wild Hunt", {"Design & Art": 9.5, "User Experience": 9.2, "Technology Systems": 8.8, "Strategy Market": 9.4})
        },
        "confidence_analysis_jsonb": {
            "score": 0.96,
            "notes": "Gran madurez de datos y estabilidad comercial desde hace una década."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["El minijuego 'Gwent' fue tan popular que generó su propio spin-off independiente."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Mantener la fidelidad al lore literario de Andrzej Sapkowski en futuros títulos."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Saturación de contenido de mundo abierto puede fatigar a nuevos jugadores modernos."]
        },
        "appendices_jsonb": {
            "expansions": ["Hearts of Stone", "Blood and Wine (Ganadora de mejor RPG 2016)"]
        }
    },
    {
        "id": uuid.UUID("f555247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("55555555-5555-5555-5555-555555555555"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.99,
        "game_name": "Minecraft",
        "game_slug": "minecraft",
        "release_year": 2011,
        "primary_genre": "Simulator",
        "primary_platform": "PC",
        "developer_name": "Mojang Studios",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r78.png",
        "all_genres": ["Simulator", "Adventure", "Indie"],
        "all_platforms": ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch", "Mobile"],
        "tags": ["Sandbox", "Crafting", "Survival"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 4, 14, 0, 0),
        "updated_at": datetime(2026, 7, 4, 14, 5, 0),
        "report_date": date(2026, 7, 4),
        "markdown_content": "# Minecraft - Creatividad sin Límites\n\n## Resumen Ejecutivo\nMinecraft es el videojuego más vendido de todos los tiempos. Permite a los jugadores explorar mundos generados procedimentalmente, construir todo tipo de estructuras y sobrevivir a amenazas en un ecosistema cúbico infinito.\n\n## Análisis Temático\n* **Jugabilidad Sandbox:** Libertad total sin objetivos forzados.\n* **Ingeniería Redstone:** Complejo sistema lógico dentro del juego que simula compuertas eléctricas.",
        "executive_summary_jsonb": {
            "summary": "Un sandbox infinito que se ha convertido en un fenómeno cultural y educativo global.",
            "verdict": "Vigente y actual tras más de 15 años en el mercado gracias a actualizaciones anuales constantes."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 8.5, "User Experience": 9.2, "Technology Systems": 9.4, "Strategy Market": 9.8},
            "structured_skills": get_mock_structured_skills("Minecraft", {"Design & Art": 8.5, "User Experience": 9.2, "Technology Systems": 9.4, "Strategy Market": 9.8})
        },
        "confidence_analysis_jsonb": {
            "score": 0.99,
            "notes": "Datos y documentación globales con el más alto grado de veracidad y cobertura."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["Herramienta educativa ampliamente adoptada en escuelas para enseñar lógica y programación básica."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Balancear cuidadosamente la introducción de nuevas mecánicas para no alienar a la base de jugadores puristas."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Fragmentación de la comunidad entre versiones Java y Bedrock."]
        },
        "appendices_jsonb": {
            "versions": ["Minecraft Java Edition", "Minecraft Bedrock Edition", "Minecraft Education Edition"]
        }
    },
    {
        "id": uuid.UUID("a115247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("66666666-6666-6666-6666-666666666666"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.97,
        "game_name": "Elden Ring",
        "game_slug": "elden-ring",
        "release_year": 2022,
        "primary_genre": "RPG",
        "primary_platform": "PC",
        "developer_name": "FromSoftware",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co4hju.png",
        "all_genres": ["RPG", "Action"],
        "all_platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
        "tags": ["Souls-like", "Dark Fantasy", "Open World"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 5, 18, 0, 0),
        "updated_at": datetime(2026, 7, 5, 18, 10, 0),
        "report_date": date(2026, 7, 5),
        "markdown_content": "# Elden Ring - El Triunfo de la Exploración Libre\n\n## Resumen Ejecutivo\nElden Ring traslada la clásica jugabilidad desafiante de FromSoftware a un colosal mundo abierto llamado las Tierras Intermedias, codiseñado por George R. R. Martin.\n\n## Análisis Temático\n* **Libertad de Exploración:** Sin marcadores intrusivos en el mapa, fomentando la curiosidad orgánica.\n* **Lore de Fantasía:** Una compleja red mitológica de semidioses y el Círculo de Elden.",
        "executive_summary_jsonb": {
            "summary": "Una magistral evolución del género Souls-like hacia un sandbox abierto de exploración libre.",
            "verdict": "Obra cumbre de FromSoftware que expande las bases del diseño de mundos abiertos modernos."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.8, "User Experience": 8.8, "Technology Systems": 9.0, "Strategy Market": 9.6},
            "structured_skills": get_mock_structured_skills("Elden Ring", {"Design & Art": 9.8, "User Experience": 8.8, "Technology Systems": 9.0, "Strategy Market": 9.6})
        },
        "confidence_analysis_jsonb": {
            "score": 0.97,
            "notes": "Consistencia impecable en reviews globales y base de jugadores muy activa."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["La inclusión del caballo 'Torrentera' redefinió completamente las tácticas de combate e invasión."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Expandir el universo a través de más DLCs de alto nivel narrativo y de combate."]
        },
        "risk_assessment_jsonb": {
            "risks": ["La dificultad elevada puede seguir siendo una barrera de entrada para la masa general."]
        },
        "appendices_jsonb": {
            "expansions": ["Shadow of the Erdtree (2024)"]
        }
    },
    {
        "id": uuid.UUID("a225247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("77777777-7777-7777-7777-777777777777"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.95,
        "game_name": "Red Dead Redemption 2",
        "game_slug": "red-dead-redemption-2",
        "release_year": 2018,
        "primary_genre": "Adventure",
        "primary_platform": "PlayStation 4",
        "developer_name": "Rockstar Games",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q1f.png",
        "all_genres": ["Adventure", "Action"],
        "all_platforms": ["PC", "PlayStation 4", "Xbox One"],
        "tags": ["Western", "Story Rich", "Realistic"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 2, 12, 0, 0),
        "updated_at": datetime(2026, 7, 2, 12, 12, 0),
        "report_date": date(2026, 7, 2),
        "markdown_content": "# Red Dead Redemption 2 - El Fin de los Forajidos\n\n## Resumen Ejecutivo\nArthur Morgan y la banda de Van der Linde se ven forzados a huir a finales del siglo XIX, lidiando con el declive del viejo oeste y la llegada de la ley industrial.\n\n## Análisis Temático\n* **Realismo Extremo:** Ciclos de caza detallados, cuidado del caballo y desgaste de armas realista.\n* **Estudio de Carácter:** El descenso moral y la redención del protagonista Arthur Morgan.",
        "executive_summary_jsonb": {
            "summary": "Una de las narrativas más profundas e inmersivas y un nivel de detalle técnico casi inigualable en la industria.",
            "verdict": "Un hito técnico en la recreación de entornos naturales y simulaciones de vida silvestre."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.9, "User Experience": 9.2, "Technology Systems": 9.4, "Strategy Market": 9.5},
            "structured_skills": get_mock_structured_skills("Red Dead Redemption 2", {"Design & Art": 9.9, "User Experience": 9.2, "Technology Systems": 9.4, "Strategy Market": 9.5})
        },
        "confidence_analysis_jsonb": {
            "score": 0.95,
            "notes": "Altísima fidelidad de datos históricos, mecánicas y cobertura crítica."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["El nivel de interactividad de los NPCs sentó un nuevo precedente para los juegos de rol occidentales."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Mantener la inversión en narrativas maduras y de un solo jugador en próximos desarrollos."]
        },
        "risk_assessment_jsonb": {
            "risks": ["El ritmo lento inicial (capítulo 1 en la nieve) puede alejar a usuarios casuales."]
        },
        "appendices_jsonb": {
            "technology": ["Custom RAGE engine con avanzadas simulaciones atmosféricas."]
        }
    },
    {
        "id": uuid.UUID("a335247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("88888888-8888-8888-8888-888888888888"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.98,
        "game_name": "The Legend of Zelda: Breath of the Wild",
        "game_slug": "the-legend-of-zelda-breath-of-the-wild",
        "release_year": 2017,
        "primary_genre": "Adventure",
        "primary_platform": "Nintendo Switch",
        "developer_name": "Nintendo EPD",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7f.png",
        "all_genres": ["Adventure", "RPG"],
        "all_platforms": ["Nintendo Switch", "Wii U"],
        "tags": ["Open World", "Fantasy", "Exploration"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 1, 14, 0, 0),
        "updated_at": datetime(2026, 7, 1, 14, 5, 0),
        "report_date": date(2026, 7, 1),
        "markdown_content": "# The Legend of Zelda: Breath of the Wild - Un Viento de Cambio en Hyrule\n\n## Resumen Ejecutivo\nNintendo reinventa su franquicia más icónica eliminando la progresión lineal tradicional por un sandbox basado en la interacción de elementos de física y química.\n\n## Análisis Temático\n* **Química de Elementos:** Fuego propaga viento, electricidad se transmite por metales y agua, etc.\n* **Ruina y Nostalgia:** Un Hyrule post-apocalíptico melancólico y vasto.",
        "executive_summary_jsonb": {
            "summary": "Una revolución en el diseño de niveles que incentiva al jugador a experimentar en lugar de seguir marcadores.",
            "verdict": "Ganador indiscutible de múltiples premios a Juego del Año y referente obligado de diseño abierto."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.7, "User Experience": 9.5, "Technology Systems": 9.4, "Strategy Market": 9.6},
            "structured_skills": get_mock_structured_skills("The Legend of Zelda: Breath of the Wild", {"Design & Art": 9.7, "User Experience": 9.5, "Technology Systems": 9.4, "Strategy Market": 9.6})
        },
        "confidence_analysis_jsonb": {
            "score": 0.98,
            "notes": "Puntaje máximo gracias a la gigantesca documentación crítica disponible."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["La escalabilidad total de superficies obligó a replantear el diseño de obstáculos verticales en videojuegos."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Continuar impulsando mecánicas de construcción y creatividad (como se vio en Tears of the Kingdom)."]
        },
        "risk_assessment_jsonb": {
            "risks": ["La durabilidad de las armas fue un punto polarizante que molestó a ciertos jugadores veteranos."]
        },
        "appendices_jsonb": {
            "dlc": ["The Master Trials", "The Champions' Ballad"]
        }
    },
    {
        "id": uuid.UUID("a445247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("99999999-9999-9999-9999-999999999999"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.94,
        "game_name": "Grand Theft Auto V",
        "game_slug": "grand-theft-auto-v",
        "release_year": 2013,
        "primary_genre": "Action",
        "primary_platform": "PC",
        "developer_name": "Rockstar North",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r8c.png",
        "all_genres": ["Action", "Adventure"],
        "all_platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "PlayStation 3", "Xbox 360"],
        "tags": ["Crime", "Sandbox", "Multiplayer"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 2, 10, 0, 0),
        "updated_at": datetime(2026, 7, 2, 10, 8, 0),
        "report_date": date(2026, 7, 2),
        "markdown_content": "# Grand Theft Auto V - La Sátira de la Sociedad de Los Santos\n\n## Resumen Ejecutivo\nEl título narra las vidas entrelazadas de tres criminales muy distintos que planean audaces atracos en la soleada metrópolis de Los Santos.\n\n## Análisis Temático\n* **Tres Protagonistas:** Alternancia fluida entre Michael, Franklin y Trevor en tiempo real.\n* **Sátira Cultural:** Ácida crítica social a las redes sociales, Hollywood y el sueño americano.",
        "executive_summary_jsonb": {
            "summary": "Un coloso comercial indiscutible impulsado por su masivo ecosistema en línea (GTA Online).",
            "verdict": "Uno de los productos de entretenimiento más rentables de todos los tiempos."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.2, "User Experience": 9.4, "Technology Systems": 9.0, "Strategy Market": 9.8},
            "structured_skills": get_mock_structured_skills("Grand Theft Auto V", {"Design & Art": 9.2, "User Experience": 9.4, "Technology Systems": 9.0, "Strategy Market": 9.8})
        },
        "confidence_analysis_jsonb": {
            "score": 0.94,
            "notes": "Datos estables a lo largo de tres generaciones diferentes de consolas de videojuegos."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["GTA Online extendió la vida del juego por más de una década, redefiniendo las ganancias recurrentes."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Garantizar la retrocompatibilidad y la continuidad de perfiles en futuras secuelas."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Fatiga de la comunidad por la falta de un nuevo juego de un solo jugador en más de diez años."]
        },
        "appendices_jsonb": {
            "sales": ["Más de 190 millones de copias vendidas a nivel global."]
        }
    },
    {
        "id": uuid.UUID("a555247f-5b34-431e-ae69-3e5c7bf08776"),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "game_id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "report_status": "completed",
        "report_type": "comprehensive",
        "confidence_score": 0.97,
        "game_name": "Portal 2",
        "game_slug": "portal-2",
        "release_year": 2011,
        "primary_genre": "Indie",
        "primary_platform": "PC",
        "developer_name": "Valve",
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7a.png",
        "all_genres": ["Indie", "Action", "Adventure"],
        "all_platforms": ["PC", "PlayStation 3", "Xbox 360", "Nintendo Switch"],
        "tags": ["Puzzle", "Comedy", "Sci-Fi"],
        "current_phase": "storage",
        "pipeline_progress": 100,
        "created_at": datetime(2026, 7, 4, 16, 0, 0),
        "updated_at": datetime(2026, 7, 4, 16, 4, 0),
        "report_date": date(2026, 7, 4),
        "markdown_content": "# Portal 2 - Genialidad en Puzles y Comedia Científica\n\n## Resumen Ejecutivo\nValve eleva el concepto del juego original a una aventura completa con nuevos geles interactivos, personajes entrañables y un humor único en los laboratorios de Aperture Science.\n\n## Análisis Temático\n* **Diseño de Puzles Espaciales:** Uso ingenioso de la inercia física y los portales interdimensionales.\n* **Comedia Narrativa:** Las brillantes actuaciones de voz de GLaDOS, Wheatley y Cave Johnson.",
        "executive_summary_jsonb": {
            "summary": "Uno de los juegos de puzles perfectos, aclamado por su narrativa ingeniosa y su modo cooperativo.",
            "verdict": "Un punto de referencia en el diseño de curvas de dificultad y guión humorístico."
        },
        "thematic_analysis_jsonb": {
            "skill_scores": {"Design & Art": 9.5, "User Experience": 9.7, "Technology Systems": 9.5, "Strategy Market": 9.2},
            "structured_skills": get_mock_structured_skills("Portal 2", {"Design & Art": 9.5, "User Experience": 9.7, "Technology Systems": 9.5, "Strategy Market": 9.2})
        },
        "confidence_analysis_jsonb": {
            "score": 0.97,
            "notes": "Reseñas perfectas consistentes en todas las plataformas y análisis históricos."
        },
        "cross_cutting_insights_jsonb": {
            "insights": ["El modo cooperativo para dos personas introdujo puzles basados en portales cuádruples únicos."]
        },
        "strategic_recommendations_jsonb": {
            "recommendations": ["Fomentar herramientas comunitarias para que los usuarios creen sus propias cámaras de pruebas."]
        },
        "risk_assessment_jsonb": {
            "risks": ["Bajo valor de rejugabilidad de la campaña de un solo jugador una vez resueltos todos los puzles."]
        },
        "appendices_jsonb": {
            "coop_characters": ["Atlas", "P-Body"]
        }
    }
]

class MockDatabaseManager:
    @staticmethod
    def get_facets() -> Facets:
        genres: Dict[str, int] = {}
        developers: Dict[str, int] = {}
        platforms: Dict[str, int] = {}
        statuses: Dict[str, int] = {}
        min_year = datetime.now().year
        max_year = 1970
        
        for r in MOCK_REPORTS_DB:
            # Status
            status = r["report_status"]
            statuses[status] = statuses.get(status, 0) + 1
            
            # Developer
            dev = r["developer_name"]
            if dev:
                developers[dev] = developers.get(dev, 0) + 1
                
            # Genres
            for g in r.get("all_genres", []):
                genres[g] = genres.get(g, 0) + 1
                
            # Platforms
            for p in r.get("all_platforms", []):
                platforms[p] = platforms.get(p, 0) + 1
                
            # Years
            y = r.get("release_year")
            if y:
                min_year = min(min_year, y)
                max_year = max(max_year, y)
                
        return Facets(
            genre=[FacetCount(value=k, count=v, label=k) for k, v in genres.items()],
            developer=[FacetCount(value=k, count=v, label=k) for k, v in developers.items()],
            platform=[FacetCount(value=k, count=v, label=k) for k, v in platforms.items()],
            status=[FacetCount(value=k, count=v, label=k) for k, v in statuses.items()],
            year_range={"min_year": min_year, "max_year": max_year}
        )

    @staticmethod
    def list_reports(
        genre: Optional[List[str]] = None,
        developer: Optional[List[str]] = None,
        platform: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[List[MockRow], int]:
        filtered = list(MOCK_REPORTS_DB)
        
        if genre:
            filtered = [r for r in filtered if r["primary_genre"] in genre or any(g in r.get("all_genres", []) for g in genre)]
        if developer:
            filtered = [r for r in filtered if r["developer_name"] in developer]
        if platform:
            filtered = [r for r in filtered if r["primary_platform"] in platform or any(p in r.get("all_platforms", []) for p in platform)]
        if status:
            filtered = [r for r in filtered if r["report_status"] in status]
        if year_from is not None:
            filtered = [r for r in filtered if r["release_year"] and r["release_year"] >= year_from]
        if year_to is not None:
            filtered = [r for r in filtered if r["release_year"] and r["release_year"] <= year_to]
        if search:
            q = search.lower()
            filtered = [
                r for r in filtered 
                if q in r["game_name"].lower() or (r["developer_name"] and q in r["developer_name"].lower())
            ]
            
        # Sorting
        reverse = sort_dir.lower() == "desc"
        if sort_by == "game.name":
            filtered.sort(key=lambda x: x["game_name"], reverse=reverse)
        elif sort_by == "game.release_year":
            filtered.sort(key=lambda x: x.get("release_year", 0), reverse=reverse)
        elif sort_by == "progress_percent":
            filtered.sort(key=lambda x: x.get("pipeline_progress", 0), reverse=reverse)
        else: # created_at / updated_at
            filtered.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=reverse)
            
        # Pagination
        offset = (page - 1) * page_size
        paginated = filtered[offset : offset + page_size]
        
        return [MockRow(item) for item in paginated], len(filtered)

    @staticmethod
    def get_report(report_id: uuid.UUID) -> Optional[MockRow]:
        for r in MOCK_REPORTS_DB:
            if r["id"] == report_id:
                return MockRow(r)
        return None

    @staticmethod
    def update_report(report_id: uuid.UUID, tags: Optional[List[str]] = None, notes: Optional[str] = None) -> Optional[MockRow]:
        for r in MOCK_REPORTS_DB:
            if r["id"] == report_id:
                if tags is not None:
                    r["tags"] = tags
                if notes is not None:
                    meta = dict(r.get("user_metadata_jsonb") or {})
                    meta["user_notes"] = notes
                    r["user_metadata_jsonb"] = meta
                r["updated_at"] = datetime.now()
                return MockRow(r)
        return None

    @staticmethod
    def create_report(data: Dict[str, Any]) -> MockRow:
        # Check if already exists, else append
        for r in MOCK_REPORTS_DB:
            if r["id"] == data["id"]:
                return MockRow(r)
                
        # Fill default values matching the DB columns format
        new_row = dict(data)
        new_row.setdefault("created_at", datetime.now())
        new_row.setdefault("updated_at", datetime.now())
        new_row.setdefault("report_date", date.today())
        new_row.setdefault("confidence_score", 0.0)
        new_row.setdefault("markdown_content", "")
        new_row.setdefault("executive_summary_jsonb", {})
        new_row.setdefault("thematic_analysis_jsonb", {})
        new_row.setdefault("confidence_analysis_jsonb", {})
        new_row.setdefault("cross_cutting_insights_jsonb", {})
        new_row.setdefault("strategic_recommendations_jsonb", {})
        new_row.setdefault("risk_assessment_jsonb", {})
        new_row.setdefault("appendices_jsonb", {})
        
        # Auto-populate mock structured skills for new reports
        scores = {"Design & Art": 8.0, "User Experience": 8.0, "Technology Systems": 8.0, "Strategy Market": 8.0}
        new_row["thematic_analysis_jsonb"] = {
            "skill_scores": scores,
            "structured_skills": get_mock_structured_skills(data.get("game_name", "Game"), scores)
        }
        
        MOCK_REPORTS_DB.append(new_row)
        return MockRow(new_row)

    @staticmethod
    def update_report_fields(report_id: uuid.UUID, update_data: Dict[str, Any]) -> bool:
        for r in MOCK_REPORTS_DB:
            if r["id"] == report_id:
                r.update(update_data)
                r["updated_at"] = datetime.now()
                return True
        return False

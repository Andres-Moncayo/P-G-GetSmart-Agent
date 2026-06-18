# → Create PR → Review → Merge to dev/main
```

## 📁 Estructura de Carpetas: Dónde Implementar Skills

### 🎯 **BACKEND Structure Analysis**

**Current Structure:**
```
backend/
├── app/
│   ├── api/routes.py          ← 🔥 Add skill endpoints here
│   ├── services/             ← 🔥 Add skill logic here
│   ├── models/               ← 🔥 Add Pydantic models here
│   ├── core/config.py        ← Environment config
│   ├── db/connection.py      ← Database layer
│   └── main.py               ← FastAPI entrypoint
├── requirements.txt          ← FastAPI + dependencies
└── README.md
```

**🚀 WHERE MACRO-SKILLS GO:**

```
backend/app/api/
├── routes.py                 ← Main router
├── macro_skills/
│   ├── ux_skill.py          ← ✅ /api/ux-analysis
│   ├── design_art_skill.py  ← ✅ /api/design-art-analysis  
│   ├── tech_systems_skill.py← ✅ /api/tech-analysis
│   └── strategy_market_skill.py ← ✅ /api/strategy-analysis
└── synthesis/
    └── synthesis_skill.py   ← ✅ /api/synthesis

backend/app/services/
├── macro_skills/
│   ├── ux_service.py        ← ✅ UX analysis logic
│   ├── design_art_service.py ← ✅ Design analysis logic
│   ├── tech_service.py      ← ✅ Tech analysis logic
│   └── strategy_service.py  ← ✅ Strategy analysis logic
└── synthesis/
    └── synthesis_service.py← ✅ Synthesis logic

backend/app/models/
├── macro_skills/
│   ├── ux_models.py         ← ✅ Pydantic schemas for UX
│   ├── design_art_models.py← ✅ Pydantic schemas for Design
│   ├── tech_models.py      ← ✅ Pydantic schemas for Tech  
│   └── strategy_models.py  ← ✅ Pydantic schemas for Strategy
└── synthesis/
    └── synthesis_models.py ← ✅ Pydantic schemas for Synthesis
```

---

### 🎨 **FRONTEND Structure Analysis**

**Current Structure:**
```
frontend/
├── src/
│   ├── index.tsx            ← App entrypoint (placeholder)
│   ├── components/          ← 🔥 Reusable components here
│   ├── modules/             ← 🔥 Skill modules here  
│   ├── pages/               ← Page-level components
│   ├── services/            ← 🔥 API services here
│   ├── state/               ← State management
│   ├── types/               ← TypeScript type definitions
│   └── styles/              ← Global styles
├── package.json             ← Vite + React
└── README.md
```

**🚀 WHERE MACRO-SKILLS GO:**

```
frontend/src/modules/
├── auth/
│   └── login/               ← ✅ Existing
├── dashboard/               ← ✅ Existing  
├── pipeline/                ← ✅ Existing
├── reports/                 ← ✅ Existing
├── macro_skills/            ← 🔥 ADD THIS FOLDER
│   ├── ux_skill/           ← ✅ UX analysis UI
│   │   ├── UxAnalysisComponent.tsx
│   │   └── index.tsx
│   ├── design_art_skill/   ← ✅ Design analysis UI
│   │   ├── DesignArtComponent.tsx
│   │   └── index.tsx
│   ├── tech_systems_skill/← ✅ Tech analysis UI
│   │   ├── TechComponent.tsx
│   │   └── index.tsx
│   └── strategy_market_skill/← ✅ Strategy analysis UI
│       ├── StrategyComponent.tsx
│       └── index.tsx
└── synthesis/              ← 🔥 ADD THIS FOLDER
    └── synthesis_skill/   ← ✅ Synthesis UI
        ├── SynthesisComponent.tsx
        └── index.tsx

frontend/src/components/
├── common/                  ← 🔥 ADD shared components
│   ├── AnalysisCard.tsx    ← ✅ Generic skill card
│   ├── LoadingSpinner.tsx  ← ✅ Loading states
│   └── ErrorBoundary.tsx   ← ✅ Error handling
└── charts/                  ← 🔥 ADD visualization components
    ├── BarChart.tsx        ← ✅ Chart components
    └── PieChart.tsx

frontend/src/services/
├── api/                     ← 🔥 ADD API services  
│   ├── uxApi.ts           ← ✅ UX API calls
│   ├── designApi.ts       ← ✅ Design API calls
│   ├── techApi.ts         ← ✅ Tech API calls
│   ├── strategyApi.ts     ← ✅ Strategy API calls
│   └── synthesisApi.ts    ← ✅ Synthesis API calls
└── types/                   ← 🔥 ADD TypeScript types
    ├── uxTypes.ts         ← ✅ UX interfaces
    ├── designTypes.ts     ← ✅ Design interfaces  
    ├── techTypes.ts       ← ✅ Tech interfaces
    ├── strategyTypes.ts   ← ✅ Strategy interfaces
    └── synthesisTypes.ts  ← ✅ Synthesis interfaces
```

---

### 🎯 **MAPPING: OpenSpec → Implementation**

| OpenSpec Contract | Backend Implementation | Frontend Implementation |
|------------------|----------------------|------------------------|
| `ux_skill.yaml` | `/app/api/macro_skills/ux_skill.py` | `/src/modules/macro_skills/ux_skill/` |
| `design_art_skill.yaml` | `/app/api/macro_skills/design_art_skill.py` | `/src/modules/macro_skills/design_art_skill/` |
| `tech_systems_skill.yaml` | `/app/api/macro_skills/tech_systems_skill.py` | `/src/modules/macro_skills/tech_systems_skill/` |
| `strategy_market_skill.yaml` | `/app/api/macro_skills/strategy_market_skill.py` | `/src/modules/macro_skills/strategy_market_skill/` |
| `synthesis_skill.yaml` | `/app/api/synthesis/synthesis_skill.py` | `/src/modules/synthesis/synthesis_skill/` |

---

### ✅ **VALIDATION CHECKLIST**

**Backend ✅:**
- [x] FastAPI structure correcto
- [x] API/routes.py listo para incluir routers
- [x] Services/ listo para lógica de negocio
- [x] Models/ listo para Pydantic schemas
- [x] Requirements.txt incluye FastAPI

**Frontend ✅:**  
- [x] Vite + React configurado
- [x] Modules/ structure existent
- [x] Services/ listo para API calls
- [x] Components/ listo para UI components
- [x] Types/ listo para TypeScript interfaces

**🚀 LISTO PARA IMPLEMENTACIÓN!**

---

### 4. After implementation:
   - Rerun validation: `openspec validate --all`
   - Update OpenSpec docs only if the contract itself changes
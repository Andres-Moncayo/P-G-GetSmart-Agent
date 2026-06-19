# GetSmart v3.0

Deterministic Parallel Analysis Pipeline for comprehensive game intelligence reports powered by Spec-Driven Development (SDD).

## 🎯 Project Overview

GetSmart is a sophisticated game intelligence platform that automatically analyzes games across multiple dimensions and generates professional-grade reports. The system uses a deterministic pipeline with four parallel Macro-Skills to process game data and produce actionable insights.

### Core Architecture

The pipeline follows a structured four-phase approach:

- **Phase 1**: Data Collection (Scrapers + Master-JSON consolidation)
- **Phase 2**: Parallel Analysis (4 Macro-Skills processing)  
- **Phase 3**: Synthesis (Combined intelligence generation)
- **Phase 4**: Report Generation (Multi-format output)

### Key Features

- **Deterministic Processing**: Predictable, programmatic control over analysis
- **Parallel Architecture**: Four independent analyzers working simultaneously
- **Professional Reports**: Structured intelligence suitable for business use cases
- **OpenSpec Contracts**: Complete specification-driven development
- **AI-Assisted Development**: Modern agent-based implementation workflow

---

## 🛠 Technical Stack

### Backend Architecture

- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis broker
- **Validation**: Pydantic for data validation
- **API Documentation**: OpenAPI/Swagger automatically generated
- **Environment**: Python-dotenv for configuration management

### Frontend Architecture

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and building
- **State Management**: Redux Toolkit for state handling
- **UI Components**: Component-based architecture with reusable patterns
- **API Integration**: Axios for backend communication
- **Development**: Hot reload with Vite dev server

### Development Tools

- **Specification**: OpenSpec for contract-driven development
- **Validation**: Automated spec validation with OpenSpec CLI
- **Version Control**: Git with structured commit workflow
- **Package Management**: pip (backend) and npm (frontend)
- **Documentation**: Markdown-based documentation system

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- PostgreSQL instance (local or cloud)
- OpenSpec CLI tool installed globally

### Setup Instructions

```bash
# Clone repository
git clone https://github.com/alejandroalzate01/g-GetSmart-Agent.git

# Install OpenSpec CLI
npm install -g @fission-ai/openspec@latest

# Validate OpenSpec contracts
openspec validate --all

# Backend setup
cd backend
pip install -r requirements.txt
# Create .env file with DATABASE_URL
uvicorn app.main:app --reload

# Frontend setup (in separate terminal)
cd frontend
npm install
npm run dev
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://neondb_owner:npg_QZN5qMuUjv9h@ep-misty-sky-aqh6wq9v-pooler.c-8.us-east-1.aws.neon.tech/getsmarth?sslmode=require&channel_binding=require
REDIS_URL=redis://localhost:6379
DEBUG=true
```

---

## 📋 Spec-Driven Development Workflow

### OpenSpec Integration

This project uses OpenSpec for complete contract-driven development. The specifications define all system behaviors, data contracts, and implementation requirements.

#### Available Specifications

**Macro Skills:**
- `openspec/specs/macro_skills/ux_skill.yaml` - User Experience analysis contract
- `openspec/specs/macro_skills/design_art_skill.yaml` - Design and Art analysis contract
- `openspec/specs/macro_skills/tech_systems_skill.yaml` - Technical Systems analysis contract
- `openspec/specs/macro_skills/strategy_market_skill.yaml` - Strategy and Market analysis contract

**Core Systems:**
- `openspec/specs/synthesis/synthesis_skill.yaml` - Synthesis engine contract
- `openspec/specs/scraper/` - Data collection contracts
- `openspec/specs/ui_and_login/ui_login_contract.md` - User Interface specification

### Development Commands

```bash
# Validate all specifications and changes
openspec validate --all

# List all registered changes
openspec list

# Create new OpenSpec change
openspec new change

# Show available workflow schemas
openspec schemas
```

### Complete Workflow Documentation

For detailed workflow procedures, including:
- File upload restrictions per contract ownership
- GitHub PR approval workflows with Tech Lead authority
- Specification changes vs implementation changes
- Quality assurance validation procedures
- Team communication standards and templates

**See:** `openspec/spec-driven-workflow.md`

This workflow ensures clean modular development while maintaining full traceability between OpenSpec contracts and code implementation.

---

## 🤖 AI-Assisted Development Process

### Standard Development Flow

This project follows an AI-assisted Spec-Driven Development (SDD) approach that combines the rigor of specification-driven development with the efficiency of AI-powered code generation.

#### Development Workflow

1. **Environment Setup**
   ```bash
   git clone <repository>
   npm npm install -g @fission-ai/openspec@latest
   openspec validate --all
   ```

2. **Feature Implementation**
   Developers provide AI agents with specific OpenSpec contracts:
   ```
   "Implement the UX Skill according to openspec/specs/macro_skills/ux_skill.yaml
   
   Create:
   1. Backend API endpoint /api/ux-analysis
   2. Frontend React component for UX analysis
   3. Handler that processes input JSON and generates output JSON according to schema"
   ```

3. **AI Implementation**
   AI generates complete implementation following contracts:
   ```python
   # Backend implementation example
   @router.post("/ux-analysis")
   async def analyze_ux(input_data: UXAnalysisInput) -> UXAnalysisOutput:
       # Process according to ux_skill.yaml contract
       return analysis_result
   ```

   ```tsx
   // Frontend implementation example
   export const UXAnalysisComponent = () => {
       // Implements UI per contract specifications
   };
   ```

4. **Validation and Deployment**
   ```bash
   openspec validate --all
   git add .
   git commit -m "feat: implement UX analysis skill per OpenSpec contracts"
   git push origin feature/ux-analysis-implementation
   ```

#### Key Advantages

- **Specification First**: All code derives from contracts
- **Quality Assurance**: Automated validation ensures compliance
- **Rapid Development**: AI generates complete implementations
- **Consistent Architecture**: All modules follow the same patterns
- **Documentation**: Specifications serve as living documentation

---

## 📁 Project Structure

### Backend Organization

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py              # Main API router
│   │   └── macro_skills/          # Skill-specific endpoints
│   │       ├── ux_skill.py        # UX analysis API
│   │       ├── design_art_skill.py # Design analysis API
│   │       ├── tech_systems_skill.py # Technical analysis API
│   │       └── strategy_market_skill.py # Strategy analysis API
│   ├── services/
│   │   └── macro_skills/          # Business logic layer
│   │       ├── ux_service.py      # UX analysis logic
│   │       ├── design_art_service.py # Design analysis logic
│   │       ├── tech_service.py    # Technical analysis logic
│   │       └── strategy_service.py # Strategy analysis logic
│   ├── models/
│   │   └── macro_skills/          # Pydantic data models
│   │       ├── ux_models.py       # UX data schemas
│   │       ├── design_art_models.py # Design data schemas
│   │       ├── tech_models.py     # Technical data schemas
│   │       └── strategy_models.py # Strategy data schemas
│   ├── core/
│   │   └── config.py              # Configuration management
│   ├── db/
│   │   └── connection.py          # Database connections
│   └── main.py                    # FastAPI application entry point
├── requirements.txt               # Python dependencies
└── README.md                      # Backend documentation
```

### Frontend Organization

```
frontend/
├── src/
│   ├── index.tsx                 # Application entry point
│   ├── modules/
│   │   ├── auth/                 # Authentication module
│   │   │   └── login/
│   │   │       └── index.tsx
│   │   ├── dashboard/            # Dashboard module
│   │   │   └── index.tsx
│   │   ├── pipeline/             # Pipeline control module
│   │   │   └── index.tsx
│   │   ├── reports/              # Reports module
│   │   │   └── index.tsx
│   │   ├── macro_skills/         # Skill modules
│   │   │   ├── ux_skill/         # UX analysis UI
│   │   │   │   ├── UxAnalysisComponent.tsx
│   │   │   │   └── index.tsx
│   │   │   ├── design_art_skill/ # Design analysis UI
│   │   │   │   ├── DesignArtComponent.tsx
│   │   │   │   └── index.tsx
│   │   │   ├── tech_systems_skill/ # Technical analysis UI
│   │   │   │   ├── TechComponent.tsx
│   │   │   │   └── index.tsx
│   │   │   └── strategy_market_skill/ # Strategy analysis UI
│   │   │       ├── StrategyComponent.tsx
│   │   │       └── index.tsx
│   │   └── synthesis/            # Synthesis module
│   │       └── synthesis_skill/
│   │           ├── SynthesisComponent.tsx
│   │           └── index.tsx
│   ├── components/
│   │   ├── common/               # Shared components
│   │   │   ├── AnalysisCard.tsx  # Generic skill card
│   │   │   ├── LoadingSpinner.tsx # Loading states
│   │   │   └── ErrorBoundary.tsx # Error handling
│   │   └── charts/               # Visualization components
│   │       ├── BarChart.tsx      # Chart components
│   │       └── PieChart.tsx
│   ├── services/
│   │   └── api/                  # API service layers
│   │       ├── uxApi.ts         # UX API integration
│   │       ├── designApi.ts      # Design API integration
│   │       ├── techApi.ts       # Technical API integration
│   │       ├── strategyApi.ts   # Strategy API integration
│   │       └── synthesisApi.ts  # Synthesis API integration
│   └── types/
│       └── api/                  # TypeScript type definitions
│           ├── uxTypes.ts        # UX interfaces
│           ├── designTypes.ts    # Design interfaces
│           ├── techTypes.ts      # Technical interfaces
│           ├── strategyTypes.ts  # Strategy interfaces
│           └── synthesisTypes.ts # Synthesis interfaces
├── package.json                  # Frontend dependencies
└── README.md                     # Frontend documentation
```

### OpenSpec Structure

```
openspec/
├── changes/                      # Development change tracking
│   ├── register-open-specs/      # OpenSpec registration change
│   └── optimize-spec-detection/ # Spec detection optimization change
├── specs/
│   ├── macro_skills/            # Macro-skill specifications
│   │   ├── ux_skill.yaml        # UX analysis contract
│   │   ├── ux_skill.md          # UX analysis documentation
│   │   ├── design_art_skill.yaml # Design analysis contract
│   │   ├── design_art_skill.md # Design analysis documentation
│   │   ├── tech_systems_skill.yaml # Technical analysis contract
│   │   ├── tech_systems_skill.md # Technical analysis documentation
│   │   ├── strategy_market_skill.yaml # Strategy analysis contract
│   │   ├── strategy_market_skill.md # Strategy analysis documentation
│   │   └── README.md            # Macro-skill overview
│   ├── scraper/                  # Data collection specifications
│   │   ├── master_json_schema.yaml # Master data structure
│   │   ├── data_crud_contract.yaml # Data operations contract
│   │   ├── pre_scrap_contract.yaml # Pre-scraping contract
│   │   ├── scraper_contract.yaml   # Scraping engine contract
│   │   └── json_schema.md          # JSON schema documentation
│   ├── synthesis/                # Synthesis specifications
│   │   ├── synthesis_skill.yaml   # Synthesis engine contract
│   │   └── synthesis_skill.md     # Synthesis engine documentation
│   ├── ui_and_login/             # User interface specifications
│   │   ├── ui_login_contract.yaml # UI login contract
│   │   └── ui_login_contract.md  # UI login documentation
│   ├── root-spec.yaml            # Root specification
│   ├── spec.yaml                 # Main specification
│   └── spec-driven.yaml          # Spec-driven workflow configuration
└── config.yaml                    # OpenSpec project configuration
```

---

## 🎯 Development Focus Areas

### Backend Development Focus

Backend developers should concentrate on:

- **API Layer**: Developing RESTful endpoints following FastAPI patterns
- **Business Logic**: Implementing skill-specific analysis algorithms
- **Data Models**: Creating Pydantic models that match OpenSpec contracts
- **Database Integration**: PostgreSQL operations with SQLAlchemy ORM
- **Task Processing**: Celery-based background job implementation
- **Validation**: Input validation and output transformation according to specs

**Key Files:**
- `backend/app/main.py` - FastAPI application entry
- `backend/app/api/routes.py` - Main API router
- `backend/app/db/connection.py` - Database connection management
- `backend/app/core/config.py` - Environment configuration
- `backend/requirements.txt` - Python dependencies

### Frontend Development Focus

Frontend developers should concentrate on:

- **Module Architecture**: Creating reusable React components
- **State Management**: Implementing Redux-based state handling
- **API Integration**: Connecting backend services with frontend components
- **User Experience**: Building intuitive interfaces for each skill
- **Data Visualization**: Creating charts and analysis displays
- **Type Safety**: Ensuring TypeScript compliance with OpenSpec contracts

**Key Files:**
- `frontend/src/index.tsx` - React application entry
- `frontend/src/modules/auth/login/index.tsx` - Authentication module
- `frontend/src/modules/dashboard/index.tsx` - Main dashboard
- `frontend/src/modules/reports/index.tsx` - Reports interface
- `frontend/src/modules/pipeline/index.tsx` - Pipeline control interface
- `frontend/package.json` - JavaScript dependencies

### OpenSpec Integration

All developers must work with OpenSpec contracts located in:

- `openspec/specs/macro_skills/` - Four parallel analysis skill contracts
- `openspec/specs/synthesis/` - Synthesis engine contract
- `openspec/specs/scraper/` - Data collection contracts
- `openspec/specs/ui_and_login/` - User interface contract

---

## 🔄 Development Process

### Implementation Workflow

1. **Contract Analysis**: Review relevant OpenSpec specifications
2. **Environment Setup**: Install dependencies and validate contracts
3. **AI-Assisted Development**: Use AI agents to generate code based on contracts
4. **Local Testing**: Validate implementations against specifications
5. **Code Review**: Peer review of generated code
6. **Integration**: Merge to main deployment pipeline

### Quality Assurance

Before committing changes:

```bash
# Validate all OpenSpec contracts
openspec validate --all

# Run backend tests if you have
cd backend && python -m pytest

# Run frontend tests if you have
cd frontend && npm test

# Build validation
npm run build
```

### Deployment Strategy

The project follows a structured deployment approach:

1. **Development Branches**: Feature-specific work
2. **Integration Testing**: Validate cross-component compatibility  
3. **Staging Environment**: Production-like testing
4. **Production Deployment**: Code promotion through environments

---

## 📚 Additional Resources

### OpenSpec Documentation

- OpenSpec CLI reference: `openspec help`
- Available workflows: `openspec schemas`
- Validation documentation: `openspec help validate`

### API Documentation

Once the backend is running, access:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Development Standards

- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Maintain meaningful commit messages
- Document complex logic with inline comments
- Ensure all functionality is covered by tests

---

## Project Status

**Current Version**: 3.0.0  
**Development Phase**: Alpha - Core Architecture Complete  
**OpenSpec Validation**: All contracts verified and compliant  
**AI Workflow**: Ready for agent-assisted development  

The project is structured for rapid, spec-driven development with AI assistance. All contracts are validated and the development workflow is optimized for efficient team collaboration.
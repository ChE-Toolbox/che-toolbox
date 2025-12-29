# ChemEng Toolbox: Architecture (Open Source, Cost-Optimized)

## Project Overview

**ChemEng Toolbox** is an open-source platform providing Chemical Engineers with computational tools spanning thermodynamics, fluid mechanics, heat transfer, reaction engineering, and process design. The platform consists of:

1. **Python Library** — Open-source calculation engine (MIT license)
2. **Web Application** — Interactive calculators and visualizations
3. **Optional Self-Hosted API** — RESTful API for programmatic access

This architecture prioritizes **minimal costs** for development and hosting while remaining scalable for anyone who wants to deploy it publicly.

---

## Architecture Philosophy

### Core Principles

1. **Free Tier First** — Use only services with generous free tiers
2. **Serverless by Default** — No fixed costs, pay only for actual usage
3. **Simple Deployment** — Single developer can deploy in under 1 hour
4. **MIT Licensed** — All code and configurations are open source
5. **Data Freedom** — Only use public domain or openly licensed data sources

### Cost Targets

| Usage Level | Monthly Cost | Notes |
|-------------|--------------|-------|
| Development | $0 | Stays within AWS free tier |
| Light Personal Use | $0-5 | <100 calculations/day |
| Medium Personal Use | $5-20 | <1000 calculations/day |
| Small Public Deployment | $20-50 | <10k calculations/day |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USERS                                          │
│         Engineers │ Researchers │ Students │ Developers                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────────┐
        │   Static Site     │     │   Python Library      │
        │   (GitHub Pages)  │     │   (pip install)       │
        │   FREE            │     │   FREE                │
        └─────────┬─────────┘     └───────────────────────┘
                  │
                  │ (Optional)
                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OPTIONAL BACKEND (Self-Hosted)                         │
│                      AWS Lambda + API Gateway (Free Tier)                   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Thermodynamics  │       │ Fluid Mechanics │       │  Heat Transfer  │
│    Lambda       │       │    Lambda       │       │    Lambda       │
│    (Python)     │       │    (Python)     │       │    (Python)     │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────────────────┐
│                           SHARED INFRASTRUCTURE                              │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│   DynamoDB      │  S3 (Free Tier) │   CloudWatch    │   (Optional)          │
│ (Free Tier)     │  Reports, Logs  │   Basic Logs    │   Redis (Upstash)     │
│  User data      │                 │   FREE          │   FREE Tier           │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
```

---

## Component Details

### 1. Python Library (Core)

**Purpose:** Standalone calculation engine with no external dependencies except scientific libraries

**Technology Stack:**
- Python 3.11+
- NumPy, SciPy (computation)
- Pint (unit handling)
- Pure Python (no database required)

**Distribution:**
```bash
pip install chemeng-toolbox
```

**Usage:**
```python
from chemeng.thermo import PengRobinson

# All calculations work offline
eos = PengRobinson("methane")
result = eos.calculate(T=300, P=1e6)
print(f"Z factor: {result.Z}")
```

**Cost:** FREE (user's machine)

---

### 2. Static Web Application

**Purpose:** Browser-based calculators with visualization, no backend required

**Technology Stack:**
- Next.js (Static Site Generation)
- React + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (visualization)
- WASM (optional: run calculations in browser)

**Hosting:** GitHub Pages (FREE)

**Key Features:**
- All calculations run in browser (JavaScript port of Python library)
- No API calls required
- Offline-capable (PWA)
- Export to PDF/CSV (client-side)

**Build:**
```bash
npm run build
npm run export  # Generates static HTML/JS
```

**Deployment:**
```bash
git push origin main  # Auto-deploys via GitHub Actions
```

**Cost:** FREE

---

### 3. Optional Backend API (For Advanced Users)

**Purpose:** RESTful API for programmatic access, batch processing, saved calculations

**When to Deploy:**
- Want to save calculations to cloud
- Need server-side batch processing
- Building integrations with other tools

**Technology Stack:**
- AWS Lambda (1M free requests/month)
- API Gateway HTTP API (1M free requests/month)
- DynamoDB (25GB free storage, 25 RCU/WCU)
- S3 (5GB free storage)

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVERLESS API LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    API Gateway HTTP API (REST)                              │
│                    https://api.yourdomain.com                               │
│                                                                             │
│  Routes:                                                                    │
│  ├── POST /v1/thermo/eos/calculate                                          │
│  ├── POST /v1/fluids/pipe/pressure-drop                                     │
│  ├── POST /v1/heat/exchanger/design                                         │
│  └── POST /v1/batch/submit                                                  │
│                                                                             │
│                           ▼                                                 │
│                                                                             │
│  Lambda Functions (Python 3.11, ARM64)                                     │
│  ├── chemeng-thermo (512MB, 30s timeout)                                   │
│  ├── chemeng-fluids (256MB, 15s timeout)                                   │
│  └── chemeng-heat (256MB, 15s timeout)                                     │
│                                                                             │
│  Lambda Layers (Shared Dependencies):                                      │
│  ├── chemeng-core (library code)                                           │
│  └── scientific-libs (NumPy, SciPy)                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   DynamoDB      │       │       S3        │       │   CloudWatch    │
│                 │       │                 │       │                 │
│ Table: calcs    │       │ Bucket: reports │       │ Free tier logs  │
│ - user_id (PK)  │       │ - PDF exports   │       │                 │
│ - calc_id (SK)  │       │ - CSV data      │       │                 │
│ - inputs        │       │                 │       │                 │
│ - results       │       │                 │       │                 │
│                 │       │                 │       │                 │
│ FREE: 25GB      │       │ FREE: 5GB       │       │ FREE: 5GB       │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

### Free Tier Limits (AWS)

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Lambda | 1M requests/month, 400K GB-seconds | Enough for ~25K calculations/month |
| API Gateway | 1M requests/month (12 months) | After 12 months: $1/million |
| DynamoDB | 25GB storage, 25 RCU/WCU | Enough for thousands of saved calcs |
| S3 | 5GB storage, 20K GET, 2K PUT | Plenty for exports |
| CloudWatch | 5GB logs, 10 custom metrics | Basic monitoring |

**Expected Monthly Cost:**
- Month 1-12: $0 (free tier)
- Month 13+: $0-5 (depends on usage beyond free tier)

---

## Data Sources (Free & Open)

### Chemical Property Database

All data sources must be:
1. Public domain OR
2. Open license (CC0, CC-BY) OR
3. Government data (public)

**Approved Sources:**

| Source | License | Coverage | Priority |
|--------|---------|----------|----------|
| **NIST WebBook** | Public Domain (US Gov) | ~10,000 compounds | P0 |
| **CoolProp** | MIT | 122 fluids (high accuracy) | P0 |
| **IAPWS-IF97** | Public formulation | Water/steam properties | P0 |
| **PubChem** | Public Domain | Chemical identifiers | P1 |
| **JANAF Tables** | Public Domain | Thermochemical data | P2 |

**Excluded (Proprietary):**
- ❌ DIPPR (requires $$ license)
- ❌ Aspen Plus data
- ❌ ChemCAD databases

**Data Strategy:**
1. Start with NIST + CoolProp (~150 compounds)
2. Community contributions for additional compounds
3. Users can load custom data via JSON files

**Example Data File:**
```json
{
  "cas": "74-82-8",
  "name": "Methane",
  "formula": "CH4",
  "molecular_weight": 16.043,
  "critical_temperature": 190.564,
  "critical_pressure": 4599200,
  "acentric_factor": 0.0115,
  "source": "NIST WebBook",
  "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C74828"
}
```

---

## Code Organization (Monorepo)

```
chemeng-toolbox/
├── README.md
├── LICENSE (MIT)
├── packages/
│   ├── core/                      # Pure Python library
│   │   ├── chemeng_core/
│   │   │   ├── units.py
│   │   │   ├── validation.py
│   │   │   └── data/
│   │   │       └── chemicals.json  # NIST + CoolProp data
│   │   ├── pyproject.toml
│   │   └── tests/
│   │
│   ├── thermo/                     # Thermodynamics module
│   ├── fluids/                     # Fluid mechanics
│   ├── heat/                       # Heat transfer
│   └── ...
│
├── web/                            # Next.js static site
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   │       └── wasm/               # Browser-based calculations
│   ├── package.json
│   └── next.config.js
│
├── backend/                        # Optional Lambda functions
│   ├── functions/
│   │   ├── thermo/
│   │   │   ├── handler.py
│   │   │   └── requirements.txt
│   │   └── ...
│   │
│   └── template.yaml              # AWS SAM template
│
├── docs/                           # Documentation
│   ├── tutorials/
│   ├── api-reference/
│   └── theory/
│
└── scripts/
    ├── deploy-web.sh              # Deploy to GitHub Pages
    └── deploy-backend.sh          # Deploy to AWS (optional)
```

---

## Deployment Guide

### Option 1: Static Site Only (FREE, No Backend)

**Requirements:**
- GitHub account
- Node.js 20+

**Steps:**
1. Fork repository
2. Enable GitHub Pages in repo settings
3. Push to main branch
4. Site live at `https://yourusername.github.io/chemeng-toolbox`

**Cost:** $0/month

---

### Option 2: With Backend API (FREE Tier)

**Requirements:**
- AWS account (free tier)
- AWS CLI configured
- SAM CLI installed

**Steps:**
```bash
# 1. Clone repo
git clone https://github.com/yourusername/chemeng-toolbox.git
cd chemeng-toolbox

# 2. Deploy backend
cd backend
sam build
sam deploy --guided

# 3. Deploy frontend
cd ../web
npm install
npm run build
npm run deploy  # Pushes to GitHub Pages

# 4. Update frontend to use your API
# Edit web/.env.production:
# NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com
```

**Cost:** $0-5/month (depends on usage)

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Run Python library tests
cd packages/core
pytest tests/ --watch

# Terminal 2: Run web app
cd web
npm run dev  # http://localhost:3000

# Terminal 3 (optional): Run local Lambda
cd backend
sam local start-api  # http://localhost:3001
```

### AI-Assisted Development

This project is designed for AI-assisted coding:

**Recommended Tools:**
- **GitHub Copilot** (pair programming)
- **Claude** (architecture decisions, code review)
- **GPT-4** (documentation generation)

**AI-Friendly Practices:**
- Comprehensive docstrings in Python
- Type hints everywhere
- Self-documenting code structure
- Clear separation of concerns

**Example AI Prompts:**
```
"Implement the Peng-Robinson EOS in packages/thermo/chemeng_thermo/eos/peng_robinson.py
following the pattern in vanderwaals.py. Include validation tests."

"Create a React component for inputting fluid properties with unit conversion
using the pattern from components/calculators/InputForm.tsx"
```

---

## Testing Strategy

### Testing Pyramid

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TESTING PYRAMID                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────┐                                        │
│                             /       \                                       │
│                            /   E2E   \         ~5% (Playwright)            │
│                           /   Tests   \        Critical paths only          │
│                          ├─────────────┤                                    │
│                         /               \                                   │
│                        /  Integration    \     ~15% (pytest + vitest)      │
│                       /     Tests         \    API contracts                │
│                      ├─────────────────────┤                                │
│                     /                       \                               │
│                    /      Unit Tests         \  ~80% (fast feedback)       │
│                   /   (Pure functions)        \ pytest + vitest             │
│                  └─────────────────────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validation Testing

**Critical:** Chemical engineering calculations must be validated against literature.

```python
# Example: Validation test for Peng-Robinson EOS
# tests/thermo/test_peng_robinson_validation.py

import pytest
from chemeng_thermo.eos import PengRobinson

class TestPengRobinsonValidation:
    """
    Validation against published values.
    References:
    - Smith, Van Ness, Abbott - Intro to ChemE Thermodynamics
    - NIST WebBook
    """
    
    @pytest.mark.parametrize("compound,T_K,P_bar,Z_expected,source", [
        ("methane", 190.564, 45.99, 0.286, "SVA Table B.1"),
        ("ethane", 305.32, 48.72, 0.279, "SVA Table B.1"),
        ("propane", 369.83, 42.48, 0.276, "SVA Table B.1"),
    ])
    def test_compressibility_factor(self, compound, T_K, P_bar, Z_expected, source):
        """Validate Z factor against reference values."""
        pr = PengRobinson(compound)
        Z_calc = pr.compressibility_factor(T=T_K, P=P_bar*1e5)
        
        # Allow 0.5% deviation from reference
        assert abs(Z_calc - Z_expected) / Z_expected < 0.005, (
            f"Z factor for {compound}: "
            f"calculated={Z_calc:.4f}, expected={Z_expected:.4f} "
            f"(source: {source})"
        )
```

---

## CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          pip install -e "./packages/core[test]"
          pytest packages/ -v --cov

  test-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: |
          cd web
          npm ci
          npm run test
          npm run build

  deploy-web:
    needs: [test-python, test-web]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          cd web
          npm ci
          npm run build
          npm run export
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web/out

  # Optional: Deploy backend (only if AWS credentials are configured)
  deploy-backend:
    needs: [test-python]
    if: github.ref == 'refs/heads/main' && vars.DEPLOY_BACKEND == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/setup-sam@v2
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: |
          cd backend
          sam build
          sam deploy --no-confirm-changeset
```

**Cost:** FREE (GitHub Actions: 2000 minutes/month)

---

## Monitoring (Cost-Free)

### CloudWatch Free Tier

- 5GB logs per month
- 10 custom metrics
- 3 dashboards

### Simple Monitoring Setup

```python
# backend/functions/thermo/handler.py
import time

def handler(event, context):
    start = time.time()
    
    try:
        result = calculate(event)
        duration = time.time() - start
        
        # CloudWatch automatically logs
        print(f"SUCCESS duration={duration:.3f}s")
        return {"statusCode": 200, "body": result}
        
    except Exception as e:
        duration = time.time() - start
        print(f"ERROR duration={duration:.3f}s error={str(e)}")
        return {"statusCode": 500, "body": str(e)}
```

### CloudWatch Insights Queries (FREE)

```
# Find slow calculations
fields @timestamp, duration
| filter ispresent(duration)
| sort duration desc
| limit 10

# Error rate
fields @timestamp
| filter @message like /ERROR/
| stats count() as errors by bin(5m)
```

**Cost:** $0/month (within free tier)

---

## Security

### Minimal Security Checklist

✓ **API Gateway:** Built-in rate limiting (1000 req/sec)
✓ **Lambda:** IAM roles (least privilege)
✓ **DynamoDB:** Encryption at rest (default)
✓ **S3:** Private by default, presigned URLs for downloads
✓ **Secrets:** AWS Systems Manager Parameter Store (FREE)

### Authentication (Optional)

For public deployment, add simple auth:

```yaml
# backend/template.yaml
HttpApi:
  Auth:
    DefaultAuthorizer: AWS_IAM
```

Then use AWS Cognito (free tier: 50K MAU)

**Cost:** $0/month (under 50K users)

---

## Scaling Path

If the project grows beyond free tiers:

### Phase 1: Optimize Costs ($0 → $20/month)
- Use Lambda ARM64 (20% cheaper)
- Implement caching (Upstash Redis free tier)
- Optimize Lambda memory allocation
- Enable S3 Intelligent-Tiering

### Phase 2: Stay Serverless ($20 → $100/month)
- Add DynamoDB on-demand billing
- Use CloudFront CDN (free tier: 1TB/month)
- Consider Lambda@Edge for global latency

### Phase 3: Hybrid Architecture ($100+/month)
- Keep low-traffic endpoints on Lambda
- Move high-traffic endpoints to EC2 Spot Instances
- Consider Kubernetes only if traffic exceeds 10M requests/month

---

## Documentation Strategy

### Documentation Types

| Type | Tool | Hosting | Cost |
|------|------|---------|------|
| README | Markdown | GitHub | FREE |
| API Docs | FastAPI auto-gen | GitHub Pages | FREE |
| Tutorials | Jupyter Notebooks | nbviewer | FREE |
| Theory Docs | MkDocs | GitHub Pages | FREE |

### Example Documentation Structure

```
docs/
├── README.md                       # Quick start
├── installation.md
├── tutorials/
│   ├── 01-first-calculation.ipynb
│   ├── 02-unit-conversions.ipynb
│   └── 03-batch-processing.ipynb
├── api/
│   └── reference.md                # Auto-generated
├── theory/
│   ├── thermodynamics.md
│   ├── fluid-mechanics.md
│   └── equations-of-state.md
└── contributing.md
```

**Cost:** $0/month (GitHub Pages)

---

## Community Contributions

### Contribution Areas

1. **Chemical Data**
   - Add compounds to chemicals.json
   - Validate against literature
   - Cite sources

2. **Calculation Methods**
   - Implement new correlations
   - Add validation tests
   - Document assumptions

3. **Web Calculators**
   - Create new calculator UIs
   - Improve visualizations
   - Add examples

4. **Bug Fixes**
   - Fix calculation errors
   - Improve error messages
   - Add edge case handling

### Example: Adding a New Compound

```json
// packages/core/chemeng_core/data/chemicals.json
{
  "cas": "7664-41-7",
  "name": "Ammonia",
  "formula": "NH3",
  "molecular_weight": 17.031,
  "critical_temperature": 405.4,
  "critical_pressure": 11333000,
  "acentric_factor": 0.253,
  "source": "NIST WebBook",
  "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417",
  "contributor": "github.com/username",
  "date_added": "2025-01-15"
}
```

---

## Success Metrics

### Open Source Success

| Metric | Year 1 Target | How to Measure |
|--------|---------------|----------------|
| GitHub Stars | 100 | GitHub insights |
| PyPI Downloads | 1,000/month | pypistats.org |
| Contributors | 5 | GitHub contributors |
| Issues Closed | 80% within 7 days | GitHub issues |
| Documentation Coverage | 100% of API | docs.rs style |

### Technical Quality

| Metric | Target | Tool |
|--------|--------|------|
| Test Coverage | >80% | pytest-cov |
| Type Coverage | 100% | mypy --strict |
| Validation Tests | 100% of correlations | Custom suite |
| Build Success Rate | >95% | GitHub Actions |

---

## License & Attribution

**License:** MIT License

**Why MIT?**
- Maximum reusability
- Compatible with most open source projects
- Allows commercial use
- No copyleft requirements

**Data Attribution:**
All data sources properly attributed in:
1. Source code docstrings
2. chemicals.json metadata
3. docs/data-sources.md
4. Web UI (tooltip on hover)

**Example Attribution:**
```python
class PengRobinson:
    """
    Peng-Robinson equation of state (1976).
    
    Reference:
        Peng, D.-Y., Robinson, D.B. (1976). 
        "A New Two-Constant Equation of State"
        Ind. Eng. Chem. Fundam. 15(1), 59-64.
        DOI: 10.1021/i160057a011
        
    Critical property data from:
        NIST Chemistry WebBook, NIST Standard Reference Database Number 69
        https://webbook.nist.gov/
        Public Domain (U.S. Government Work)
    """
```

---

## Roadmap

**Note:** Timeline is flexible and based on available development time.

### v0.1 (MVP)
- [ ] Core library with 3 modules (thermo, fluids, heat)
- [ ] 20 most common calculations
- [ ] Basic web UI
- [ ] GitHub Pages deployment
- [ ] Documentation site

### v0.2
- [ ] Add reactions module
- [ ] Add separations module
- [ ] Additional validated calculations
- [ ] Interactive visualizations
- [ ] Python SDK published to PyPI

### v0.3
- [ ] Optional backend API (Lambda)
- [ ] Enhanced web features
- [ ] Export functionality
- [ ] Mobile-responsive design

### v1.0
- [ ] Complete core modules
- [ ] Comprehensive validation suite
- [ ] Stable API
- [ ] Full documentation
- [ ] Community contributions accepted

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data licensing issues | Low | Critical | Only use public domain sources |
| Calculation errors | Medium | High | Extensive validation tests |
| AWS costs exceed free tier | Low | Medium | Monitor with budget alerts |
| Low adoption | Medium | Low | Focus on quality, SEO |
| Developer burnout | High | High | Scope control, AI assistance |

### Contingency Plans

1. **If AWS free tier expires:**
   - Migrate to Vercel (serverless functions included)
   - Use Supabase (free PostgreSQL + auth)
   - Consider fly.io (free tier)

2. **If development is too slow:**
   - Focus on MVP (thermo + fluids only)
   - Accept community PRs earlier
   - Use AI for boilerplate code

3. **If data sources become unavailable:**
   - NIST is stable (government)
   - CoolProp is MIT licensed
   - Community can contribute data

---

## Getting Started

### Phase 1: Project Setup
```bash
# 1. Create repo
gh repo create chemeng-toolbox --public --license=mit

# 2. Setup Python project
cd packages/core
poetry init
poetry add numpy scipy pint

# 3. Setup web project
cd ../../web
npx create-next-app@latest .

# 4. First commit
git add .
git commit -m "Initial commit"
git push
```

### Phase 2: Core Library
- Implement critical calculations
- Write validation tests
- Publish to PyPI

### Phase 3: Web Interface
- Build calculators
- Add visualizations
- Deploy to GitHub Pages

### Phase 4: Iterate
- Add features based on priorities
- Accept community contributions
- Improve documentation

---

## Summary

This architecture provides:

1. **$0 monthly cost** for development
2. **Open source** (MIT) with clear data provenance
3. **Simple deployment** (1 command to GitHub Pages)
4. **Scalable** (can grow to handle serious traffic)
5. **AI-friendly** (clear structure for code generation)

The focus is on **building a useful tool** without worrying about infrastructure, costs, or team coordination. The architecture scales from solo laptop development to public deployment without major rewrites.

**Next Steps:**
1. Clone repo template
2. Implement first calculation (Peng-Robinson EOS)
3. Create first web calculator
4. Deploy to GitHub Pages
5. Share on Reddit /r/ChemicalEngineering

Total time to working prototype: **~40 hours of coding**

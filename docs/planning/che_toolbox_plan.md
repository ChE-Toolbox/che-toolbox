# ChemEng Toolbox: Project Plan (Open Source)

## Executive Summary

**ChemEng Toolbox** is an open-source platform (MIT License) providing Chemical Engineers with computational tools spanning thermodynamics, fluid mechanics, heat transfer, reaction engineering, and process design. This project is optimized for:

- **Zero ongoing costs** (free tier hosting)
- **AI-assisted development** (designed for code generation tools)
- **Community contributions** (clear structure for PRs)
- **Educational use** (students and researchers)

The platform provides:
1. **Python Library** — Standalone calculation engine (`pip install chemeng-toolbox`)
2. **Static Web App** — Interactive calculators (GitHub Pages)
3. **Optional API** — Self-hosted backend for advanced features (AWS free tier)

---

## Project Principles

### Core Values

1. **Open Source First** — MIT license, all code public
2. **Cost-Free Operation** — Use only free hosting tiers
3. **Data Freedom** — Only public domain or openly licensed data
4. **Developer Productivity** — Clear structure, AI-assisted development
5. **Quality Over Speed** — Validated calculations, good documentation

### Non-Goals

- ❌ Commercial hosting (no funding)
- ❌ 24/7 availability guarantees
- ❌ Enterprise features (SSO, SLAs)
- ❌ Real-time collaboration
- ❌ Mobile apps (web is enough)

---

## Part 1: Capability Matrix

### 1.1 Core Engineering Domains

| Domain | Python Library | Web App | API (Optional) | Priority |
|--------|----------------|---------|----------------|----------|
| **Thermodynamics** | ✓ | ✓ | ✓ | P0 |
| **Fluid Mechanics** | ✓ | ✓ | ✓ | P0 |
| **Heat Transfer** | ✓ | ✓ | ✓ | P0 |
| **Reaction Engineering** | ✓ | ✓ | ✓ | P1 |
| **Separations** | ✓ | ✓ | ✓ | P1 |
| **Equipment Sizing** | ✓ | ✓ | ✓ | P1 |
| **Process Economics** | ✓ | ✓ | ✓ | P2 |
| **Safety Analysis** | ✓ | ✓ | ✓ | P2 |

### 1.2 MVP Feature Set (v0.1)

**Thermodynamics:**
- Ideal Gas Law
- Van der Waals EOS
- Peng-Robinson EOS
- Steam Tables (IAPWS-IF97)
- Basic flash calculations

**Fluid Mechanics:**
- Pipe pressure drop (Darcy-Weisbach)
- Reynolds number calculator
- Pump head calculations
- Valve Cv sizing

**Heat Transfer:**
- LMTD method
- NTU-effectiveness method
- Convection correlations (common geometries)
- Insulation sizing

**Total MVP:** ~20 calculations, validated against literature

---

## Part 2: Data Strategy

### 2.1 Approved Data Sources

| Source | License | Coverage | Use Case |
|--------|---------|----------|----------|
| **NIST WebBook** | Public Domain | 10,000+ compounds | Critical properties, thermodynamic data |
| **CoolProp** | MIT | 122 fluids | High-accuracy fluid properties |
| **IAPWS-IF97** | Public formulation | Water/steam | Steam tables |
| **PubChem** | Public Domain | Chemical identifiers | CAS numbers, formulas |
| **JANAF Tables** | Public Domain | Thermochemical data | Heat capacity, enthalpy |

### 2.2 Data File Structure

```json
{
  "cas": "74-82-8",
  "name": "Methane",
  "formula": "CH4",
  "molecular_weight": 16.043,
  "critical_temperature": 190.564,
  "critical_pressure": 4599200,
  "critical_volume": 0.0000986,
  "acentric_factor": 0.0115,
  "ideal_gas_heat_capacity": {
    "equation": "shomate",
    "coefficients": [33.298, -0.0791, 0.000202, 0, -0.00000102],
    "valid_range": [298, 1300],
    "units": "J/mol/K"
  },
  "antoine_coefficients": {
    "A": 3.9895,
    "B": 443.028,
    "C": -0.49,
    "valid_range": [91, 190],
    "units": "log10(P_bar)"
  },
  "source": "NIST Chemistry WebBook",
  "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C74828",
  "retrieved": "2025-01-15",
  "validated_by": "github.com/username"
}
```

### 2.3 Community Contributions

Users can contribute data via pull requests:

**Contribution Requirements:**
1. Source must be public domain or openly licensed
2. Include source URL
3. Add validation test comparing to source
4. Document units and valid ranges

**Example PR:**
```
Title: Add ammonia thermodynamic properties

- Added NH3 to chemicals.json
- Source: NIST WebBook (public domain)
- Added validation test comparing Cp(T) to NIST data
- Accuracy: <0.1% deviation from 300-1000K
```

---

## Part 3: Technology Stack

### 3.1 Python Library

```python
# Minimal dependencies
numpy>=1.24.0
scipy>=1.10.0
pint>=0.20.0      # Unit handling
```

**Design Principles:**
- Pure Python (no C extensions for portability)
- Type hints everywhere (mypy --strict)
- Comprehensive docstrings (Google style)
- No external API calls (offline-first)

**Example Usage:**
```python
from chemeng.thermo import PengRobinson

# Load data from local JSON file
pr = PengRobinson("methane")

# All calculations offline
result = pr.calculate(T=300, P=1e6)
print(f"Z = {result.Z:.4f}")
print(f"Fugacity = {result.fugacity:.2f} Pa")
```

### 3.2 Web Application

**Framework:** Next.js 14 (Static Site Generation)

**Key Libraries:**
```json
{
  "next": "14.x",
  "react": "18.x",
  "typescript": "5.x",
  "tailwindcss": "3.x",
  "recharts": "2.x",
  "jspdf": "2.x",
  "zustand": "4.x"
}
```

**Architecture:**
- Static site generation (no server required)
- All calculations in browser (WASM or JS port)
- Offline-capable (PWA)
- Export to PDF/CSV client-side

### 3.3 Optional Backend

**When to deploy:**
- Want cloud-saved calculations
- Need batch processing
- Building integrations

**Technology:**
- AWS Lambda (Python 3.11, ARM64)
- API Gateway HTTP API
- DynamoDB (on-demand billing)
- S3 (standard storage)

**Cost:** $0-5/month (free tier)

---

## Part 4: Development Workflow

### 4.1 Development Setup

**Daily Workflow:**
```bash
# Morning: Review open issues
gh issue list --state open

# Code new feature with AI assistance
# (Use GitHub Copilot, Claude, GPT-4)

# Test locally
pytest packages/core/tests/ -v

# Commit with conventional commits
git commit -m "feat(thermo): add SRK equation of state"

# Push triggers CI
git push origin feature/srk-eos

# Create PR (AI generates description)
gh pr create --fill
```

**Time Estimates:**
- New calculation: 2-4 hours
- Web calculator UI: 1-2 hours
- Validation tests: 1-2 hours
- Documentation: 1 hour

**Weekly Target:** 1-2 new calculations + tests + docs

### 4.2 AI-Assisted Development

**Effective AI Prompts:**

```
"Implement the Soave-Redlich-Kwong equation of state in 
packages/thermo/chemeng_thermo/eos/srk.py following the 
pattern in peng_robinson.py. Include:
- Class with calculate() method
- Pydantic validation
- Comprehensive docstrings with references
- Type hints"

"Create validation tests in tests/thermo/test_srk_validation.py 
comparing to the following literature values:
[paste values from SVA textbook]"

"Generate a React calculator component for SRK EOS in 
web/src/components/calculators/SRKCalculator.tsx using 
the pattern from PengRobinsonCalculator.tsx"
```

**AI Code Review Checklist:**
- [ ] Type hints present?
- [ ] Docstrings complete?
- [ ] Edge cases handled?
- [ ] Units documented?
- [ ] Validation test included?
- [ ] Source cited?

### 4.3 Testing Strategy

**Test Categories:**

1. **Unit Tests** (80% of tests)
   - Pure function testing
   - Edge case handling
   - Input validation

2. **Validation Tests** (15% of tests)
   - Compare to literature values
   - Source attribution required
   - Acceptable deviation documented

3. **Integration Tests** (5% of tests)
   - API contracts
   - End-to-end workflows

**Example Test:**
```python
import pytest
from chemeng.thermo import PengRobinson

class TestPengRobinsonValidation:
    """
    Validation against Smith, Van Ness, Abbott (7th ed)
    Table B.1: Critical Properties and Acentric Factors
    """
    
    @pytest.mark.parametrize("compound,T,P,Z_expected", [
        ("methane", 190.564, 4.5992e6, 0.286),   # Critical point
        ("ethane", 305.32, 4.8722e6, 0.279),
    ])
    def test_compressibility_at_critical(self, compound, T, P, Z_expected):
        pr = PengRobinson(compound)
        Z_calc = pr.calculate(T=T, P=P).Z
        assert abs(Z_calc - Z_expected) < 0.01  # 1% tolerance
```

---

## Part 5: Implementation Roadmap

**Note:** Timeline estimates are approximate and subject to available development time.

### Phase 0: Foundation

```
Week 1: Project Setup
──────────────────────
□ Create GitHub repo (MIT license)
□ Setup Python package structure
□ Configure pytest, mypy, black
□ Setup GitHub Actions CI
□ Create chemicals.json with 10 compounds

Week 2: First Calculation
─────────────────────────
□ Implement Peng-Robinson EOS
□ Add validation tests (vs NIST)
□ Write comprehensive docs
□ Create example Jupyter notebook
```

**Deliverable:** Working Python package with 1 validated calculation

---

### Phase 1: Core Library (Week 3-8)

```
Week 3-4: Thermodynamics Module
───────────────────────────────
□ Van der Waals EOS
□ Ideal Gas Law
□ Steam tables (IAPWS-IF97)
□ Basic flash calculation
□ 5 validation tests

Week 5-6: Fluid Mechanics Module
────────────────────────────────
□ Pipe pressure drop
□ Reynolds/friction factor
□ Pump sizing
□ Valve Cv calculations
□ 4 validation tests

Week 7-8: Heat Transfer Module
──────────────────────────────
□ LMTD method
□ NTU-effectiveness
□ Convection correlations (5 geometries)
□ Insulation sizing
□ 4 validation tests
```

**Deliverable:** Python library with 20 calculations, published to PyPI

---

### Phase 2: Web Application (Week 9-12)

```
Week 9: Web Framework Setup
───────────────────────────
□ Initialize Next.js project
□ Setup Tailwind + shadcn/ui
□ Create reusable calculator components
□ Deploy to GitHub Pages

Week 10-11: Core Calculators
────────────────────────────
□ EOS calculator (3 models)
□ Pipe flow calculator
□ Heat exchanger calculator
□ Steam properties calculator
□ Add charts (Recharts)

Week 12: Polish & Documentation
───────────────────────────────
□ Responsive design (mobile)
□ Add examples for each calculator
□ Create tutorial videos
□ SEO optimization
```

**Deliverable:** Static website with 5 working calculators

---

### Phase 3: Optional Backend (Week 13-14)

```
Week 13: Lambda Functions
─────────────────────────
□ SAM template configuration
□ Implement 3 Lambda functions
□ Setup DynamoDB table
□ Configure API Gateway

Week 14: API Features
────────────────────
□ Save calculation history
□ Batch processing endpoint
□ PDF report generation
□ API documentation
```

**Deliverable:** Optional self-hosted API (AWS free tier)

---

### Phase 4: Community & Growth (Week 15+)

```
Ongoing Tasks
─────────────
□ Accept community PRs
□ Add requested calculations
□ Improve documentation
□ Create video tutorials
□ Write blog posts
□ Share on Reddit, HN, Twitter
```

---

## Part 6: Documentation

### 6.1 Documentation Structure

```
docs/
├── README.md                          # Quick start
├── installation.md
├── tutorials/
│   ├── 01-installation.md
│   ├── 02-first-calculation.ipynb
│   ├── 03-unit-conversions.ipynb
│   ├── 04-batch-processing.ipynb
│   └── 05-custom-data.ipynb
├── api/
│   ├── thermo.md                      # Auto-generated
│   ├── fluids.md
│   └── heat.md
├── theory/
│   ├── equations-of-state.md
│   ├── phase-equilibrium.md
│   └── dimensionless-numbers.md
├── data-sources.md                    # Attribution
└── contributing.md
```

### 6.2 Documentation Tools

| Type | Tool | Hosting |
|------|------|---------|
| README | Markdown | GitHub |
| API Reference | pdoc3 | GitHub Pages |
| Tutorials | Jupyter | nbviewer.org |
| Theory Docs | MkDocs | GitHub Pages |

**Cost:** $0 (all free hosting)

### 6.3 Example Theory Documentation

```markdown
# Peng-Robinson Equation of State

## Mathematical Formulation

The Peng-Robinson EOS (1976) is:

$$P = \frac{RT}{V-b} - \frac{a(T)}{V(V+b)+b(V-b)}$$

where:
- $a(T) = 0.45724 \frac{R^2T_c^2}{P_c}\alpha(T)$
- $b = 0.07780 \frac{RT_c}{P_c}$
- $\alpha(T) = [1+\kappa(1-\sqrt{T_r})]^2$
- $\kappa = 0.37464 + 1.54226\omega - 0.26992\omega^2$

## Applicability

| System | Accuracy | Recommendation |
|--------|----------|----------------|
| Light hydrocarbons | Excellent | Recommended |
| Heavy hydrocarbons | Good | Use volume translation |
| Polar compounds | Fair | Consider activity models |

## Implementation

```python
from chemeng.thermo import PengRobinson

pr = PengRobinson("methane")
result = pr.calculate(T=300, P=1e6)
print(f"Z = {result.Z:.4f}")
```

## References

1. Peng, D.-Y., Robinson, D.B. (1976). *Ind. Eng. Chem. Fundam.* 15(1), 59-64.
2. Smith, Van Ness, Abbott (2005). *Intro to ChemE Thermodynamics*, 7th ed.
```

---

## Part 7: Community Building

### 7.1 Target Audiences

1. **Students** (primary)
   - Chemical engineering students
   - Homework help
   - Learning thermodynamics

2. **Practicing Engineers**
   - Quick calculations
   - Verify spreadsheets
   - Process design

3. **Educators**
   - Teaching tool
   - Assignment generation
   - Demonstration

4. **Researchers**
   - Literature comparisons
   - Method validation
   - Data extraction

### 7.2 Community Engagement

**Launch Strategy:**
```
Initial Launch
──────────────
- Publish to GitHub and PyPI
- Share on relevant communities
- Create documentation site

Ongoing Promotion (as time permits)
───────────────────────────────────
- Share updates with community
- Engage with feedback
- Submit to relevant directories

Maintenance
───────────
- Respond to issues on best-effort basis
- Review PRs when available
- Document features and updates
- Highlight community contributions
```

### 7.3 Contributor Guidelines

**Good First Issues:**
- Add new compound to chemicals.json
- Fix typo in documentation
- Add example to existing calculator
- Improve error messages

**Medium Issues:**
- Implement new correlation
- Add validation test
- Create new web calculator UI
- Translate documentation

**Advanced Issues:**
- New module (e.g., process control)
- WASM compilation
- Performance optimization
- Mobile app (React Native)

---

## Part 8: Success Metrics

### 8.1 Year 1 Targets

| Metric | Target (Aspirational) | Measurement |
|--------|--------|-------------|
| GitHub Stars | 50+ | GitHub insights |
| PyPI Downloads | 100+/month | pypistats.org |
| Website Visitors | 1K+/month | Analytics (if enabled) |
| Calculations | 50+ | Feature count |
| Test Coverage | >80% | pytest-cov |
| Documentation | 100% | Manual review |

### 8.2 Quality Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Type Coverage | 100% | mypy --strict |
| Test Coverage | >80% | pytest-cov |
| Validation Tests | 100% of correlations | Custom |
| Build Success | >95% | GitHub Actions |
| Response Time | <24h | GitHub issues |

---

## Part 9: Risk Management

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Calculation errors | Medium | Critical | Extensive validation tests |
| Data licensing issues | Low | Critical | Only use public domain sources |
| AWS costs exceed free tier | Low | Low | Budget alerts, stay under limits |
| Developer burnout | High | Medium | Scope control, take breaks |
| Low adoption | Medium | Low | Focus on quality over quantity |

### 9.2 Contingency Plans

**If development becomes overwhelming:**
- Focus on core 3 modules only (thermo, fluids, heat)
- Accept "good enough" over "perfect"
- Use more AI assistance
- Open to co-maintainers after 6 months

**If AWS free tier expires:**
- Static site only (no backend)
- Migrate to Vercel/Netlify
- Community can self-host

**If data sources become unavailable:**
- NIST WebBook is stable (government)
- CoolProp is MIT licensed
- Community contributions fill gaps

---

## Part 10: Cost Analysis

### 10.1 Development Costs

| Item | Cost | Notes |
|------|------|-------|
| GitHub | $0 | Free for public repos |
| Domain (optional) | $12/year | Not required, can use github.io |
| AWS (development) | $0 | Free tier |
| AI Tools (optional) | $20/month | GitHub Copilot |
| **Total** | **$0-20/month** | |

### 10.2 Hosting Costs

**Free Tier Option (Recommended):**
- GitHub Pages: Web hosting
- AWS Lambda: 1M requests/month
- DynamoDB: 25GB storage
- **Total: $0/month**

**Paid Option (if needed):**
- Custom domain: $12/year
- Vercel Pro: $20/month (if exceed GH Pages limits)
- AWS beyond free tier: ~$5/month
- **Total: ~$25-35/month**

### 10.3 Time Investment

**Initial Development (MVP):**
- Setup: 8 hours
- Core library: 120 hours
- Web application: 80 hours
- Documentation: 40 hours
- Testing: 60 hours
- **Total: ~300 hours (~2 months part-time)**

**Maintenance:**
- ~10 hours/week (bug fixes, PRs, issues)
- ~20 hours/month new features

---

## Part 11: License & Legal

### 11.1 MIT License

**Why MIT?**
- Most permissive
- Compatible with other open source
- Allows commercial use
- Simple and clear

**License Text:**
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Standard MIT license continues...]
```

### 11.2 Data Attribution

**All data sources must be attributed:**

```python
"""
Critical property data from NIST Chemistry WebBook,
NIST Standard Reference Database Number 69
https://webbook.nist.gov/
Public Domain (U.S. Government Work)

Equation of state formulation from:
Peng, D.-Y., Robinson, D.B. (1976).
Ind. Eng. Chem. Fundam. 15(1), 59-64.
DOI: 10.1021/i160057a011
"""
```

### 11.3 Contributor License

**Simple CLA (Contributor License Agreement):**
```
By submitting a pull request, you agree that:
1. Your contribution is your original work
2. You grant the project a perpetual, worldwide license to use your contribution
3. Your contribution does not violate any third-party rights
```

---

## Part 12: Getting Started

### 12.1 Quick Start for New Contributors

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/chemeng-toolbox.git
cd chemeng-toolbox

# 2. Setup Python environment
cd packages/core
pip install -e ".[dev]"

# 3. Run tests
pytest tests/ -v

# 4. Make changes
# ... edit code ...

# 5. Test changes
pytest tests/ -v
mypy chemeng_core/

# 6. Create PR
git checkout -b feature/my-feature
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### 12.2 Project Kanban Board

**GitHub Projects Board:**

**Backlog:**
- [ ] Add CO2 properties
- [ ] Implement NRTL model
- [ ] Create distillation calculator
- [ ] Add mobile optimization

**In Progress:**
- [ ] SRK equation of state
- [ ] Pipe flow calculator UI

**Review:**
- [ ] PR: Add ethanol properties

**Done:**
- [x] Peng-Robinson EOS
- [x] Steam tables
- [x] Basic web UI

---

## Summary

This project plan provides:

1. **Clear scope** — 8 modules, ~200 calculations
2. **Solo-friendly** — AI-assisted development
3. **Cost-free** — Leverage free tiers
4. **Open source** — MIT license, community-driven
5. **Quality focus** — Validation tests for all calculations

**Next Steps:**
1. Create GitHub repo
2. Implement first calculation (Peng-Robinson)
3. Add validation tests
4. Create simple web UI
5. Deploy to GitHub Pages
6. Share with community

**Estimated time to MVP:** 2-3 months part-time

**Long-term vision:** The go-to open-source ChemE calculation library

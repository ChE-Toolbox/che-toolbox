# ChemEng Toolbox: Planning Documents

## Project Overview

**ChemEng Toolbox** is an open-source (MIT License) platform providing Chemical Engineers with computational tools for thermodynamics, fluid mechanics, heat transfer, and more.

**Key Principles:**
- ✅ Open source (MIT License)
- ✅ Cost-free hosting (GitHub Pages + AWS free tier)
- ✅ Developer friendly (AI-assisted development)
- ✅ Public domain data only (NIST, CoolProp, IAPWS)
- ✅ Validated calculations (tested against literature)

**NOT Goals:**
- ❌ Commercial hosting
- ❌ Production SLA guarantees
- ❌ Enterprise features (SSO, 24/7 support, SLAs)
- ❌ Real-time collaboration features

---

## Document Structure

### 1. [che_toolbox_plan.md](che_toolbox_plan.md)
**Main planning document**
- Project principles and scope
- Feature matrix (8 modules, ~200 calculations)
- Data strategy (public domain sources only)
- Development workflow (AI-assisted development)
- Implementation roadmap (MVP in 2-3 months)
- Community contribution guidelines
- Success metrics

**Read this first** to understand the project vision and scope.

---

### 2. [che_toolbox_architecture.md](che_toolbox_architecture.md)
**System architecture (cost-optimized)**
- Three-tier deployment: Python library → Static web → Optional API
- Free tier architecture (GitHub Pages + AWS Lambda)
- Cost breakdown ($0/month for static, $0-5/month with backend)
- Technology stack (Next.js, Python 3.11, AWS SAM)
- Data sources (NIST, CoolProp, IAPWS)
- Monitoring and observability (CloudWatch free tier)

**Key Decision:** Consolidated from two architecture documents, keeping only the cost-optimized serverless approach.

---

### 3. [che_toolbox_deployment.md](che_toolbox_deployment.md)
**Deployment guide**
- Option 1: Static site only (FREE, GitHub Pages)
- Option 2: With backend API (AWS free tier, $0-5/month)
- Step-by-step deployment instructions
- Infrastructure as code (AWS SAM templates)
- Cost monitoring and budget alerts
- Troubleshooting guide
- Disaster recovery procedures

**Use this** when you're ready to deploy the application.

---

### 4. [che_toolbox_additional.md](che_toolbox_additional.md)
**Additional considerations**
- Testing strategy (80% unit, 15% validation, 5% integration)
- Validation testing examples (compare to literature)
- Security considerations (authentication, rate limiting)
- Documentation strategy (MkDocs, Jupyter, FastAPI auto-docs)
- Community contribution guide
- Success metrics and risk mitigation
- Future roadmap

**Reference this** for detailed implementation guidance.

---

## Quick Start

### For Developers

```bash
# 1. Clone/create repo
git clone https://github.com/yourusername/chemeng-toolbox.git
cd chemeng-toolbox

# 2. Setup Python environment
cd packages/core
pip install -e ".[dev]"

# 3. Run tests
pytest tests/ -v

# 4. Start web dev
cd ../../web
npm install
npm run dev

# 5. Deploy when ready
npm run deploy  # Pushes to GitHub Pages
```

### For Contributors

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/chemeng-toolbox.git

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes, test, commit
pytest tests/ -v
git commit -m "feat: add my feature"

# 4. Push and create PR
git push origin feature/my-feature
gh pr create --fill
```

---

## Technology Stack Summary

**Core Library:**
- Python 3.11+
- NumPy, SciPy (scientific computing)
- Pint (unit handling)
- Pydantic (validation)

**Web Application:**
- Next.js 14 (static site generation)
- React + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (visualization)

**Optional Backend:**
- AWS Lambda (Python 3.11, ARM64)
- API Gateway HTTP API
- DynamoDB (on-demand billing)
- S3 (standard storage)

**Hosting:**
- GitHub Pages (web, FREE)
- AWS free tier (API, $0-5/month)

**CI/CD:**
- GitHub Actions (FREE: 2000 min/month)

---

## Cost Breakdown

### Static Site Only (Recommended for Start)

| Service | Cost |
|---------|------|
| GitHub Pages | $0 |
| Domain (optional) | $12/year |
| **Total** | **$0-1/month** |

### With Backend API (Optional)

| Service | Free Tier | Expected Usage | Monthly Cost |
|---------|-----------|----------------|--------------|
| Lambda | 1M requests | ~25K requests | $0 |
| API Gateway | 1M requests (12mo) | ~25K requests | $0 (then $0.03) |
| DynamoDB | 25GB, 25 RCU/WCU | ~1GB, <5 ops | $0 |
| S3 | 5GB, 20K GET | ~500MB | $0 |
| CloudWatch | 5GB logs | ~100MB | $0 |
| **Total** | | | **$0/month** |

---

## Data Sources (All Public Domain)

| Source | License | Coverage | Use |
|--------|---------|----------|-----|
| NIST WebBook | Public Domain | 10K+ compounds | Critical properties |
| CoolProp | MIT | 122 fluids | Fluid properties |
| IAPWS-IF97 | Public | Water/steam | Steam tables |
| PubChem | Public Domain | Identifiers | CAS numbers |
| JANAF Tables | Public Domain | Thermochemical | Heat capacity |

**Note:** Only public domain or openly licensed data is used. No proprietary databases (DIPPR, Aspen, etc.).

---

## Key Features

### Python Library
```python
from chemeng.thermo import PengRobinson

pr = PengRobinson("methane")
result = pr.calculate(T=300, P=1e6)
print(f"Z = {result.Z:.4f}")
```

### Web Application
- Interactive calculators
- Unit conversion
- Visualization (charts)
- Export to PDF/CSV
- Offline capable (PWA)

### Optional API
```bash
curl -X POST https://api.example.com/v1/thermo/eos/calculate \
  -H "Content-Type: application/json" \
  -d '{"model": "peng_robinson", "compound": "methane", ...}'
```

---

## Development Roadmap

### Phase 1: MVP
- Core library (thermo, fluids, heat)
- 20 validated calculations
- Basic web UI
- GitHub Pages deployment

### Phase 2: Expand
- Add reactions, separations
- Additional validated calculations
- Interactive charts
- PyPI package

### Phase 3: Polish
- Optional backend API
- More calculation modules
- Mobile responsive
- Export functionality

### Phase 4: v1.0
- Complete core modules
- Comprehensive test coverage
- Full documentation
- Stable API

---

## Success Metrics

**Technical Quality:**
- Test coverage: >80%
- Type coverage: 100% (mypy --strict)
- Validation tests: 100% of calculations
- Build success: >95%

**Community (Aspirational):**
- GitHub stars: 50+ (Year 1)
- PyPI downloads: 100+/month
- Issue response: Best effort
- Active maintenance

---

## Contributing

See [che_toolbox_additional.md](che_toolbox_additional.md#community-contributions) for detailed contribution guidelines.

**Quick Contribution:**
1. Fork repo
2. Add feature/fix bug
3. Write tests
4. Submit PR
5. Maintainer will review on best-effort basis

---

## License

MIT License - see LICENSE file

**Why MIT?**
- Most permissive
- Allows commercial use
- Compatible with other open source
- Simple and clear

---

## Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

**Response Time:** Best effort (personal project)

---

## Roadmap

See [che_toolbox_plan.md](che_toolbox_plan.md#part-11-future-roadmap) for detailed roadmap.

**Next Steps:**
1. ✅ Planning documents complete
2. ⬜ Create GitHub repo
3. ⬜ Implement first calculation (Peng-Robinson)
4. ⬜ Build simple web UI
5. ⬜ Deploy to GitHub Pages

---

## Changes from Original Plans

**Optimized for open-source personal project:**

1. **AI-assisted development** → Leverage AI tools for productivity
2. **Zero cost priority** → Free tier hosting only
3. **Public domain data** → No proprietary data sources (DIPPR, etc.)
4. **Simple architecture** → Serverless/static only, no Kubernetes
5. **Focused scope** → Core engineering calculations, no enterprise features
6. **Best-effort support** → Realistic community engagement expectations

**Cost target:** $0/month (static deployment) or $0-5/month (with optional API)

---

## Questions?

Open an issue or discussion on GitHub!

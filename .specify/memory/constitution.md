<!--
Sync Impact Report:
Version: 0.1.0 → 1.0.0
Rationale: MAJOR version - Initial constitution ratification, establishing core governance framework

Modified Principles:
- NEW: All core principles established (I-VII)
- NEW: Technical constraints defined
- NEW: Quality standards established
- NEW: Governance rules created

Added Sections:
- Core Principles (7 principles)
- Technical Constraints
- Development Workflow
- Governance

Removed Sections: None

Templates Status:
✅ .specify/templates/plan-template.md - Constitution Check section aligns with new principles
✅ .specify/templates/spec-template.md - User story structure aligns with testing principles
✅ .specify/templates/tasks-template.md - Task structure supports independent testing and library-first approach

Follow-up TODOs: None - all placeholders filled
-->

# ChemEng Toolbox Constitution

## Core Principles

### I. Library-First Architecture

Every feature MUST start as a standalone Python library with clear boundaries:

- **Self-Contained**: Libraries must be independently testable without external dependencies on other project components
- **Clear Purpose**: Each library solves a specific engineering problem (no organizational-only libraries)
- **Documentation Required**: Public API must be documented with docstrings (NumPy style)
- **Unit Handling**: All calculations must use Pint for dimensional analysis and unit validation

**Rationale**: Library-first design enables code reuse across CLI, web, and API interfaces while maintaining testability and clarity.

### II. Multi-Interface Design

Every library MUST expose functionality through multiple interfaces:

- **Python API**: Direct function/class imports for library users
- **CLI Interface**: Command-line tools for scripting and automation
- **Web Interface**: Interactive calculators in static web application
- **Optional REST API**: For advanced integration scenarios (self-hosted)

**Text I/O Protocol**: CLI tools must follow stdin/args → stdout, errors → stderr with support for both JSON and human-readable formats.

**Rationale**: Multiple interfaces maximize accessibility for different use cases (students, researchers, automation) while maintaining a single source of truth in the library code.

### III. Validation-First Development (NON-NEGOTIABLE)

All calculations MUST be validated against authoritative sources:

- **Literature Validation**: Every calculation must match published examples from Perry's, GPSA, or peer-reviewed sources
- **Test Coverage**: Minimum 80% code coverage with pytest
- **Validation Tests**: Each calculation must have at least one validation test comparing output to literature values within acceptable tolerance
- **Type Safety**: 100% type coverage enforced with mypy --strict

**Red-Green-Refactor**: When adding calculations: (1) Write validation test from literature, (2) Verify test fails, (3) Implement calculation, (4) Verify test passes.

**Rationale**: Engineering calculations affect safety-critical decisions. Validation against authoritative sources ensures correctness and builds user trust.

### IV. Public Domain Data Only

All data sources MUST be public domain or openly licensed:

- **Approved Sources**: NIST WebBook, CoolProp (MIT), IAPWS-IF97, PubChem, JANAF Tables
- **Prohibited Sources**: DIPPR, Aspen Properties, or any proprietary databases requiring licensing fees
- **Data Attribution**: All data files must include source attribution and license information in headers
- **No Scraping**: Only use officially published APIs or downloadable datasets

**Rationale**: Ensures project remains free and legally redistributable under MIT license without licensing constraints.

### V. Cost-Free Operation

Infrastructure MUST remain within free tier limits:

- **Zero Monthly Cost Target**: Primary deployment (static web) must cost $0/month
- **Optional Backend**: If API deployed, must stay within AWS free tier ($0-5/month maximum)
- **GitHub Pages**: Static web hosting (free forever)
- **No Commercial Services**: No services requiring payment (avoid vendor lock-in)
- **Budget Alerts**: CloudWatch alarms required if using AWS backend

**Rationale**: Enables long-term sustainability without ongoing financial burden.

### VI. Developer Productivity

Development workflow MUST support efficient AI-assisted development:

- **Clear Structure**: Consistent project organization following library-first principles
- **Comprehensive Documentation**: README, architecture docs, deployment guides for AI context
- **Type Hints**: Full type annotations enable IDE/AI assistance
- **Conventional Commits**: Commit messages follow conventional format for automated changelog
- **Best-Effort Support**: Issue/PR responses on a best-effort basis

**Rationale**: Clear structure and AI tooling support maintain productivity and code quality.

### VII. Simplicity and Focus

Avoid over-engineering and maintain focus on core value:

- **YAGNI Principle**: Implement only features with demonstrated need
- **No Premature Optimization**: Optimize only when performance issues measured
- **No Enterprise Features**: No SSO, SLAs, 24/7 support, real-time collaboration
- **Web-Only UI**: No mobile apps (responsive web is sufficient)
- **Standard Tools**: Use well-established libraries (NumPy, SciPy, React) over custom solutions

**Rationale**: Limited development capacity requires ruthless prioritization on core engineering calculations over infrastructure complexity.

## Technical Constraints

### Technology Stack

**Backend (Python 3.11+)**:
- Core: NumPy, SciPy (scientific computing)
- Units: Pint (dimensional analysis)
- Validation: Pydantic (data validation)
- Testing: pytest, mypy (type checking)
- Data: CoolProp, thermo (property libraries)

**Frontend (Static Web)**:
- Framework: Next.js 14 (static site generation)
- Language: TypeScript (type safety)
- UI: Tailwind CSS + shadcn/ui (component library)
- Visualization: Recharts (chemical engineering plots)

**Optional Backend (AWS)**:
- Runtime: AWS Lambda (Python 3.11, ARM64 for cost efficiency)
- API: API Gateway HTTP API (cheaper than REST API)
- Storage: DynamoDB on-demand billing (if needed)
- Deployment: AWS SAM (infrastructure as code)

**CI/CD**:
- Platform: GitHub Actions (free tier: 2000 min/month)
- Checks: pytest, mypy, build validation on every PR

### Performance Requirements

- **Calculation Speed**: Single calculations <100ms (most <10ms)
- **Web Load Time**: First contentful paint <2s on 3G
- **API Response**: p95 latency <500ms (if backend deployed)
- **Memory**: Python processes <200MB per calculation
- **Test Suite**: Complete test run <60 seconds

### Quality Gates

All PRs MUST pass:
1. **Type Checking**: mypy --strict with zero errors
2. **Unit Tests**: pytest with >80% coverage
3. **Validation Tests**: All literature comparisons within tolerance
4. **Linting**: Black (formatting), isort (imports), flake8 (style)
5. **Build**: Next.js production build succeeds

## Development Workflow

### Feature Development Cycle

1. **Specification**: Create feature spec using `/speckit.specify` (optional for simple features)
2. **Literature Research**: Identify authoritative sources for validation
3. **Library Implementation**:
   - Write library code in `packages/core/src/`
   - Include type hints and docstrings
   - Add validation tests from literature
4. **Interface Exposure**:
   - CLI wrapper (if applicable)
   - Web calculator component
   - API endpoint (if backend exists)
5. **Documentation**: Update relevant docs (API reference, user guide)
6. **Quality Check**: Verify all quality gates pass
7. **Commit**: Use conventional commit format

### Testing Requirements

**Unit Tests** (80% of test effort):
- Test individual functions/classes in isolation
- Mock external dependencies
- Fast execution (<1s per test file)

**Validation Tests** (15% of test effort):
- Compare calculations to literature examples
- Use realistic parameter ranges
- Document source (book, paper, standard)

**Integration Tests** (5% of test effort):
- Test complete user workflows (library → web → API)
- Verify unit conversions work end-to-end
- Test error handling across interfaces

### Branching Strategy

- **main**: Production-ready code only
- **feature/###-name**: Feature development branches
- **fix/###-description**: Bug fix branches
- **docs/description**: Documentation-only changes

### Code Review

- **Self-Review**: Use AI assistance for code review suggestions
- **Community PRs**: Review on a best-effort basis, provide constructive feedback
- **Constitution Compliance**: Verify PR adheres to all applicable principles

## Governance

### Constitution Authority

This constitution supersedes all other development practices and preferences. Any deviation from these principles MUST be explicitly justified in PR description or planning documents.

### Amendment Process

1. **Proposal**: Document proposed change with rationale
2. **Impact Analysis**: Identify affected code, templates, documentation
3. **Version Bump**: Increment constitution version per semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
4. **Template Updates**: Update all dependent templates (plan, spec, tasks)
5. **Migration Plan**: Document steps to bring existing code into compliance
6. **Commit**: Use conventional commit format (e.g., `docs: amend constitution to v2.0.0`)

### Versioning Policy

All version numbers follow MAJOR.MINOR.PATCH format:
- **Code Versions**: packages/core follows semantic versioning
- **Constitution Version**: Governance changes follow semantic versioning
- **API Versions**: If backend deployed, use /v1/, /v2/ URL prefixes for breaking changes

### Complexity Justification

Any violation of Core Principles (I-VII) MUST be justified in planning documents:
- Document why the complexity is needed
- Explain why simpler alternatives were rejected
- Establish clear acceptance criteria for the exception
- Include sunset plan to remove complexity if possible

### Compliance Review

- **Every PR**: Verify compliance with applicable principles
- **Quarterly Review**: Audit codebase for principle adherence
- **Constitution Updates**: Review constitution annually for relevance

### Conflict Resolution

When principles conflict (rare), priority order:
1. **III. Validation-First Development** (safety/correctness is paramount)
2. **I. Library-First Architecture** (maintainability foundation)
3. **V. Cost-Free Operation** (sustainability requirement)
4. **IV. Public Domain Data Only** (legal compliance)
5. **VII. Simplicity and Focus** (prevents complexity creep)
6. **II. Multi-Interface Design** (user accessibility)
7. **VI. Developer Productivity** (productivity support)

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29

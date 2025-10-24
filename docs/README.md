# Documentation Index

## Welcome to the Legal Form Application Documentation

This directory contains comprehensive documentation for the Legal Form Application, a full-stack web application for collecting and processing legal case information.

---

## 📚 Documentation Overview

### For End Users
- **[User Guide](USER_GUIDE.md)** - Complete guide for filling out and submitting legal forms
  - Step-by-step instructions
  - Common workflows
  - Troubleshooting tips
  - FAQ

### For Developers
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development setup, workflow, and best practices
  - Environment setup
  - Project structure
  - Code style standards
  - Testing & debugging
  - Contribution guidelines

### For Architects & Technical Leads
- **[Architecture Documentation](ARCHITECTURE.md)** - System design and technical architecture
  - System overview diagrams (Mermaid)
  - Component interactions
  - Data flow diagrams
  - Technology stack
  - Scalability strategies
  - Deployment architecture

### For API Consumers
- **[API Reference](API_REFERENCE.md)** - Complete REST API documentation
  - All endpoints with examples
  - Authentication
  - Request/response formats
  - Error handling
  - Code examples (JavaScript, Python, cURL)

- **[OpenAPI Specification](api/openapi.yaml)** - Machine-readable API spec
  - Interactive API documentation
  - Import into Postman/Insomnia
  - Generate client libraries

---

## 🚀 Quick Links

### Getting Started
- [Installation Instructions](../README.md#installation) - Main README
- [Environment Setup](DEVELOPER_GUIDE.md#development-setup)
- [Database Setup](DEVELOPER_GUIDE.md#4-set-up-postgresql-database)
- [First Form Submission](USER_GUIDE.md#filling-out-the-form)

### Common Tasks
- [How to Submit a Form](USER_GUIDE.md#filling-out-the-form)
- [API Usage Examples](API_REFERENCE.md#code-examples)
- [Running Tests](DEVELOPER_GUIDE.md#testing)
- [Debugging Issues](DEVELOPER_GUIDE.md#debugging)
- [Deploying to Production](DEVELOPER_GUIDE.md#building--deployment)

### Reference
- [Database Schema](ARCHITECTURE.md#database-schema)
- [API Endpoints](API_REFERENCE.md#endpoints)
- [Frontend Components](ARCHITECTURE.md#component-details)
- [Monitoring & Metrics](API_REFERENCE.md#prometheus-metrics)

---

## 📖 Documentation by Role

### 👤 I'm a Legal Aid Staff Member
**Start here:** [User Guide](USER_GUIDE.md)

You'll learn:
- How to fill out legal forms
- How to add multiple plaintiffs/defendants
- How to track issues across 19 categories
- Common workflows and tips

### 💻 I'm a Developer
**Start here:** [Developer Guide](DEVELOPER_GUIDE.md)

You'll learn:
- How to set up your development environment
- Project structure and code organization
- How to write and run tests
- Code style guidelines
- How to contribute

### 🏗️ I'm an Architect/Tech Lead
**Start here:** [Architecture Documentation](ARCHITECTURE.md)

You'll learn:
- System architecture and design decisions
- Component interactions and data flow
- Technology stack rationale
- Scalability and performance considerations
- Deployment strategies

### 🔌 I'm Integrating with the API
**Start here:** [API Reference](API_REFERENCE.md)

You'll learn:
- Available API endpoints
- Authentication requirements
- Request/response formats
- Error handling
- Code examples in multiple languages

---

## 📂 Documentation Structure

```
docs/
├── README.md                    # This file - Documentation index
├── USER_GUIDE.md               # End-user documentation
├── DEVELOPER_GUIDE.md          # Developer documentation
├── ARCHITECTURE.md             # System architecture
├── API_REFERENCE.md            # API documentation
└── api/
    └── openapi.yaml            # OpenAPI 3.0 specification
```

---

## 🎯 Quick Reference

### Key Concepts

#### Form Entries
Legal form submissions containing:
- Property information
- Plaintiff details (with issue tracking)
- Defendant details
- Stored in JSON files + PostgreSQL database

#### Plaintiffs
Individuals or organizations filing the legal action. Each plaintiff can track issues across 19 comprehensive categories.

#### Defendants
Individuals or entities being sued (property managers, owners, etc.).

#### Issue Categories (19 Total)
- Vermin Issues
- Insect Issues
- Environmental Hazards
- Health Hazards
- Structure Issues
- Plumbing Problems
- Weatherproofing
- HVAC Issues
- Fire Hazards
- Safety Issues
- Common Area Issues
- Trash Problems
- Notice Issues
- Utility Interruptions
- Accessibility Issues
- Tenant Harassment
- Lease Violations
- Habitability Defects
- Other Issues

#### Dual Storage
Form submissions are stored in TWO places:
1. **JSON Files** - In `data/` directory
2. **PostgreSQL Database** - Normalized relational structure

#### Pipeline
Optional Python FastAPI service that processes and normalizes form submissions through a 5-phase ETL pipeline.

---

## 🔧 Technology Stack Summary

### Frontend
- HTML5, CSS3, Vanilla JavaScript (ES6+)
- Notyf (toast notifications)
- Server-Sent Events (real-time updates)

### Backend
- Node.js with Express
- PostgreSQL database
- Winston (logging)
- Prometheus (metrics)
- Dropbox SDK (optional cloud backup)

### Pipeline (Optional)
- Python 3.8+ with FastAPI
- Psycopg 3 (PostgreSQL driver)
- Pydantic (data validation)

### Testing
- Playwright (E2E tests)

---

## 📊 System Diagrams

### High-Level Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│  Express Server     │
│  (Port 3000)        │
└──────┬──────────────┘
       │
       ├──→ JSON Files (data/)
       ├──→ PostgreSQL Database
       ├──→ Dropbox (optional)
       └──→ Python Pipeline (optional)
```

**Detailed diagrams:** See [Architecture Documentation](ARCHITECTURE.md)

---

## 🚦 API Quick Start

### Submit a Form
```bash
curl -X POST http://localhost:3000/api/form-entries \
  -H "Content-Type: application/json" \
  -d '{"Full_Address": {...}, "PlaintiffDetails": [...], "DefendantDetails2": [...]}'
```

### Get All Entries
```bash
curl http://localhost:3000/api/form-entries
```

### Health Check
```bash
curl http://localhost:3000/health
```

**Full API documentation:** [API Reference](API_REFERENCE.md)

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Documentation |
|-------|---------------|
| Can't submit form | [User Guide - Troubleshooting](USER_GUIDE.md#troubleshooting) |
| Development setup failing | [Developer Guide - Initial Setup](DEVELOPER_GUIDE.md#development-setup) |
| Database connection errors | [Developer Guide - Debugging](DEVELOPER_GUIDE.md#database-debugging) |
| API returning 401 | [API Reference - Authentication](API_REFERENCE.md#authentication) |
| Pipeline not running | [Architecture - Pipeline](ARCHITECTURE.md#3-python-normalization-pipeline) |

---

## 📝 Additional Resources

### Project Files
- **Main README** - [`../README.md`](../README.md)
- **Package Info** - [`../package.json`](../package.json)
- **Environment Template** - [`../.env.example`](../.env.example)
- **Database Schema** - [`../database/schema.sql`](../database/schema.sql)

### External Documentation
- [Express.js Documentation](https://expressjs.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Documentation](https://playwright.dev/)

---

## 🤝 Contributing

Interested in contributing? See the [Developer Guide - Contributing](DEVELOPER_GUIDE.md#contributing) section.

**Quick Checklist:**
- [ ] Read the Developer Guide
- [ ] Set up development environment
- [ ] Create feature branch
- [ ] Write tests
- [ ] Update documentation
- [ ] Submit pull request

---

## 📞 Support & Feedback

### Documentation Issues
If you find errors or have suggestions for improving this documentation:
1. Create an issue describing the problem
2. Suggest specific improvements
3. Submit a pull request with corrections

### Application Issues
For bugs or feature requests related to the application itself:
1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Steps to reproduce (if bug)
   - Expected vs actual behavior
   - Environment details

---

## 📄 Document Versions

| Document | Version | Last Updated |
|----------|---------|--------------|
| Documentation Index | 1.0.0 | 2025-10-21 |
| User Guide | 1.0.0 | 2025-10-21 |
| Developer Guide | 1.0.0 | 2025-10-21 |
| Architecture | 1.0.0 | 2025-10-21 |
| API Reference | 1.0.0 | 2025-10-21 |
| OpenAPI Spec | 1.0.0 | 2025-10-21 |

---

## 🗺️ Documentation Roadmap

### Planned Additions
- [ ] Database migration guide
- [ ] Performance tuning guide
- [ ] Security best practices
- [ ] Monitoring & alerting setup
- [ ] Backup & disaster recovery procedures
- [ ] CI/CD pipeline documentation
- [ ] Docker containerization guide
- [ ] Kubernetes deployment guide
- [ ] API versioning strategy
- [ ] Multi-tenant setup guide

### Continuous Improvement
This documentation is actively maintained and updated. If you notice outdated information or have suggestions, please contribute!

---

## 📚 Related Documentation

### Project-Specific
- **Dropbox Setup** - [`../DROPBOX_SETUP.md`](../DROPBOX_SETUP.md) (if exists)
- **GCP Deployment** - [`../GCP_DEPLOYMENT_PLAN.md`](../GCP_DEPLOYMENT_PLAN.md)
- **Pipeline README** - [`../api/README.md`](../api/README.md)
- **Database README** - [`../database/README.md`](../database/README.md)

### Python API Documentation
For the normalization pipeline:
- FastAPI auto-generated docs: http://localhost:8000/docs
- ReDoc alternative: http://localhost:8000/redoc

---

## 🎓 Learning Path

### For New Team Members

**Week 1: Understanding the Application**
1. Read [Main README](../README.md)
2. Read [User Guide](USER_GUIDE.md)
3. Try submitting a test form
4. Review [Architecture Documentation](ARCHITECTURE.md)

**Week 2: Development Setup**
1. Set up development environment ([Developer Guide](DEVELOPER_GUIDE.md))
2. Run the application locally
3. Explore the codebase
4. Run tests

**Week 3: Making Changes**
1. Pick a small issue or enhancement
2. Create feature branch
3. Make changes following style guidelines
4. Write/update tests
5. Submit pull request

**Ongoing: Deep Dives**
- Study specific components in [Architecture](ARCHITECTURE.md)
- Review [API Reference](API_REFERENCE.md) for integrations
- Read inline code documentation
- Participate in code reviews

---

## 🏆 Documentation Best Practices

When updating documentation:

✅ **DO:**
- Keep language clear and concise
- Include code examples
- Add diagrams for complex concepts
- Update version and date
- Test all code examples
- Check links work
- Use consistent formatting

❌ **DON'T:**
- Assume prior knowledge
- Use jargon without explanation
- Skip important details
- Leave outdated information
- Forget to update related docs
- Make docs too technical (unless dev docs)

---

## 🔍 Document Search Tips

To find specific information quickly:

1. **Use your browser's find** (Ctrl+F / Cmd+F)
2. **Check the Table of Contents** in each document
3. **Use specific keywords**:
   - "authentication" → API Reference
   - "setup" → Developer Guide
   - "submit form" → User Guide
   - "database" → Architecture or Developer Guide
   - "troubleshooting" → User Guide or Developer Guide

4. **Browse by role** (see [Documentation by Role](#-documentation-by-role))

---

**Thank you for using the Legal Form Application!**

For questions, issues, or contributions, please reach out to the development team.

---

**Documentation Index Version:** 1.0.0
**Last Updated:** 2025-10-21
**Maintained By:** Development Team

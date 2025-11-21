# Trial Balance Automation - Documentation Index

**Last Updated:** November 21, 2025

---

## 📚 Documentation Overview

This folder contains all technical and user documentation for the Trial Balance Automation system.

---

## 🚀 Getting Started (Read These First)

### 1. [GETTING_STARTED.md](GETTING_STARTED.md)
**For:** Business users, first-time users  
**Purpose:** Step-by-step guide to run the system  
**Contains:**
- Prerequisites checklist
- Installation instructions
- How to launch the GUI
- How to process reports
- Where to find outputs

### 2. [README.md](../README.md) *(Project Root)*
**For:** All users  
**Purpose:** Project overview and quick reference  
**Contains:**
- Project description
- Technology stack
- Quick start commands
- Directory structure

---

## 📖 User Guides

### 3. [simple_user_guide.pdf](../simple_user_guide.pdf)
**For:** Business users  
**Purpose:** Visual guide with screenshots  
**Contains:**
- GUI interface walkthrough
- Step-by-step processing instructions
- Output file explanations

---

## 🔧 Technical Documentation

### 4. [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) ⭐ **COMPREHENSIVE**
**For:** Developers, data scientists, technical users  
**Purpose:** Complete technical reference for reproducibility  
**Contains:**
- Project structure
- Data inventory (all input/output schemas)
- Data flow pipeline (cell-by-cell execution)
- DataFrame transformations (6 key DataFrames)
- Functions reference (7 major functions)
- Execution workflows (GUI, Jupyter, CLI)
- Reproducibility guide (setup → verification)
- Configuration reference
- Logging configuration
- Data quality & validation
- Extension points

### 5. [FILE_INDEX.md](FILE_INDEX.md)
**For:** Developers  
**Purpose:** Complete file inventory  
**Contains:**
- All project files with descriptions
- File locations
- Purpose of each file
- Which files to use/ignore

### 6. [OUTPUT_DIRECTORIES.md](OUTPUT_DIRECTORIES.md)
**For:** All users  
**Purpose:** Understanding output locations  
**Contains:**
- Where reports are saved
- File naming conventions
- GUI display features
- Output folder structure

### 7. [OUTPUT_LOCATION_GUIDE.md](OUTPUT_LOCATION_GUIDE.md) ⭐ **NEW**
**For:** All users  
**Purpose:** Choose where reports are saved (shared drive vs local)  
**Contains:**
- How to use output location selector
- Shared drive vs local storage comparison
- When to use each option
- Troubleshooting output location issues
- Technical implementation details

---

## 🔄 Workflow & Process

### 8. [workflow-diagram.md](workflow-diagram.md)
**For:** Technical users  
**Purpose:** Visual process flow  
**Contains:**
- Mermaid diagrams
- Data flow visualization
- Processing steps

### 9. [Trail Balance Automation Flowchart.html](Trail%20Balance%20Automation%20Flowchart.html)
**For:** All users  
**Purpose:** Interactive flowchart  
**Contains:**
- Visual workflow representation
- Decision points
- Process flow

---

## ⚙️ Configuration & Setup

### 10. [config-fallback-system.md](config-fallback-system.md)
**For:** Developers  
**Purpose:** Understanding config system  
**Contains:**
- How config/run_config.json works
- Fallback to auto-detection
- GUI → Notebook bridge

### 11. [HOW_PATHS_WORK.md](HOW_PATHS_WORK.md)
**For:** Developers  
**Purpose:** Path resolution logic  
**Contains:**
- Absolute vs relative paths
- Project root detection
- Cross-platform compatibility

### 12. [QUICKSTART-CONFIG-FALLBACK.md](QUICKSTART-CONFIG-FALLBACK.md)
**For:** Developers  
**Purpose:** Quick reference for config system  
**Contains:**
- Config file structure
- Usage examples

---

## 🔌 Integration & Deployment

### 13. [GITHUB_SETUP.md](GITHUB_SETUP.md)
**For:** Developers, DevOps  
**Purpose:** GitHub repository setup  
**Contains:**
- Repository configuration
- Branch structure
- Collaboration guidelines

### 14. [IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)
**For:** Developers  
**Purpose:** Implementation decisions log  
**Contains:**
- Feature implementation notes
- Technical decisions
- Change history

### 15. [VERIFICATION-CHECKLIST.md](VERIFICATION-CHECKLIST.md)
**For:** QA, Developers  
**Purpose:** Testing and validation  
**Contains:**
- Pre-deployment checks
- Test scenarios
- Validation steps

---

## 📝 Draft Documentation

### 16. [draft/](draft/)
**For:** Internal reference  
**Purpose:** Work-in-progress documentation  
**Contains:**
- `overview.md` - Initial project overview
- `crisp-dm.md` - CRISP-DM framework mapping
- Other planning documents

---

## 📄 Additional Resources

### 17. [DGD - Trial Balance - v1.0.docx.pdf](DGD%20-%20Trial%20Balance%20-%20v1.0.docx.pdf)
**For:** Business stakeholders  
**Purpose:** Original requirements document  
**Contains:**
- Business requirements
- Functional specifications
- Use cases

---

## 🗺️ Documentation Map by User Type

### Business Users (Non-Technical)
1. **Start here:** [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Visual guide:** [simple_user_guide.pdf](../simple_user_guide.pdf)
3. **Choose output location:** [OUTPUT_LOCATION_GUIDE.md](OUTPUT_LOCATION_GUIDE.md) ⭐ NEW
4. **Find outputs:** [OUTPUT_DIRECTORIES.md](OUTPUT_DIRECTORIES.md)

### Data Analysts / Power Users
1. **Start here:** [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Understand outputs:** [OUTPUT_DIRECTORIES.md](OUTPUT_DIRECTORIES.md)
3. **Technical details:** [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
4. **Process flow:** [workflow-diagram.md](workflow-diagram.md)

### Developers / Data Scientists
1. **Overview:** [README.md](../README.md) *(root)*
2. **Complete reference:** [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) ⭐
3. **File inventory:** [FILE_INDEX.md](FILE_INDEX.md)
4. **Configuration:** [config-fallback-system.md](config-fallback-system.md)
5. **Paths logic:** [HOW_PATHS_WORK.md](HOW_PATHS_WORK.md)
6. **Implementation:** [IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)

### DevOps / System Administrators
1. **Setup:** [GETTING_STARTED.md](GETTING_STARTED.md)
2. **GitHub:** [GITHUB_SETUP.md](GITHUB_SETUP.md)
3. **Verification:** [VERIFICATION-CHECKLIST.md](VERIFICATION-CHECKLIST.md)
4. **Technical:** [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)

---

## 🔍 Quick Find

| Need to... | Read this |
|------------|-----------|
| Run the system for first time | [GETTING_STARTED.md](GETTING_STARTED.md) |
| Understand the code structure | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) |
| Find output files | [OUTPUT_DIRECTORIES.md](OUTPUT_DIRECTORIES.md) |
| Choose output location | [OUTPUT_LOCATION_GUIDE.md](OUTPUT_LOCATION_GUIDE.md) ⭐ |
| Reproduce results | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) → Reproducibility Guide |
| Understand data flow | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) → Data Flow section |
| Find function definitions | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) → Functions Reference |
| Add new features | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) → Extension Points |
| Debug issues | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) → Troubleshooting |
| Understand config system | [config-fallback-system.md](config-fallback-system.md) |
| See all project files | [FILE_INDEX.md](FILE_INDEX.md) |

---

## 📊 Documentation Statistics

- **Total Documents:** 17 files + draft folder
- **Primary Reference:** TECHNICAL_DOCUMENTATION.md (comprehensive)
- **User Guides:** 4 files (Getting Started, User Guide, Output Location Guide, README)
- **Technical Docs:** 8 files
- **Configuration:** 3 files
- **Verification:** 2 files

---

## 🔄 Document Maintenance

**How to Update Documentation:**

1. **Code changes:** Update [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
2. **New features:** Update both TECHNICAL_DOCUMENTATION.md and GETTING_STARTED.md
3. **Output changes:** Update [OUTPUT_DIRECTORIES.md](OUTPUT_DIRECTORIES.md)
4. **New files:** Update [FILE_INDEX.md](FILE_INDEX.md)
5. **Process changes:** Update [workflow-diagram.md](workflow-diagram.md)

**Version Control:**
- All documentation is tracked in Git
- Update "Last Updated" date when making changes
- Add version history in TECHNICAL_DOCUMENTATION.md

---

## 💡 Documentation Best Practices

✅ **Use TECHNICAL_DOCUMENTATION.md** as single source of truth for code structure  
✅ **Keep GETTING_STARTED.md** simple and user-friendly  
✅ **Update FILE_INDEX.md** when adding/removing files  
✅ **Add screenshots** to user guides when possible  
✅ **Link between documents** for easy navigation  
✅ **Version documentation** alongside code changes  

---

**Questions?** Contact VFC Data Science Team

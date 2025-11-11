# Trial Balance Automation - Workflow Diagram

## Overview
This document provides a visual representation of the Trial Balance Automation workflow, from data loading to export.

---

## Main Workflow

```mermaid
flowchart TD
    Start([Start Automation]) --> Init[Initialize Libraries & Logger]
    Init --> LoadFunctions[Define Data Loading Functions]
    
    LoadFunctions --> LoadTB[Load Trial Balance Data]
    LoadTB --> FindYear{Find Latest Year Folder}
    FindYear --> FindMonth{Find Latest Month Folder}
    FindMonth --> LoadDaily[Load Daily TB Files<br/>MM-DD-YYYY.csv]
    LoadDaily --> LoadCOA[Load Chart of Accounts]
    
    LoadFunctions --> LoadRef[Load Reference Data]
    LoadRef --> LoadCOAMap[Load COA Mapping<br/>Latest CSV/XLSX]
    LoadRef --> LoadPortMap[Load Portfolio Mapping<br/>Latest CSV/XLSX]
    
    LoadCOA --> Separate[Separate Data by Source]
    LoadCOAMap --> Separate
    LoadPortMap --> Separate
    
    Separate --> AddDate[Add Date Column to TB Data]
    AddDate --> Consolidate[Consolidate Daily TB<br/>into Single DataFrame]
    
    Consolidate --> CreatePivot[Create Pivot Table<br/>GL Account × Fund Name]
    
    CreatePivot --> Match[Match GL Accounts<br/>with COA Mapping]
    Match --> CheckNew{New Accounts<br/>Found?}
    
    CheckNew -->|Yes| ListNew[List New Accounts]
    CheckNew -->|No| AllMatch[All Accounts Match]
    
    ListNew --> CreateDF[Create New Accounts DataFrame]
    CreateDF --> Combine[Combine with Original COA]
    Combine --> AddIndicator[Add Is_New_Account Column]
    AddIndicator --> Export[Export Updated COA Mapping<br/>MM.DD.YYYY.xlsx]
    
    Export --> End([End])
    AllMatch --> End
    
    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style CheckNew fill:#fff4e1
    style Export fill:#e1f0ff
    style CreatePivot fill:#f0e1ff
```

---

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input["📂 Input Sources"]
        RawTB[(Trial Balance<br/>Daily CSVs)]
        RawCOA[(Chart of<br/>Accounts)]
        RefCOA[(COA<br/>Mapping)]
        RefPort[(Portfolio<br/>Mapping)]
    end
    
    subgraph Processing["⚙️ Processing Steps"]
        Load[Load & Parse]
        Transform[Transform & Consolidate]
        Analyze[Analyze & Match]
    end
    
    subgraph Output["📤 Output"]
        Pivot[(Pivot Table<br/>GL × Fund)]
        Updated[(Updated COA<br/>Mapping)]
        Logs[(Log Files)]
    end
    
    RawTB --> Load
    RawCOA --> Load
    RefCOA --> Load
    RefPort --> Load
    
    Load --> Transform
    Transform --> Analyze
    
    Analyze --> Pivot
    Analyze --> Updated
    Load -.-> Logs
    Transform -.-> Logs
    Analyze -.-> Logs
    
    style Input fill:#e1f5e1
    style Processing fill:#fff4e1
    style Output fill:#e1f0ff
```

---

## Detailed Process Flow

```mermaid
flowchart TD
    subgraph Section1["1. Initialization"]
        S1A[Import Libraries]
        S1B[Configure Logging]
        S1C[Set Display Options]
        S1A --> S1B --> S1C
    end
    
    subgraph Section2["2-3. Define Functions"]
        S2A[load_trial_balance_data]
        S2B[load_reference_data]
        S2C[Helper: load_file]
        S2A -.-> S2C
        S2B -.-> S2C
    end
    
    subgraph Section4["4. Load Data"]
        S4A[Execute: load_trial_balance_data]
        S4B[Execute: load_reference_data]
        S4A --> S4C[Store in 'data' dict]
        S4B --> S4D[Store in 'reference_data' dict]
    end
    
    subgraph Section5["5. Separate Data"]
        S5A[trial_balance_data]
        S5B[chart_of_accounts]
        S5C[coa_mapping]
        S5D[portfolio_mapping]
        S5E[metadata]
    end
    
    subgraph Section6["6. Add Date Column"]
        S6A[Loop through TB dates]
        S6B[Add Date to each DF]
    end
    
    subgraph Section7["7. Consolidate"]
        S7A[pd.concat all TB DFs]
        S7B[Create: trial_balance_consolidated]
    end
    
    subgraph Section8["8. Create Pivot"]
        S8A[pivot_table<br/>index=accountname<br/>columns=level1accountname<br/>values=netamt]
        S8B[Create: trial_balance_pivot_table]
    end
    
    subgraph Section9["9. Match & Export"]
        S9A[Compare GL Accounts]
        S9B[Identify New Accounts]
        S9C[Create updated_coa_mapping]
        S9D[Add Is_New_Account column]
        S9E[Export to Excel]
        S9A --> S9B --> S9C --> S9D --> S9E
    end
    
    Section1 --> Section2
    Section2 --> Section4
    Section4 --> Section5
    Section5 --> Section6
    Section6 --> Section7
    Section7 --> Section8
    Section8 --> Section9
    
    style Section1 fill:#e1f5e1
    style Section2 fill:#ffe1e1
    style Section4 fill:#e1f0ff
    style Section5 fill:#fff4e1
    style Section6 fill:#f0e1ff
    style Section7 fill:#e1f5f5
    style Section8 fill:#ffe1f5
    style Section9 fill:#f5e1e1
```

---

## Data Structures

```mermaid
graph TD
    subgraph DataDict["data = load_trial_balance_data()"]
        TB[trial_balance: dict]
        COA[chart_of_accounts: DataFrame]
        Meta[metadata: dict]
    end
    
    subgraph RefDict["reference_data = load_reference_data()"]
        COAMap[coa_mapping: DataFrame]
        PortMap[portfolio_mapping: DataFrame]
        RefMeta[metadata: dict]
    end
    
    subgraph TBDict["trial_balance (dict of DataFrames)"]
        Date1['2025-09-01': DataFrame]
        Date2['2025-09-02': DataFrame]
        DateN['2025-09-30': DataFrame]
    end
    
    subgraph Consolidated["trial_balance_consolidated (DataFrame)"]
        Cols[Columns:<br/>accountname, level1accountname,<br/>netamt, Date, ...]
    end
    
    subgraph Pivot["trial_balance_pivot_table (DataFrame)"]
        Rows[Index: GL Account]
        Columns[Columns: Fund Name]
        Values[Values: Balance sum]
    end
    
    TB --> TBDict
    TBDict --> Consolidated
    Consolidated --> Pivot
    
    COAMap --> Match[Matching Process]
    Pivot --> Match
    
    style DataDict fill:#e1f5e1
    style RefDict fill:#ffe1e1
    style TBDict fill:#e1f0ff
    style Consolidated fill:#fff4e1
    style Pivot fill:#f0e1ff
```

---

## Error Handling & Validation

```mermaid
flowchart TD
    Start([File Loading]) --> CheckFolder{Folder<br/>Exists?}
    
    CheckFolder -->|No| Warn1[⚠️ WARNING: Folder not found]
    CheckFolder -->|Yes| CheckFiles{Files<br/>Found?}
    
    CheckFiles -->|No| Warn2[⚠️ WARNING: No files found]
    CheckFiles -->|Yes| Validate{File Format<br/>Valid?}
    
    Validate -->|Invalid| Warn3[⚠️ WARNING: Invalid format<br/>Skip file]
    Validate -->|Valid| LoadFile[✓ Load File]
    
    LoadFile --> LogSuccess[📝 Log: File loaded successfully]
    Warn1 --> LogWarn[📝 Log: Warning recorded]
    Warn2 --> LogWarn
    Warn3 --> LogWarn
    
    LogSuccess --> Continue([Continue])
    LogWarn --> Continue
    
    style Start fill:#e1f5e1
    style CheckFolder fill:#fff4e1
    style CheckFiles fill:#fff4e1
    style Validate fill:#fff4e1
    style LoadFile fill:#e1f0ff
    style Warn1 fill:#ffe1e1
    style Warn2 fill:#ffe1e1
    style Warn3 fill:#ffe1e1
```

---

## Usage Instructions

### Viewing the Diagrams

To view these Mermaid diagrams in VS Code, install one of these extensions:

1. **Markdown Preview Mermaid Support** (Recommended)
   - Extension ID: `bierner.markdown-mermaid`
   - Preview this file with `Ctrl+Shift+V`

2. **Mermaid Chart** (Official)
   - Extension ID: `mermaidchart.vscode-mermaid-chart`
   - Enhanced editing features

3. **Mermaid Preview**
   - Extension ID: `vstirbu.vscode-mermaid-preview`
   - Live preview capability

### Exporting Diagrams

1. **As PNG/SVG**: Use Mermaid Chart extension or online editor (mermaid.live)
2. **In Documentation**: These diagrams work in GitHub, GitLab, and most markdown viewers
3. **In Presentations**: Export as images or use reveal.js with mermaid plugin

---

## Diagram Legend

- 🟢 **Green boxes**: Start/Input points
- 🔵 **Blue boxes**: Processing steps
- 🟡 **Yellow boxes**: Decision points
- 🔴 **Red boxes**: End/Output points
- 🟣 **Purple boxes**: Data transformations
- **Dashed arrows**: Logging/metadata flow
- **Solid arrows**: Data flow

---

**Last Updated**: November 11, 2025  
**Author**: Raiden Velarde Guillergan - Data Scientist

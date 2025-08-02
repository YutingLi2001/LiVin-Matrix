# Infrastructure Validation Task

## Purpose

To comprehensively validate platform infrastructure changes against security, reliability, operational, and compliance requirements before deployment. This task ensures all platform infrastructure meets organizational standards, follows best practices, and properly integrates with the broader system.

## Inputs

- Infrastructure Change Request
- Infrastructure Architecture Document
- Infrastructure Guidelines
- Technology Stack Document
- `infrastructure-checklist.md` (primary validation framework)

## Key Activities & Instructions

### 1. Confirm Interaction Mode

- Ask the user: "How would you like to proceed with platform infrastructure validation? We can work:
  A. **Incrementally (Default & Recommended):** We'll work through each section of the checklist step-by-step, documenting compliance or gaps for each item before moving to the next section.
  B. **"YOLO" Mode:** I can perform a rapid assessment of all checklist items and present a comprehensive validation report for review."
- Request the user to select their preferred mode and proceed accordingly.

### 2. Initialize Platform Validation

- Review the infrastructure change documentation to understand platform implementation scope and purpose
- Analyze the infrastructure architecture document for platform design patterns and compliance requirements
- Examine infrastructure guidelines for organizational standards across all platform components
- Prepare the validation environment and tools for comprehensive platform testing

### 3. Execute Comprehensive Platform Validation Process

- **If "Incremental Mode" was selected:**
  - For each section of the infrastructure checklist:
    - **a. Present Section Purpose:** Explain what this section validates and why it's important for platform operations
    - **b. Work Through Items:** Present each checklist item, guide the user through validation, and document compliance or gaps
    - **c. Evidence Collection:** For each compliant item, document how compliance was verified
    - **d. Gap Documentation:** For each non-compliant item, document specific issues and proposed remediation
    - **e. Section Summary:** Provide a compliance percentage and highlight critical findings before moving to the next section

- **If "YOLO Mode" was selected:**
  - Work through all checklist sections rapidly
  - Document compliance status for each item across all platform components  
  - Identify and document critical non-compliance issues affecting platform operations
  - Present a comprehensive validation report for all sections

### 4. Generate Comprehensive Platform Validation Report

- Summarize validation findings by section across all checklist areas
- Calculate and present overall compliance percentage for complete platform stack
- Clearly document all non-compliant items with remediation plans prioritized by platform impact
- Highlight critical security or operational risks affecting platform reliability
- Provide validation signoff recommendation based on complete platform assessment

## Output

A comprehensive platform validation report documenting:

1. **Compliance percentage by checklist section**
2. **Detailed findings for each non-compliant item** across foundation and platform components
3. **Platform integration validation results** documenting component interoperability
4. **Remediation recommendations with priority levels** based on platform impact
5. **Clear signoff recommendation** for platform deployment readiness
6. **Next steps for implementation or remediation** prioritized by platform dependencies
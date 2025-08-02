# Infrastructure Review Task

## Purpose

To conduct a thorough review of existing infrastructure to identify improvement opportunities, security concerns, and alignment with best practices. This task helps maintain infrastructure health, optimize costs, and ensure continued alignment with organizational requirements.

## Inputs

- Current infrastructure documentation
- Monitoring and logging data
- Recent incident reports
- Cost and performance metrics
- `infrastructure-checklist.md` (primary review framework)

## Key Activities & Instructions

### 1. Confirm Interaction Mode

- Ask the user: "How would you like to proceed with the infrastructure review? We can work:
  A. **Incrementally (Default & Recommended):** We'll work through each section of the checklist methodically, documenting findings for each item before moving to the next section. This provides a thorough review.
  B. **"YOLO" Mode:** I can perform a rapid assessment of all infrastructure components and present a comprehensive findings report. This is faster but may miss nuanced details."
- Request the user to select their preferred mode and proceed accordingly.

### 2. Prepare for Review

- Gather and organize current infrastructure documentation
- Access monitoring and logging systems for operational data
- Review recent incident reports for recurring issues
- Collect cost and performance metrics
- <critical_rule>Establish review scope and boundaries with the user before proceeding</critical_rule>

### 3. Conduct Systematic Review

- **If "Incremental Mode" was selected:**

  - For each section of the infrastructure checklist:
    - **a. Present Section Focus:** Explain what aspects of infrastructure this section reviews
    - **b. Work Through Items:** Examine each checklist item against current infrastructure
    - **c. Document Current State:** Record how current implementation addresses or fails to address each item
    - **d. Identify Gaps:** Document improvement opportunities with specific recommendations
    - **e. Section Summary:** Provide an assessment summary before moving to the next section

- **If "YOLO Mode" was selected:**
  - Rapidly assess all infrastructure components
  - Document key findings and improvement opportunities
  - Present a comprehensive review report

### 4. Generate Findings Report

- Summarize review findings by category (Security, Performance, Cost, Reliability, etc.)
- Prioritize identified issues (Critical, High, Medium, Low)
- Document recommendations with estimated effort and impact
- Create an improvement roadmap with suggested timelines
- Highlight cost optimization opportunities

## Output

A comprehensive infrastructure review report that includes:

1. **Current state assessment** for each infrastructure component
2. **Prioritized findings** with severity ratings
3. **Detailed recommendations** with effort/impact estimates
4. **Cost optimization opportunities**
5. **Action plan** for critical improvements
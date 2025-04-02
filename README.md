# HealthTrack: Cognitive Health Monitoring System 🧠🏥

## 1. Introduction
### 1.1 Purpose
HealthTrack is a software solution designed to address cognitive health disparities in African communities by providing:
- cognitive assessments
- Lifestyle habit tracking
- Healthcare professional connectivity

### 1.2 Problem Statement
| Aspect       | Description |
|--------------|-------------|
| **Who**      | African adults (25-65) with limited access to cognitive healthcare |
| **What**     | Lack of affordable, localized cognitive health monitoring tools |
| **When**     | Persistent need due to rising dementia cases (WHO reports 2.3M cases in Africa, 2023) |
| **Where**    | Urban and peri-urban areas with smartphone penetration |
| **Why**      | Early detection can reduce dementia progression by 40% |
| **How**      | Mobile-first platform with offline capabilities |

## 2. Technical Specifications
### 2.1 System Features
| Feature | Description | Status |
|---------|-------------|--------|
| Cognitive Tests | Memory/attention assessments | ✅ Implemented |
| Lifestyle Dashboard | Sleep/nutrition/exercise tracking | ✅ Implemented |
| Healthcare Network | Verified professional directory | 🚧 In Progress |

### 2.2 Technology Stack
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Frontend | React.js | Cross-platform compatibility |
| Backend | Django REST | Rapid development for African context |
| Database | PostgreSQL | ACID compliance for medical data |
| Deployment | Vercel + Render | Cost-effective for African startups |

## 3. Development Approach
### 3.1 Software Development Model
**Agile Methodology**  
*Selected because:*
- Allows iterative improvements based on user feedback
- Accommodates resource constraints common in African tech ecosystems
- Supports parallel development of core modules

*Implementation Steps:*
1. Sprint 1: Core assessment engine (completed)
2. Sprint 2: Data visualization (current)
3. Sprint 3: Professional network integration (planned needs discussion with healthcare professional for implementation)

### 3.2 Hypothesis
"Deploying a health platform will increase early cognitive impairment detection rates among target users."

## 4. Installation Guide
### 4.1 Local Development

# Frontend
cd PRODIM/my-app && npm install && npm start

# Backend 
cd PRODIM/dementia_prevention
python manage.py runserver

## 5. Requirements Specification

### 5.1 Functional Requirements

| ID  | Requirement                          | Priority   | Status            |
|-----|--------------------------------------|------------|-------------------|
| FR1 | User authentication system          | High       | ✅ Implemented    |
| FR2 | Cognitive test scoring algorithm     | Critical   | ✅ Implemented    |
| FR3 | Data export to PDF                   | Medium     | 🚧 In Progress    |

### 5.2 Non-Functional Requirements

| Type          | Requirement                          | Metric                    | Phase       |
|---------------|--------------------------------------|---------------------------|-------------|
| Performance   | To Support 50 concurrent users      | ≤2s response time         | Live        |
| Security      |                                     | AES-256 encryption        | Live        |
| Localization  | English Language                    | 2+ languages              | Phase 2     |

---

## 6. References (APA Format)

1. World Health Organization. (2023). *Dementia in Africa: Situation Analysis*. Geneva: WHO Press.  
2. African Union. (2022). *Digital Health Strategy for Africa 2023-2030*. Addis Ababa: AU Publications.
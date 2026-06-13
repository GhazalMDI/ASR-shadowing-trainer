# AI-Powered English Shadowing Platform using Automatic Speech Recognition (ASR)

## Introduction
Speech Shadowing Platform is an AI-based language learning project that helps users improve their **Pronunciation**, **Fluency**, and **Speaking** skills using the shadowing technique.

In this project, users can listen to podcasts and real-world audio content, and then repeat what they hear within a **10-second window**. The system processes the user’s speech in real-time and finally returns a score for evaluation.

---

## Features

### Shadowing Practice

* Audio content playback
* Real-time user speech recording
* Comparison of user speech with reference audio using matching subsequences

---

### AI-based Analysis

* Speech-to-text conversion using Whisper
* Pronunciation quality evaluation
* Similarity analysis between user speech and reference audio
* Feedback generation to improve speaking skills

---

### YouTube Content Ingestion

* Fetch podcast videos from YouTube
* Extract and process audio content
* Store podcast metadata in the database
* Automatically prepare content for shadowing practice

---

## System Architecture

```
YouTube Videos
       │
       ▼
Video Downloader
       │
       ▼
Audio Extraction
       │
       ▼
Speech Processing
       │
       ▼
Database Storage
       │
       ▼
Frontend Application
       │
       ▼
User Recording & Evaluation
```

---

## Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Docker

---

### Frontend

* Angular
* TypeScript
* Bootstrap

---

### AI & Speech Processing

* OpenAI Whisper (Speech-to-Text)
* Transcript Alignment using Sequence Matching
* Word-level speech evaluation
* Audio processing pipelines (chunking, timestamp parsing, segmentation)
* Similarity scoring for pronunciation assessment

---

## Project Goal

The goal of this project is to create an intelligent language learning platform that enables users to improve their speaking skills through real-world content and the shadowing technique in a more effective and interactive way.

---

## Project Setup

### Prerequisites

* Docker
* Docker Compose
* Git

---

### Clone Repository

```bash
git clone https://github.com/GhazalMDI/ASR-shadowing-trainer
cd Speech-shadowing
```

---

### Environment Variables

Create `.env` files and configure database credentials, API keys, and project settings.

---

### Run the Project

```bash
docker compose up --build
```

or

```bash
docker-compose up --build
```

---

### Access the Application

After successful execution, the application will be available via Nginx:

```
http://localhost
```

---

### Services Overview

* Frontend (Angular)
* Backend API (FastAPI)
* PostgreSQL Database
* Nginx Reverse Proxy

All services are managed using Docker Compose.

---

### API Documentation

```
http://localhost/api/docs
```

---

### Stop Services

```bash
docker compose down
```

---

## Deployment Architecture

```
Client
   │
   ▼
Nginx
 ├── Frontend (Angular)
 └── Backend (FastAPI)
           │
           ▼
      PostgreSQL
```
---
# Contact

If you have any questions, suggestions, or feedback about this project, feel free to reach out:

💼 LinkedIn: https://www.linkedin.com/in/ghazal-mohammadi-199986312/
📧 Email: Ghazal.mohammadi.developer@gmail.com

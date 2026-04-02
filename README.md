# KAIST Cafeteria Menu Bot

A Telegram bot that sends daily KAIST cafeteria menus.  
Menus are fetched automatically and summarized using Gemini 2.0 Flash.

---

## Motivation

At KAIST, students often check cafeteria menus before meals.  
Some avoid pork, while others compare menus across cafeterias.

The current process is manual:
- open the KAIST website  
- check multiple cafeteria pages  
- repeat this every day  

This takes time, so many people stop checking.

This project automates that process:
- menus are delivered before lunch and dinner  
- summaries are easy to read  
- pork status is clearly indicated  

Telegram is widely used on campus, so delivery is simple.

---

## Features

- Subscribe a Telegram group to receive menus  
- Automatic updates before meal times  
- Menu summarization using LLM  
- Pork detection included in each menu  
- No manual checking required  

---

## Architecture Overview

### Problem
The KAIST firewall blocks traffic from major cloud providers such as GCP and AWS.  
This prevented direct scraping from a Cloud Run service.

### Solution: Push-Based Bridge

Instead of pulling data from the backend, the system pushes data from a trusted source.

#### Flow

1. **GitHub Actions (Frontend / Bridge)**
   - Runs on a schedule (10:45 AM and 4:45 PM KST)
   - Fetches raw HTML from KAIST cafeteria pages
   - Acts as a trusted network source

2. **Secure Push**
   - Sends the HTML data to the backend via HTTP POST
   - Uses `GIT_ACTIONS_WEBHOOK_SECRET` for authentication

3. **Cloud Run Backend**
   - Receives and validates incoming data
   - Extracts menu information using an LLM
   - Sends summarized results to Telegram

---

## Project Structure

- `.github/workflows/`  
  Contains scheduled jobs for scraping and pushing data

- `main.py`  
  Handles request processing and background tasks

- `llm_service.py`  
  Integrates Gemini 2.0 Flash for:
  - Menu summarization  
  - Basic allergy detection (e.g., pork)

- `telegram_service.py`  
  Sends messages to Telegram  
  Handles cases such as group migrations

---

## Deployment

### Backend (Cloud Run)

```bash
bash scripts/deploy-backend.sh
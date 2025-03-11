# UI

This repository (or module) provides the **user interface** for the AMPLEC project. It is built with [Streamlit](https://streamlit.io/) and interacts with the backend (`core` module) via API calls. The UI module aims to make malware analysis results more accessible and user-friendly by offering a chat-based interface and other pages for uploading samples and configuring settings.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Architecture](#architecture)

---

## Overview
AMPLEC stands for **Automated Malware-analysis Processing with Language Explanation for Consumers**. It is a prototype system that uses Large Language Models (LLMs) to interpret and explain results from an automated malware-analysis pipeline. By using the UI module, users can conveniently upload files, view analysis data, and query the system via a chat-based interface to quickly extract critical insights about the submitted malware.

The UI module consists of three main parts:
1. **Start/Chat Page**: Allows you to interact with the AMPLEC assistant (LLM-based), asking questions about submitted malware or getting deeper insights.
2. **Settings Page**: Lets you configure various aspects of the UI and the underlying LLM interactions.
3. **Upload Page**: Enables the uploading of suspicious files or malware samples to the `core` module.

---

## Features
- **LLM-Powered Chat**: Ask questions about specific malware samples or general malware analysis topics.  
- **Seamless Data Retrieval**: The UI fetches metadata, analysis summaries, and other information from the core module’s APIs.  
- **Streamlit Interface**: Easy to navigate pages (Chat, Settings, and Upload) with a clean and modern look.  
- **Dockerized Deployment**: Simplified setup using `docker compose` with minimal local dependencies.  

---

## Prerequisites
- A system with **Docker** and the **Docker Compose plugin** (often referred to as `docker compose`) installed.
- Port **80** should be available on your machine (or adapt the Docker configuration if it is already in use).
- Tested on **Ubuntu 22.04 LTS** (though other OSes meeting the Docker prerequisites should also work).

---

## Installation
1. **Clone this repository**:
   ```bash
   git clone https://github.com/amplec/ui.git
   ```
2. **Navigate into the cloned folder**:
   ```bash
   cd ui
   ```
3. **Start the container**:
   ```bash
   docker compose up
   ```
   > Add `-d` to run in detached mode:
   > ```bash
   > docker compose up -d
   > ```

Once the container finishes building, the application should be available at [http://localhost](http://localhost) (or the IP/hostname of your server). If you need a different port, adjust it in the Docker configuration.

---

## Usage
When the container is up and running, you can open your web browser and navigate to the exposed port (default: `80`). The UI supports the following core use cases:

1. **Chat with the Assistant**  
   - Go to the Chat page and ask questions about any malware you’ve submitted. For example:  
     - *“Is this sample malicious or benign?”*  
     - *“Which malware family does it resemble?”*  
   - The system leverages the AMPLEC backend to interpret your queries and generate responses using a Large Language Model.

2. **Upload Malware Samples to Karton**  
   - On the Upload page, submit a file for analysis (e.g., a suspected piece of malware).  
   - After karton completes its automated analysis, you can return to the Chat page to ask follow-up questions about the specific sample, or view any logs and results that the UI displays.

3. **Configure Settings**  
   - On the Settings page, tweak various UI or LLM options to tailor the chat experience, such as:  
     - The LLM model to use (depending on your setup).  
     - Desired response detail level.  
     - Other advanced config parameters.
The UI will load you straight into use case 3, if you haven't set some required settings already.
---

## Architecture
The UI module is a Streamlit app that communicates with the `core` module over an internal network (managed by Docker). The high-level flow is:
1. **User Interaction**: A user initiates actions in the UI (e.g., asks a question, uploads a file).  
2. **Core Module**: The UI calls API endpoints on the `core` container, which processes the request (e.g., runs analysis, retrieves or summarizes stored data).  
3. **LLM Support**: The `core` module either uses a local LLM or queries a hosted LLM (depending on your settings).  
4. **Response Display**: The results (e.g., analysis summaries, chat responses) are sent back to the UI and rendered for the user.

```
[ Browser ] <--> [ UI (Streamlit) ] <--> [ Core (API) + LLM ] 
```

**Note:** The AMPLEC system also involves `utils` modules and other internal components that handle tasks like data preprocessing, function-calling logic, or specialized data transformations. However, from the UI perspective, all logic is encapsulated behind the `core` module’s API.

---

### Disclaimer
This project is a prototype to explore how Large Language Models can improve the user experience of malware analysis. It is **not** production-ready and should be used with caution. Always follow strict security guidelines when analyzing potentially malicious files, and never run untrusted code outside of a safe, isolated environment.

---

**Thank you for using the AMPLEC UI module!** If you have any questions or suggestions, feel free to open an issue or reach out to the maintainers.

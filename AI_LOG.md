# AI Collaboration Log

## AI Tech Stack

For this assignment, I primarily used **ChatGPT (OpenAI GPT-5.6 Thinking)** to speed up development across the entire stack. I used it to help design the overall architecture, generate the initial FastAPI backend, build the React frontend, create the Docker setup, and prepare the project documentation. Rather than copying everything directly, I reviewed the generated code, made changes where needed, and tested each component before moving forward.

---

## Prompts That Helped Build the Project

### Backend

> Build a simple FastAPI uptime monitor for a small number of URLs. Use SQLite and SQLAlchemy for storage. The application should allow users to add URLs, list all monitored URLs, manually trigger a health check, view previous checks, and delete a monitor. Store the HTTP status code, response time, timestamp, UP/DOWN status, and any error messages. Use APScheduler to automatically check all registered URLs every 60 seconds. Keep the implementation lightweight and Docker-friendly.

### Frontend

> Create a simple React dashboard for an uptime monitoring application. Users should be able to add URLs, view whether each URL is UP or DOWN, see the latest response time and status code, manually trigger a health check, delete monitors, and have the dashboard refresh automatically every few seconds. Focus on functionality rather than complex UI design.

### Docker Setup

> Create Dockerfiles for both the FastAPI backend and the React frontend. Serve the React build using Nginx, configure Nginx to forward API requests to the backend container, use a Docker volume to persist the SQLite database, and make the entire project start with a single `docker compose up --build` command.

### Documentation

> Write a README explaining how to run the project, how to verify the monitor using both a working and a broken URL, briefly describe the API, and include a simple deployment approach for AWS using Terraform or similar infrastructure.

---

## Course Corrections

AI generated a good starting point, but a few things needed to be corrected during development.

One issue was with the scheduler. The initial design would have executed scheduled health checks in every backend instance if the application were scaled, resulting in duplicate checks. Since this assignment is intended as a simple MVP, I kept a single scheduler instance and mentioned in the documentation that a production system would use a dedicated worker service or a managed scheduler.

Another issue was communication between the frontend and backend inside Docker. Initially, the frontend attempted to call the backend container directly, which does not work from the browser. This was fixed by configuring Nginx as a reverse proxy so that the frontend simply makes requests to `/api`, while Nginx forwards those requests to the backend container internally.

---

## Validation Checklist

The completed application was tested using the following scenarios:

* Added a valid URL and verified that it was displayed as **UP**.
* Added an invalid URL and verified that it was displayed as **DOWN**.
* Confirmed that a health check runs immediately after adding a new URL.
* Verified that scheduled health checks execute every 60 seconds.
* Confirmed that the dashboard updates automatically without refreshing the page.
* Verified that monitoring data remains available after restarting the containers using the Docker volume.
* Confirmed that the complete application starts successfully using a single `docker compose up --build` command.


# Simple Uptime Monitor

This project is a lightweight uptime monitoring application built as a strict MVP. It allows users to register URLs, periodically checks whether they are reachable, records the results of each health check, and displays the latest status along with the response time.

## Tech Stack

**Backend**

* FastAPI
* SQLAlchemy
* SQLite
* APScheduler
* HTTPX

**Frontend**

* React (Vite)
* Nginx

**Containerization**

* Docker Compose

---

## Project Structure

```text
/backend
/frontend
docker-compose.yml
README.md
AI_LOG.md
```

---

## Running the Project

Once Docker Desktop is running, start the entire application using:

```bash
docker compose up --build
```

After the containers start successfully:

* Dashboard: `http://localhost:3000`
* FastAPI Docs: `http://localhost:8000/docs`

---

## How the Application Works

The workflow is intentionally simple:

1. Enter a URL from the dashboard.
2. The backend immediately performs a health check.
3. Every 60 seconds, the scheduler checks all registered URLs again.
4. Each health check stores:

   * HTTP status code
   * Response time
   * Timestamp
   * UP/DOWN status
   * Error message (if any)
5. The frontend refreshes automatically every few seconds so the latest status is always visible.

A URL is considered **UP** when it returns an HTTP response between **200 and 399**. Redirects are followed automatically. Invalid domains, network failures, timeouts, and HTTP 4xx/5xx responses are treated as **DOWN**.

---

## Testing the Application

To verify that the monitor is working correctly:

1. Start the project.

```bash
docker compose up --build
```

2. Open:

```
http://localhost:3000
```

3. Add a working URL:

```
https://example.com
```

4. Add an invalid URL:

```
https://this-domain-should-not-exist.invalid
```

5. Verify the results:

* The valid URL should appear as **UP** along with its response time and HTTP status.
* The invalid URL should appear as **DOWN** with an appropriate network error.

You can either wait for the automatic 60-second health check or click **Check Now** to trigger it immediately.

---

## API Endpoints

| Method | Endpoint                    | Description                                           |
| ------ | --------------------------- | ----------------------------------------------------- |
| POST   | `/api/monitors`             | Register a new URL and perform the first health check |
| GET    | `/api/monitors`             | List all monitored URLs with their latest status      |
| POST   | `/api/monitors/{id}/check`  | Trigger an immediate health check                     |
| GET    | `/api/monitors/{id}/checks` | View previous health checks                           |
| DELETE | `/api/monitors/{id}`        | Remove a monitored URL                                |
| GET    | `/health`                   | Backend health endpoint                               |

---

## Deployment Approach

If this project were deployed to AWS, I would keep the architecture simple while making it suitable for production.

The frontend and backend would each run as separate containers on **Amazon ECS Fargate**. An **Application Load Balancer** would route normal web traffic to the frontend and forward `/api` requests to the backend service. Instead of SQLite, I would use **Amazon RDS PostgreSQL** so that data remains consistent across multiple backend instances. Container images would be stored in **Amazon ECR**, and application logs would be collected using **CloudWatch**.

For scheduled health checks, I would avoid running a scheduler inside every backend instance. Instead, I would use either **Amazon EventBridge Scheduler** or a dedicated worker service to ensure checks run only once.

---

## Design Decisions

Since this assignment focuses on a working MVP, I intentionally kept the architecture straightforward.

* SQLite is sufficient for local development and avoids unnecessary setup.
* APScheduler runs inside the backend to keep the solution simple.
* Docker Compose allows the complete application to start with a single command.
* The frontend communicates with the backend through Nginx, making the application easier to run inside Docker.

---

## Future Improvements

Given more time, I would consider adding:

* User authentication
* Email or Slack alerts when a website goes down
* Retry logic before marking a URL as DOWN
* HTTPS enforcement and SSRF protection
* Historical charts showing response times
* PostgreSQL and Redis for better scalability
* Separate scheduler worker for production deployments
* Monitoring and metrics using Prometheus and Grafana

Overall, the goal of this project was to build a clean, end-to-end uptime monitoring application that is easy to run locally while keeping the implementation simple and maintainable.

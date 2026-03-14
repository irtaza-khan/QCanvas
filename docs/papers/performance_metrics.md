# Application Performance Metrics

This document outlines the key performance metrics you should monitor for your QCanvas application, covering the frontend (Next.js/React), backend (Python/FastAPI), and database. It also includes practical steps on how to measure them.

## 1. Frontend Performance Metrics (Next.js / React)

These metrics measure the experience from the user's perspective in the browser. Next.js and modern browsers track these under the umbrella of Core Web Vitals.

### Key Metrics
*   **LCP (Largest Contentful Paint):** How long it takes for the largest piece of content (like an image or headline text) to appear on the screen.
    *   *Target:* < 2.5 seconds.
*   **INP (Interaction to Next Paint):** How quickly the page responds when a user first interacts with it (e.g., clicking your canvas or a button).
    *   *Target:* < 200 milliseconds.
*   **CLS (Cumulative Layout Shift):** Measures visual stability. It checks if elements on the screen jump around unexpectedly while the page is loading.
    *   *Target:* < 0.1.
*   **FCP (First Contentful Paint):** The time it takes for the *first* piece of text or image to appear.
*   **TTFB (Time to First Byte):** How long the browser waits to receive the first byte of data from your backend/server after making a request.
*   **Bundle Size:** The total size of the JavaScript files sent to the browser. Large bundles delay everything.

### How to Check
1.  **Google Lighthouse:** Built into Chrome DevTools. Press `F12` in Chrome, go to the **Lighthouse** tab, and click "Analyze page load".
2.  **Chrome Network Tab:** Press `F12`, go to the **Network** tab, check "Disable cache", and refresh the page to see how long your individual assets take to load.
3.  **Next.js Speed Insights:** If deployed on Vercel, Next.js provides built-in speed insights in the Vercel dashboard.

---

## 2. Backend Performance Metrics (Python / API)

These metrics measure how efficiently your backend server processes requests.

### Key Metrics
*   **Response Time / Latency:** The total time it takes for your API to receive a request, process it, and send the response back.
    *   *Target:* < 100-200ms per API call for standard requests.
*   **Throughput (Requests Per Second - RPS):** The number of requests your application can handle concurrently in a given second.
*   **Error Rate:** The percentage of requests that result in an error (e.g., HTTP 500). A spike usually indicates performance breakdown under heavy load.
*   **CPU & Memory Usage:** How much of the server's resources your Python application is consuming. High memory usage can lead to garbage collection pauses or crashes.

### How to Check
1.  **Middleware Execution Timing:** In your FastAPI/Python backend, you can add a simple middleware to log the execution time of each endpoint to the console.
2.  **Load Testing (Locust):** Write a Python script using the `locust` library (`pip install locust`) to simulate dozens or hundreds of concurrent users hitting your API endpoints to see where it breaks/slows down.
3.  **APM Tools:** Use Application Performance Monitoring tools if you are deploying to production (e.g., Datadog, New Relic, Prometheus/Grafana).

---

## 3. Database Metrics (SQL / Alembic)

Since the database is often the most common performance bottleneck, keeping an eye on it is crucial.

### Key Metrics
*   **Query Execution Time:** How long it takes for the database to return data for a specific SQL query. Slow queries usually need proper indexing.
*   **N+1 Query Problem:** A common ORM issue where (for example) SQLAlchemy runs 100 small queries instead of 1 large, efficient joined query.
*   **Connection Pool Usage:** How many database connections your Python app is currently opening/using. If exhausted, incoming requests will queue up and time out.
*   **Disk I/O / CPU:** High disk read/write usually means the database is scanning entire tables due to missing indexes.

### How to Check
1.  **SQLAlchemy Echo (Local Dev):** Set `echo=True` in your SQLAlchemy engine configuration to print every SQL query and its execution time to your terminal. This immediately highlights N+1 issues.
2.  **EXPLAIN ANALYZE:** Run the `EXPLAIN ANALYZE` command before a raw SQL query in your database client (like pgAdmin or DBeaver) to see why the engine is taking a long time to execute it.
3.  **Database Dashboards:** If using a managed database (like AWS RDS or Supabase), use their built-in metrics dashboards to monitor CPU, Connections, and slow queries.

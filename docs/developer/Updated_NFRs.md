# Non-Functional Requirements (NFRs)

## 2.2.1 Reliability
*   **NFR-R1: Service Availability**
    *   *The system containers (Backend, Database, Redis) shall report a 'healthy' status code (200 OK) on their health check endpoints 99.9% of the time during active operation.*
    *   **Rationale:** Ensures high availability of the core infrastructure components.
*   **NFR-R2: Audit Trail**
    *   *The system shall record an audit log entry in the `ApiActivity` table for 100% of API requests resulting in 4xx or 5xx status codes.*
    *   **Rationale:** Critical for security monitoring and troubleshooting.

## 2.2.2 Usability
*   **NFR-U1: Keyboard Efficiency**
    *   *The system shall execute the current quantum circuit when the user triggers the `Ctrl+Shift+R` (or `Cmd+Shift+R`) key combination.*
    *   **Rationale:** Provides a specific, measurable efficiency constraint for power users.
*   **NFR-U2: Visual Accessibility**
    *   *The user interface shall utilize the Monaco Editor's high-contrast `vs-dark` or `vs` theme standards to ensure text legibility.*
    *   **Rationale:** Ensures compliance with accessibility standards for the primary work surface.

## 2.2.3 Performance
*   **NFR-P1: Conversion Latency**
    *   *The API shall process circuit conversion requests (AST parsing to QASM generation) in under 1500ms for circuits with <100 gates.*
    *   **Rationale:** Sets a measurable performance budget for the core specific task of the application.
*   **NFR-P2: Simulation Throughput**
    *   *The simulator shall complete execution of standard algorithms (e.g., Grover's Search n=2) in under 5 seconds.*
    *   **Rationale:** measurable constraint on the simulation engine's efficiency.

## 2.2.4 Security
*   **NFR-S1: API Rate Limiting**
    *   *The API shall strictly enforce a rate limit of **20 requests per minute** per client IP address for conversion endpoints.*
    *   **Rationale:** Prevents abuse and specifically matches the current implementation capacity.
*   **NFR-S2: Encryption Standards**
    *   *The application shall enforce HTTP Strict Transport Security (HSTS) with a max-age of at least 1 year (31536000 seconds).*
    *   **Rationale:** Enforces modern security best practices for data in transit.
*   **NFR-S3: Data Integrity Protection**
    *   *The system shall sanitize 100% of user inputs via ORM parameterization to prevent SQL injection vulnerabilities.*
    *   **Rationale:** Mandates a specific security control for data layer interactions.

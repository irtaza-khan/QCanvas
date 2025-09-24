import express from "express";
import cors from "cors";
import { handleDemo } from "./routes/demo";
import { handleQuantumExecution } from "./routes/quantum";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    res.json({ message: "Hello from Express server v2!" });
  });

  app.get("/api/demo", handleDemo);

  // Quantum execution endpoint
  app.post("/api/quantum/execute", handleQuantumExecution);

  return app;
}

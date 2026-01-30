
import os
import sys
import uuid
import random
from datetime import datetime, timedelta

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.config.database import SessionLocal
from app.models.database_models import (
    User, Project, File, Job, Conversion, ConversionStats, 
    Simulation, Session, ApiActivity, UserRole, 
    QuantumFramework, SimulationBackend, ExecutionStatus, 
    SessionType, JobStatus
)
from app.utils.security import SecurityUtils

def populate_dummy_data():
    db = SessionLocal()
    try:
        print("Starting to populate database with dummy data...")
        
        # 1. Create Users
        print("Creating Users...")
        users = []
        roles = [UserRole.USER, UserRole.ADMIN, UserRole.USER, UserRole.USER, UserRole.USER]
        
        for i in range(5):
            user = User(
                email=f"user{i+1}@example.com",
                username=f"user{i+1}",
                full_name=f"Test User {i+1}",
                role=roles[i],
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            user.set_password("password123")
            db.add(user)
            users.append(user)
        
        db.commit()
        for u in users:
            db.refresh(u)
            
        # 2. Create Projects
        print("Creating Projects...")
        projects = []
        for i in range(5):
            owner = random.choice(users)
            project = Project(
                user_id=owner.id,
                name=f"Project {chr(65+i)}", # Project A, B, C...
                description=f"This is a dummy project description for project {i+1}.",
                is_public=random.choice([True, False]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            db.add(project)
            projects.append(project)
            
        db.commit()
        for p in projects:
            db.refresh(p)
            
        # 3. Create Files
        print("Creating Files...")
        files = []
        for i in range(5):
            project = projects[i] # One file per project for simplicity
            file = File(
                user_id=project.user_id,
                project_id=project.id,
                filename=f"script_{i+1}.py",
                content=f"# Dummy python script {i+1}\nprint('Hello Quantum World {i+1}')",
                is_main=True,
                is_shared=project.is_public
            )
            db.add(file)
            files.append(file)
            
        db.commit()
        
        # 4. Create Jobs
        print("Creating Jobs...")
        for i in range(5):
            user = random.choice(users)
            project = random.choice(projects)
            job = Job(
                user_id=user.id,
                project_id=project.id,
                status=random.choice(list(JobStatus)),
                backend=random.choice(["aer_simulator", "ibmq_qasm_simulator"]),
                shots=1024,
                execution_time_ms=random.randint(100, 5000) if random.random() > 0.3 else None,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.add(job)
            
        # 5. Create Conversions and Stats
        print("Creating Conversions...")
        for i in range(5):
            user = random.choice(users)
            status = random.choice(list(ExecutionStatus))
            conversion = Conversion(
                user_id=user.id,
                source_framework=random.choice(list(QuantumFramework)),
                target_framework=random.choice(list(QuantumFramework)),
                source_code="# source code",
                target_code="# target code" if status == ExecutionStatus.SUCCESS else None,
                status=status,
                execution_time_ms=random.randint(50, 1000) if status == ExecutionStatus.SUCCESS else None
            )
            db.add(conversion)
            db.flush() # flush to get ID
            
            if status == ExecutionStatus.SUCCESS:
                stats = ConversionStats(
                    conversion_id=conversion.id,
                    num_qubits=random.randint(2, 10),
                    num_gates=random.randint(5, 50),
                    circuit_depth=random.randint(5, 30)
                )
                db.add(stats)
                
        # 6. Create Simulations
        print("Creating Simulations...")
        for i in range(5):
            user = random.choice(users)
            status = random.choice(list(ExecutionStatus))
            simulation = Simulation(
                user_id=user.id,
                qasm_code='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;',
                backend=random.choice(list(SimulationBackend)),
                shots=1024,
                status=status,
                execution_time_ms=random.randint(100, 2000) if status == ExecutionStatus.SUCCESS else None
            )
            db.add(simulation)
            
        # 7. Create Sessions
        print("Creating Sessions...")
        for i in range(5):
            user = random.choice(users)
            session = Session(
                user_id=user.id,
                session_token=str(uuid.uuid4()),
                session_type=random.choice(list(SessionType)),
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.add(session)
            
        # 8. Create ApiActivity
        print("Creating API Activities...")
        endpoints = ["/api/v1/convert", "/api/v1/simulate", "/api/v1/projects", "/api/v1/auth/login"]
        methods = ["GET", "POST", "PUT", "DELETE"]
        for i in range(5):
            user = random.choice(users)
            activity = ApiActivity(
                user_id=user.id,
                endpoint=random.choice(endpoints),
                method=random.choice(methods),
                status_code=random.choice([200, 201, 400, 401, 404, 500]),
                ip_address=f"10.0.0.{random.randint(1, 255)}",
                user_agent="PostmanRuntime/7.28.0",
                response_time_ms=random.randint(10, 500)
            )
            db.add(activity)
            
        db.commit()
        print("✅ Database successfully populated with dummy data!")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_dummy_data()

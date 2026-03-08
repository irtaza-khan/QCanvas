"""
Achievement definitions for QCanvas Gamification System.

This module defines all available badges and achievements based on the 
QCanvas Gamification Plan. Each achievement has:
- name: Unique display name
- description: How to unlock it
- category: Grouping for UI display
- criteria: Machine-evaluable unlock conditions (JSON)
- reward_xp: XP awarded upon unlocking
- rarity: common, uncommon, rare, epic, legendary
- icon_name: Lucide icon identifier for frontend
- is_hidden: Whether shown before unlocking
"""

# Criteria types:
# - "activity_count": Count occurrences of activity_type
#     e.g. {"type": "activity_count", "activity_type": "simulation_run", "count": 100}
# - "level_reached": User reached a certain level
#     e.g. {"type": "level_reached", "level": 5}
# - "streak_days": Current or longest streak reached N days
#     e.g. {"type": "streak_days", "days": 7}
# - "total_xp": Total XP threshold
#     e.g. {"type": "total_xp", "xp": 1000}
# - "distinct_activity_count": Count distinct values in metadata field
#     e.g. {"type": "distinct_activity_count", "activity_type": "conversion", "metadata_field": "target_framework", "count": 3}
# - "multi_activity_count": Count across multiple activity types
#     e.g. {"type": "multi_activity_count", "activity_types": ["simulation_run", "conversion"], "count": 5}

ACHIEVEMENT_DEFINITIONS = [
    # =========================================================================
    # 🌟 GETTING STARTED BADGES
    # =========================================================================
    {
        "name": "First Steps",
        "description": "Create your first quantum circuit.",
        "category": "getting_started",
        "criteria": {"type": "activity_count", "activity_type": "circuit_saved", "count": 1},
        "reward_xp": 50,
        "rarity": "common",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "Hello Quantum",
        "description": "Run your first quantum simulation.",
        "category": "getting_started",
        "criteria": {"type": "activity_count", "activity_type": "simulation_run", "count": 1},
        "reward_xp": 75,
        "rarity": "common",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "Framework Explorer",
        "description": "Try all 3 quantum frameworks (Qiskit, Cirq, PennyLane).",
        "category": "getting_started",
        "criteria": {"type": "distinct_activity_count", "activity_type": "conversion", "metadata_field": "target_framework", "count": 3},
        "reward_xp": 150,
        "rarity": "rare",
        "icon_name": "compass",
        "is_hidden": False,
    },
    {
        "name": "Gate Master",
        "description": "Use all basic gates (H, X, Z, CNOT) in your circuits.",
        "category": "getting_started",
        "criteria": {"type": "distinct_activity_count", "activity_type": "simulation_run", "metadata_field": "gates_used", "count": 4},
        "reward_xp": 100,
        "rarity": "uncommon",
        "icon_name": "star",
        "is_hidden": False,
    },

    # =========================================================================
    # 🔬 ALGORITHM BADGES
    # =========================================================================
    {
        "name": "Entanglement Expert",
        "description": "Create 10 entangled circuits.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "entangled_circuit", "count": 10},
        "reward_xp": 200,
        "rarity": "rare",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Superposition Savant",
        "description": "Use superposition in 20 circuits.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "superposition_circuit", "count": 20},
        "reward_xp": 150,
        "rarity": "rare",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Deutsch Detective",
        "description": "Implement the Deutsch-Jozsa algorithm.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "algorithm_deutsch", "count": 1},
        "reward_xp": 300,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Grover's Guardian",
        "description": "Implement Grover's search algorithm.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "algorithm_grover", "count": 1},
        "reward_xp": 400,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Shor's Scholar",
        "description": "Implement Shor's factoring algorithm.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "algorithm_shor", "count": 1},
        "reward_xp": 500,
        "rarity": "legendary",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "VQE Virtuoso",
        "description": "Implement the VQE algorithm.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "algorithm_vqe", "count": 1},
        "reward_xp": 400,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "QAOA Champion",
        "description": "Implement the QAOA algorithm.",
        "category": "algorithms",
        "criteria": {"type": "activity_count", "activity_type": "algorithm_qaoa", "count": 1},
        "reward_xp": 450,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },

    # =========================================================================
    # 🏆 MASTERY BADGES
    # =========================================================================
    {
        "name": "Qubit Wrangler",
        "description": "Simulate 100 quantum circuits.",
        "category": "mastery",
        "criteria": {"type": "activity_count", "activity_type": "simulation_run", "count": 100},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "target",
        "is_hidden": False,
    },
    {
        "name": "Conversion King",
        "description": "Convert 50 circuits between frameworks.",
        "category": "mastery",
        "criteria": {"type": "activity_count", "activity_type": "conversion", "count": 50},
        "reward_xp": 250,
        "rarity": "rare",
        "icon_name": "target",
        "is_hidden": False,
    },
    {
        "name": "Getting the Hang of It",
        "description": "Run 10 simulations successfully.",
        "category": "mastery",
        "criteria": {"type": "activity_count", "activity_type": "simulation_run", "count": 10},
        "reward_xp": 100,
        "rarity": "uncommon",
        "icon_name": "target",
        "is_hidden": False,
    },
    {
        "name": "Perfectionist",
        "description": "Create 25 error-free circuit simulations.",
        "category": "mastery",
        "criteria": {"type": "activity_count", "activity_type": "simulation_run", "count": 25},
        "reward_xp": 350,
        "rarity": "rare",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Speed Demon",
        "description": "Complete 10 circuits in under 5 minutes each.",
        "category": "mastery",
        "criteria": {"type": "activity_count", "activity_type": "fast_circuit", "count": 10},
        "reward_xp": 200,
        "rarity": "uncommon",
        "icon_name": "target",
        "is_hidden": False,
    },

    # =========================================================================
    # 📚 LEARNING BADGES
    # =========================================================================
    {
        "name": "Tutorial Completionist",
        "description": "Complete all available tutorials.",
        "category": "learning",
        "criteria": {"type": "activity_count", "activity_type": "tutorial_completed", "count": 10},
        "reward_xp": 500,
        "rarity": "epic",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Quiz Master",
        "description": "Score 90%+ on 10 quizzes.",
        "category": "learning",
        "criteria": {"type": "activity_count", "activity_type": "quiz_passed", "count": 10},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Challenge Accepted",
        "description": "Complete 20 challenges.",
        "category": "learning",
        "criteria": {"type": "activity_count", "activity_type": "challenge_completed", "count": 20},
        "reward_xp": 400,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Concept Master",
        "description": "Master 5 different quantum concepts.",
        "category": "learning",
        "criteria": {"type": "activity_count", "activity_type": "concept_mastered", "count": 5},
        "reward_xp": 350,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },

    # =========================================================================
    # 🔥 STREAK BADGES
    # =========================================================================
    {
        "name": "7-Day Streak",
        "description": "Practice for 7 consecutive days.",
        "category": "streak",
        "criteria": {"type": "streak_days", "days": 7},
        "reward_xp": 150,
        "rarity": "uncommon",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "30-Day Streak",
        "description": "Practice for 30 consecutive days.",
        "category": "streak",
        "criteria": {"type": "streak_days", "days": 30},
        "reward_xp": 500,
        "rarity": "rare",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "100-Day Streak",
        "description": "Practice for 100 consecutive days.",
        "category": "streak",
        "criteria": {"type": "streak_days", "days": 100},
        "reward_xp": 1500,
        "rarity": "legendary",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "Weekend Warrior",
        "description": "Complete 10 weekend challenges.",
        "category": "streak",
        "criteria": {"type": "activity_count", "activity_type": "weekend_challenge", "count": 10},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "rocket",
        "is_hidden": False,
    },

    # =========================================================================
    # 👥 SOCIAL BADGES
    # =========================================================================
    {
        "name": "Collaborator",
        "description": "Share 10 circuits with the community.",
        "category": "social",
        "criteria": {"type": "activity_count", "activity_type": "circuit_shared", "count": 10},
        "reward_xp": 150,
        "rarity": "uncommon",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Community Helper",
        "description": "Help 10 other users.",
        "category": "social",
        "criteria": {"type": "activity_count", "activity_type": "helped_user", "count": 10},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Upvote Champion",
        "description": "Receive 100 upvotes on your circuits.",
        "category": "social",
        "criteria": {"type": "activity_count", "activity_type": "received_upvote", "count": 100},
        "reward_xp": 400,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },
    {
        "name": "Mentor",
        "description": "Help 5 beginners complete their first circuit.",
        "category": "social",
        "criteria": {"type": "activity_count", "activity_type": "mentored_beginner", "count": 5},
        "reward_xp": 500,
        "rarity": "epic",
        "icon_name": "award",
        "is_hidden": False,
    },

    # =========================================================================
    # 🎓 SPECIALIZATION BADGES
    # =========================================================================
    {
        "name": "Qiskit Specialist",
        "description": "Complete 50 circuits using Qiskit.",
        "category": "specialization",
        "criteria": {"type": "activity_count", "activity_type": "qiskit_circuit", "count": 50},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Cirq Expert",
        "description": "Complete 50 circuits using Cirq.",
        "category": "specialization",
        "criteria": {"type": "activity_count", "activity_type": "cirq_circuit", "count": 50},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "PennyLane Pro",
        "description": "Complete 50 circuits using PennyLane.",
        "category": "specialization",
        "criteria": {"type": "activity_count", "activity_type": "pennylane_circuit", "count": 50},
        "reward_xp": 300,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Multi-Framework Master",
        "description": "Become an expert in all 3 quantum frameworks.",
        "category": "specialization",
        "criteria": {"type": "multi_activity_count", "activity_types": ["qiskit_circuit", "cirq_circuit", "pennylane_circuit"], "count": 25},
        "reward_xp": 1000,
        "rarity": "legendary",
        "icon_name": "award",
        "is_hidden": False,
    },

    # =========================================================================
    # 🏅 PROGRESSION BADGES
    # =========================================================================
    {
        "name": "Level 5 Achieved",
        "description": "Reach Level 5 — Quantum Novice mastered!",
        "category": "progression",
        "criteria": {"type": "level_reached", "level": 5},
        "reward_xp": 100,
        "rarity": "uncommon",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Level 10 Achieved",
        "description": "Reach Level 10 — Circuit Builder status!",
        "category": "progression",
        "criteria": {"type": "level_reached", "level": 10},
        "reward_xp": 200,
        "rarity": "uncommon",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Level 20 Achieved",
        "description": "Reach Level 20 — Quantum Explorer!",
        "category": "progression",
        "criteria": {"type": "level_reached", "level": 20},
        "reward_xp": 400,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Level 30 Achieved",
        "description": "Reach Level 30 — Algorithm Designer!",
        "category": "progression",
        "criteria": {"type": "level_reached", "level": 30},
        "reward_xp": 600,
        "rarity": "epic",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "Level 50 Achieved",
        "description": "Reach Level 50 — Quantum Master!",
        "category": "progression",
        "criteria": {"type": "level_reached", "level": 50},
        "reward_xp": 1000,
        "rarity": "legendary",
        "icon_name": "star",
        "is_hidden": False,
    },
    {
        "name": "XP Milestone: 1K",
        "description": "Earn a total of 1,000 XP.",
        "category": "progression",
        "criteria": {"type": "total_xp", "xp": 1000},
        "reward_xp": 50,
        "rarity": "common",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "XP Milestone: 10K",
        "description": "Earn a total of 10,000 XP.",
        "category": "progression",
        "criteria": {"type": "total_xp", "xp": 10000},
        "reward_xp": 200,
        "rarity": "rare",
        "icon_name": "rocket",
        "is_hidden": False,
    },
    {
        "name": "XP Milestone: 50K",
        "description": "Earn a total of 50,000 XP.",
        "category": "progression",
        "criteria": {"type": "total_xp", "xp": 50000},
        "reward_xp": 500,
        "rarity": "epic",
        "icon_name": "rocket",
        "is_hidden": False,
    },

    # =========================================================================
    # 🌈 HIDDEN / SECRET BADGES
    # =========================================================================
    {
        "name": "Easter Egg Hunter",
        "description": "Find the hidden feature in QCanvas.",
        "category": "hidden",
        "criteria": {"type": "activity_count", "activity_type": "easter_egg_found", "count": 1},
        "reward_xp": 250,
        "rarity": "epic",
        "icon_name": "star",
        "is_hidden": True,
    },
    {
        "name": "Night Owl",
        "description": "Complete 10 circuits after midnight.",
        "category": "hidden",
        "criteria": {"type": "activity_count", "activity_type": "night_circuit", "count": 10},
        "reward_xp": 200,
        "rarity": "uncommon",
        "icon_name": "star",
        "is_hidden": True,
    },
    {
        "name": "Early Bird",
        "description": "Complete 10 circuits before 6 AM.",
        "category": "hidden",
        "criteria": {"type": "activity_count", "activity_type": "early_circuit", "count": 10},
        "reward_xp": 200,
        "rarity": "uncommon",
        "icon_name": "star",
        "is_hidden": True,
    },
    {
        "name": "Lucky Number",
        "description": "Create a circuit with exactly 42 gates.",
        "category": "hidden",
        "criteria": {"type": "activity_count", "activity_type": "lucky_42_circuit", "count": 1},
        "reward_xp": 150,
        "rarity": "rare",
        "icon_name": "star",
        "is_hidden": True,
    },
]


# Category display names for the frontend
ACHIEVEMENT_CATEGORIES = {
    "getting_started": "Getting Started",
    "algorithms": "Algorithms",
    "mastery": "Mastery",
    "learning": "Learning",
    "streak": "Streak",
    "social": "Social",
    "specialization": "Specialization",
    "progression": "Progression",
    "hidden": "Hidden",
}

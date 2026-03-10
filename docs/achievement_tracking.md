# 🔧 Achievement Tracking — Technical Reference

> **File:** `docs/achievement_tracking.md`  
> **Backend:** `backend/app/services/gamification_service.py`  
> **Definitions:** `backend/app/services/achievement_definitions.py`  
> **Migration:** `backend/alembic/versions/b2c3d4e5f6a7_seed_achievement_definitions.py`

This document explains **exactly how** each of the 44 achievements is tracked, evaluated, and unlocked in the QCanvas backend.

---

## Table of Contents

1. [How the System Works (Architecture)](#how-the-system-works)
2. [The 6 Criteria Types](#the-6-criteria-types)
3. [Activity Types Reference](#activity-types-reference)
4. [Tracking Per Achievement — All 44](#tracking-per-achievement)
   - [Getting Started (4)](#-getting-started)
   - [Algorithms (7)](#-algorithms)
   - [Mastery (5)](#-mastery)
   - [Learning (4)](#-learning)
   - [Streak (4)](#-streak)
   - [Social (4)](#-social)
   - [Specialization (4)](#-specialization)
   - [Progression (8)](#-progression)
   - [Hidden (4)](#-hidden)
5. [Database Schema](#database-schema)
6. [Known Limitations](#known-limitations)

---

## How the System Works

### Full Flow: Activity → Achievement Check

```
User performs action
       │
       ▼
POST /api/gamification/activity
  { "activity_type": "simulation_run", "metadata": {...} }
       │
       ▼
GamificationService.award_xp()
  1. Looks up XP reward from XP_REWARDS dict
  2. Checks if it's the user's first time (first-time bonus)
  3. Inserts row into gamification_activities table
  4. Updates user_gamification (total_xp, level, streak, last_activity_date)
  5. Commits to DB
       │
       ▼
GamificationService.check_achievements()
  1. Loads ALL 44 achievements from DB
  2. Loads user's already-unlocked achievement IDs (to skip them)
  3. Loads activity_summary = COUNT of each activity_type the user has ever done
  4. Loads user stats (level, total_xp, current_streak, longest_streak)
  5. For each unearned achievement → calls _evaluate_criteria()
  6. If criteria met → calls _unlock_achievement()
       │
       ▼
_unlock_achievement()
  1. Creates/updates UserAchievement row with unlocked_at = now()
  2. Adds achievement.reward_xp directly to user_gamification.total_xp
  3. Logs an 'achievement_unlocked' activity row (for history)
  4. Returns the achievement dict to include in the API response
       │
       ▼
Response includes new_achievements[] — frontend shows toast notifications
```

> **Key point:** Achievement checking happens on **every single** XP-awarding activity. There is no separate job or cron — it's always inline and synchronous.

---

## The 6 Criteria Types

All 44 achievements use exactly one of these 6 criteria types, defined in the `criteria` JSON column of the `achievements` table.

### 1. `activity_count`
**Most common type.** Counts how many times the user has performed a specific activity.

```json
{ "type": "activity_count", "activity_type": "simulation_run", "count": 10 }
```

**Evaluation:**
```python
current_count = activity_summary[activity_type]['count']
return current_count >= required_count
```

**Progress display:** `current_count / count`

---

### 2. `level_reached`
Checks the user's current level against the `user_gamification.level` column.

```json
{ "type": "level_reached", "level": 10 }
```

**Evaluation:**
```python
return stats.level >= required_level
```

**Progress display:** `current_level / required_level` (e.g., `7 / 10`)

---

### 3. `streak_days`
Checks the user's **best ever streak** — `max(current_streak, longest_streak)`.

```json
{ "type": "streak_days", "days": 7 }
```

**Evaluation:**
```python
best_streak = max(stats.current_streak, stats.longest_streak)
return best_streak >= required_days
```

**How streak is maintained:** Each time XP is awarded, the system compares `today` to `last_activity_date`:
- Same day → streak unchanged
- Next day (diff = 1) → streak +1, update longest if exceeded
- Skipped day (diff > 1) → streak resets to 1

**Progress display:** `best_streak / required_days`

---

### 4. `total_xp`
Checks the user's cumulative XP from the `user_gamification.total_xp` column.

```json
{ "type": "total_xp", "xp": 1000 }
```

**Evaluation:**
```python
return stats.total_xp >= required_xp
```

**Progress display:** `current_total_xp / required_xp` (capped at target for display)

> Note: XP from achievements themselves is included in `total_xp` since it's added directly to the column.

---

### 5. `distinct_activity_count`
**Current approximation:** Counts the *total* number of times an activity was performed, not true distinct values (e.g., distinct frameworks). Full distinct tracking requires metadata indexing — planned for a future update.

```json
{ "type": "distinct_activity_count", "activity_type": "conversion", "metadata_field": "target_framework", "count": 3 }
```

**Evaluation (current):**
```python
# Uses total count as a proxy — not truly checking distinct metadata values yet
current_count = activity_summary[activity_type]['count']
return current_count >= required_count
```

**Progress display:** Always shows `0 / target` for locked achievements (cannot compute distinct without metadata scan). Shows `target / target` when unlocked.

**Affects:** Framework Explorer, Gate Master

---

### 6. `multi_activity_count`
Requires **each** of multiple activity types to reach a minimum count. All must meet the threshold.

```json
{ "type": "multi_activity_count", "activity_types": ["qiskit_circuit", "cirq_circuit", "pennylane_circuit"], "count": 25 }
```

**Evaluation:**
```python
for act_type in activity_types:
    if activity_summary[act_type]['count'] < required_count:
        return False
return True
```

**Progress display:** Shows the minimum count across all activity types (the "weakest link") vs the required count.

**Affects:** Multi-Framework Master

---

## Activity Types Reference

This is the full list of activity type strings that trigger XP and feed into achievement evaluation. All are sent via `POST /api/gamification/activity`.

| Activity Type | Base XP | Who calls it | Notes |
|--------------|---------|-------------|-------|
| `simulation_run` | 10 XP | Simulation service | Most common activity |
| `first_simulation` | 50 XP | Simulation service | Auto-applied on very first simulation |
| `conversion` | 30 XP | Converter service | Any framework-to-framework conversion |
| `first_conversion` | 60 XP | Converter service | Auto-applied on very first conversion |
| `circuit_saved` | 5 XP | Circuit editor | Every save |
| `project_created` | 25 XP | Project service | Creating a new project |
| `tutorial_completed` | 100 XP | Learning module | Per tutorial finished |
| `challenge_completed` | 150 XP | Challenge system | Per challenge completed |
| `circuit_shared` | 25 XP | Social feature | Per public share |
| `helped_user` | 50 XP | Community system | Verified help action |
| `entangled_circuit` | — | Simulation service | Logged alongside `simulation_run` for entangled results |
| `superposition_circuit` | — | Simulation service | Logged when circuit uses H gate |
| `algorithm_deutsch` | — | Algorithm service | Deutsch-Jozsa implementation |
| `algorithm_grover` | — | Algorithm service | Grover's search |
| `algorithm_shor` | — | Algorithm service | Shor's factoring |
| `algorithm_vqe` | — | Algorithm service | VQE hybrid algorithm |
| `algorithm_qaoa` | — | Algorithm service | QAOA algorithm |
| `fast_circuit` | — | Simulation service | Circuit completed in < 5 minutes |
| `quiz_passed` | — | Learning module | Quiz score ≥ 90% |
| `concept_mastered` | — | Learning module | All exercises for a concept done |
| `received_upvote` | — | Social feature | Upvote received on shared circuit |
| `mentored_beginner` | — | Mentorship system | Beginner completed first circuit with mentor |
| `qiskit_circuit` | — | Simulation service | Simulation using Qiskit framework |
| `cirq_circuit` | — | Simulation service | Simulation using Cirq framework |
| `pennylane_circuit` | — | Simulation service | Simulation using PennyLane framework |
| `weekend_challenge` | — | Challenge system | Challenge completed on Sat/Sun |
| `night_circuit` | — | Simulation service | Simulation after midnight (local time) |
| `early_circuit` | — | Simulation service | Simulation before 6 AM (local time) |
| `lucky_42_circuit` | — | Simulation service | Circuit with exactly 42 gates |
| `easter_egg_found` | — | Various | Hidden interaction discovered |
| `achievement_unlocked` | varies | Achievement system | Auto-logged when any badge is earned |

> Activities with `—` for XP have no default XP in `XP_REWARDS` and rely on the calling service to pass `xp_amount` explicitly, or yield 0 XP if not explicitly set.

---

## Tracking Per Achievement

### 🌟 Getting Started

---

#### First Steps
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `circuit_saved` activity log |
| **Trigger** | Log activity `circuit_saved` |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(circuit_saved_count, 1) / 1` |

**When does it fire?** The very first time the simulation service logs `circuit_saved` for this user.

---

#### Hello Quantum
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `simulation_run` activity log |
| **Trigger** | Log activity `simulation_run` |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(simulation_run_count, 1) / 1` |

**When does it fire?** The first successful simulation logs `simulation_run`. Note: the very first also gets a `first_simulation` bonus (50 XP instead of 10 XP).

---

#### Framework Explorer
| Field | Value |
|-------|-------|
| **Criteria type** | `distinct_activity_count` |
| **Tracked via** | `conversion` activity log |
| **Trigger** | Log activity `conversion` (any framework pair) |
| **Threshold** | Count ≥ **3** (intended: 3 *distinct* target frameworks) |
| **Progress formula** | `0 / 3` while locked (distinct count not yet computed), `3 / 3` when unlocked |

> **⚠️ Current limitation:** The system counts *total* conversions, not distinct target frameworks. So 3 Qiskit→Cirq conversions would satisfy this. True distinct-framework checking is a planned improvement.

---

#### Gate Master
| Field | Value |
|-------|-------|
| **Criteria type** | `distinct_activity_count` |
| **Tracked via** | `simulation_run` activity log |
| **Trigger** | Log activity `simulation_run` with gate metadata |
| **Threshold** | Count ≥ **4** (intended: 4 distinct gate types used) |
| **Progress formula** | `0 / 4` while locked, `4 / 4` when unlocked |

> **⚠️ Current limitation:** Same as Framework Explorer — counts total simulations ≥ 4, not distinct gate types.

---

### 🔬 Algorithms

---

#### Entanglement Expert
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `entangled_circuit` activity log |
| **Trigger** | Simulation service logs `entangled_circuit` after detecting entanglement |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(entangled_circuit_count, 10) / 10` |

---

#### Superposition Savant
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `superposition_circuit` activity log |
| **Trigger** | Simulation service logs `superposition_circuit` when circuit includes an H gate |
| **Threshold** | Count ≥ **20** |
| **Progress formula** | `min(superposition_circuit_count, 20) / 20` |

---

#### Deutsch Detective
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `algorithm_deutsch` activity log |
| **Trigger** | Algorithm service logs `algorithm_deutsch` for successful Deutsch-Jozsa run |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(algorithm_deutsch_count, 1) / 1` |

---

#### Grover's Guardian
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `algorithm_grover` activity log |
| **Trigger** | Algorithm service logs `algorithm_grover` for successful Grover's search run |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(algorithm_grover_count, 1) / 1` |

---

#### Shor's Scholar
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `algorithm_shor` activity log |
| **Trigger** | Algorithm service logs `algorithm_shor` for successful Shor's factoring run |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(algorithm_shor_count, 1) / 1` |

---

#### VQE Virtuoso
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `algorithm_vqe` activity log |
| **Trigger** | Algorithm service logs `algorithm_vqe` for successful VQE run |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(algorithm_vqe_count, 1) / 1` |

---

#### QAOA Champion
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `algorithm_qaoa` activity log |
| **Trigger** | Algorithm service logs `algorithm_qaoa` for successful QAOA run |
| **Threshold** | Count ≥ **1** |
| **Progress formula** | `min(algorithm_qaoa_count, 1) / 1` |

---

### 🏆 Mastery

---

#### Getting the Hang of It
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `simulation_run` activity log |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(simulation_run_count, 10) / 10` |

*Shared counter with Hello Quantum, Perfectionist, and Qubit Wrangler — all use `simulation_run`.*

---

#### Perfectionist
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `simulation_run` activity log |
| **Threshold** | Count ≥ **25** |
| **Progress formula** | `min(simulation_run_count, 25) / 25` |

---

#### Qubit Wrangler
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `simulation_run` activity log |
| **Threshold** | Count ≥ **100** |
| **Progress formula** | `min(simulation_run_count, 100) / 100` |

---

#### Conversion King
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `conversion` activity log |
| **Threshold** | Count ≥ **50** |
| **Progress formula** | `min(conversion_count, 50) / 50` |

---

#### Speed Demon
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `fast_circuit` activity log |
| **Trigger** | Simulation service logs `fast_circuit` when time from circuit open to simulation < 5 minutes |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(fast_circuit_count, 10) / 10` |

---

### 📚 Learning

---

#### Tutorial Completionist
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `tutorial_completed` activity log |
| **Trigger** | Learning module logs `tutorial_completed` when a tutorial is finished |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(tutorial_completed_count, 10) / 10` |

---

#### Quiz Master
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `quiz_passed` activity log |
| **Trigger** | Learning module logs `quiz_passed` when quiz score ≥ 90% |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(quiz_passed_count, 10) / 10` |

---

#### Challenge Accepted
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `challenge_completed` activity log |
| **Trigger** | Challenge system logs `challenge_completed` when any challenge is finished |
| **Threshold** | Count ≥ **20** |
| **Progress formula** | `min(challenge_completed_count, 20) / 20` |

---

#### Concept Master
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `concept_mastered` activity log |
| **Trigger** | Learning module logs `concept_mastered` when all exercises for a concept are completed |
| **Threshold** | Count ≥ **5** |
| **Progress formula** | `min(concept_mastered_count, 5) / 5` |

---

### 🔥 Streak

---

#### 7-Day Streak
| Field | Value |
|-------|-------|
| **Criteria type** | `streak_days` |
| **Tracked via** | `user_gamification.current_streak` and `longest_streak` columns |
| **Trigger** | Any XP-awarding activity on a new day |
| **Threshold** | `max(current_streak, longest_streak)` ≥ **7** |
| **Progress formula** | `min(best_streak, 7) / 7` |

---

#### 30-Day Streak
| Field | Value |
|-------|-------|
| **Criteria type** | `streak_days` |
| **Tracked via** | `user_gamification.current_streak` and `longest_streak` columns |
| **Threshold** | `max(current_streak, longest_streak)` ≥ **30** |
| **Progress formula** | `min(best_streak, 30) / 30` |

---

#### 100-Day Streak
| Field | Value |
|-------|-------|
| **Criteria type** | `streak_days` |
| **Tracked via** | `user_gamification.current_streak` and `longest_streak` columns |
| **Threshold** | `max(current_streak, longest_streak)` ≥ **100** |
| **Progress formula** | `min(best_streak, 100) / 100` |

---

#### Weekend Warrior
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `weekend_challenge` activity log |
| **Trigger** | Challenge system checks if today is Saturday/Sunday when logging `challenge_completed`, then additionally logs `weekend_challenge` |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(weekend_challenge_count, 10) / 10` |

---

### 👥 Social

---

#### Collaborator
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `circuit_shared` activity log |
| **Trigger** | Social service logs `circuit_shared` when a circuit is made public |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(circuit_shared_count, 10) / 10` |

---

#### Community Helper
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `helped_user` activity log |
| **Trigger** | Community system logs `helped_user` for verified help actions |
| **Threshold** | Count ≥ **10** |
| **Progress formula** | `min(helped_user_count, 10) / 10` |

---

#### Upvote Champion
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `received_upvote` activity log |
| **Trigger** | Social service logs `received_upvote` when another user upvotes a shared circuit |
| **Threshold** | Count ≥ **100** |
| **Progress formula** | `min(received_upvote_count, 100) / 100` |

---

#### Mentor
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `mentored_beginner` activity log |
| **Trigger** | Mentorship system logs `mentored_beginner` when a mentee completes their first circuit |
| **Threshold** | Count ≥ **5** |
| **Progress formula** | `min(mentored_beginner_count, 5) / 5` |

---

### 🎓 Specialization

---

#### Qiskit Specialist
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `qiskit_circuit` activity log |
| **Trigger** | Simulation service logs `qiskit_circuit` after each successful Qiskit simulation |
| **Threshold** | Count ≥ **50** |
| **Progress formula** | `min(qiskit_circuit_count, 50) / 50` |

---

#### Cirq Expert
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `cirq_circuit` activity log |
| **Trigger** | Simulation service logs `cirq_circuit` after each successful Cirq simulation |
| **Threshold** | Count ≥ **50** |
| **Progress formula** | `min(cirq_circuit_count, 50) / 50` |

---

#### PennyLane Pro
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `pennylane_circuit` activity log |
| **Trigger** | Simulation service logs `pennylane_circuit` after each successful PennyLane simulation |
| **Threshold** | Count ≥ **50** |
| **Progress formula** | `min(pennylane_circuit_count, 50) / 50` |

---

#### Multi-Framework Master
| Field | Value |
|-------|-------|
| **Criteria type** | `multi_activity_count` |
| **Tracked via** | `qiskit_circuit`, `cirq_circuit`, `pennylane_circuit` activity logs |
| **Threshold** | **Each** of the 3 activity types ≥ **25** |
| **Progress formula** | `min(min_of_all_three, 25) / 25` (bottlenecked by the lowest count) |

**Evaluation logic:**
```python
# Returns False as soon as ANY framework falls below 25
for act_type in ["qiskit_circuit", "cirq_circuit", "pennylane_circuit"]:
    if activity_summary[act_type]['count'] < 25:
        return False
return True
```

---

### 🏅 Progression

---

#### Level 5 Achieved
| Field | Value |
|-------|-------|
| **Criteria type** | `level_reached` |
| **Tracked via** | `user_gamification.level` column |
| **Trigger** | Any XP-awarding activity that pushes `total_xp` past 2,000 XP |
| **Threshold** | `level` ≥ **5** (requires 2,000 total XP at 500 XP/level) |
| **Progress formula** | `min(current_level, 5) / 5` |

---

#### Level 10 Achieved
| Field | Value |
|-------|-------|
| **Criteria type** | `level_reached` |
| **Tracked via** | `user_gamification.level` column |
| **Threshold** | `level` ≥ **10** (requires 4,500 total XP) |
| **Progress formula** | `min(current_level, 10) / 10` |

---

#### Level 20 Achieved
| Field | Value |
|-------|-------|
| **Criteria type** | `level_reached` |
| **Tracked via** | `user_gamification.level` column |
| **Threshold** | `level` ≥ **20** (requires 9,500 total XP) |
| **Progress formula** | `min(current_level, 20) / 20` |

---

#### Level 30 Achieved
| Field | Value |
|-------|-------|
| **Criteria type** | `level_reached` |
| **Tracked via** | `user_gamification.level` column |
| **Threshold** | `level` ≥ **30** (requires 14,500 total XP) |
| **Progress formula** | `min(current_level, 30) / 30` |

---

#### Level 50 Achieved
| Field | Value |
|-------|-------|
| **Criteria type** | `level_reached` |
| **Tracked via** | `user_gamification.level` column |
| **Threshold** | `level` ≥ **50** (requires 24,500 total XP) |
| **Progress formula** | `min(current_level, 50) / 50` |

---

#### XP Milestone: 1K
| Field | Value |
|-------|-------|
| **Criteria type** | `total_xp` |
| **Tracked via** | `user_gamification.total_xp` column |
| **Trigger** | Any XP-awarding activity that pushes `total_xp` past 1,000 |
| **Threshold** | `total_xp` ≥ **1,000** |
| **Progress formula** | `min(total_xp, 1000) / 1000` |

---

#### XP Milestone: 10K
| Field | Value |
|-------|-------|
| **Criteria type** | `total_xp` |
| **Tracked via** | `user_gamification.total_xp` column |
| **Threshold** | `total_xp` ≥ **10,000** |
| **Progress formula** | `min(total_xp, 10000) / 10000` |

---

#### XP Milestone: 50K
| Field | Value |
|-------|-------|
| **Criteria type** | `total_xp` |
| **Tracked via** | `user_gamification.total_xp` column |
| **Threshold** | `total_xp` ≥ **50,000** |
| **Progress formula** | `min(total_xp, 50000) / 50000` |

---

### 🌈 Hidden

> Hidden achievements are tracked exactly the same as regular ones. Their names and descriptions are masked in the API response until they are unlocked. Progress is hidden (shown as `0/1`) while locked.

---

#### Easter Egg Hunter *(Hidden)*
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `easter_egg_found` activity log |
| **Trigger** | Logs `easter_egg_found` when user interacts with a specific hidden UI element or feature |
| **Threshold** | Count ≥ **1** |

---

#### Night Owl *(Hidden)*
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `night_circuit` activity log |
| **Trigger** | Simulation service logs `night_circuit` when a simulation is run after midnight (local time) |
| **Threshold** | Count ≥ **10** |

---

#### Early Bird *(Hidden)*
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `early_circuit` activity log |
| **Trigger** | Simulation service logs `early_circuit` when a simulation is run before 06:00 (local time) |
| **Threshold** | Count ≥ **10** |

---

#### Lucky Number *(Hidden)*
| Field | Value |
|-------|-------|
| **Criteria type** | `activity_count` |
| **Tracked via** | `lucky_42_circuit` activity log |
| **Trigger** | Simulation service counts the total gates in the circuit. If exactly 42, logs `lucky_42_circuit` |
| **Threshold** | Count ≥ **1** |

---

## Database Schema

```sql
-- Stores the achievement definitions (seeded by Alembic migration)
CREATE TABLE achievements (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    category    VARCHAR(50)  NOT NULL,          -- 'getting_started', 'algorithms', etc.
    criteria    JSONB        NOT NULL,           -- { "type": "...", ...params }
    reward_xp   INTEGER      NOT NULL DEFAULT 0,
    rarity      VARCHAR(20)  NOT NULL DEFAULT 'common',
    icon_name   VARCHAR(50),
    is_hidden   BOOLEAN      NOT NULL DEFAULT false,
    created_at  TIMESTAMP    NOT NULL DEFAULT now()
);

-- Stores each user's progress and unlock status for each achievement
CREATE TABLE user_achievements (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    progress       JSONB,                        -- { "current": N, "target": N }
    unlocked_at    TIMESTAMP,                    -- NULL = not yet completed
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(user_id, achievement_id)              -- One record per user per achievement
);

-- Stores every XP-awarding activity event (the raw log)
CREATE TABLE gamification_activities (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    xp_awarded    INTEGER NOT NULL,
    metadata      JSONB,
    created_at    TIMESTAMP NOT NULL DEFAULT now()
);

-- Stores aggregate user stats (level, total xp, streaks)
CREATE TABLE user_gamification (
    user_id           UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_xp          INTEGER NOT NULL DEFAULT 0,
    level             INTEGER NOT NULL DEFAULT 1,
    current_streak    INTEGER NOT NULL DEFAULT 0,
    longest_streak    INTEGER NOT NULL DEFAULT 0,
    last_activity_date DATE,
    created_at        TIMESTAMP NOT NULL DEFAULT now(),
    updated_at        TIMESTAMP NOT NULL DEFAULT now()
);
```

**How activity_summary is computed:**
```sql
-- Equivalent to what get_activity_summary() runs:
SELECT activity_type, COUNT(*) as count, SUM(xp_awarded) as total_xp
FROM gamification_activities
WHERE user_id = :user_id
GROUP BY activity_type
```

---

## Known Limitations

| # | Limitation | Affected Achievements | Planned Fix |
|---|-----------|----------------------|-------------|
| 1 | **`distinct_activity_count` uses total count, not true distinct metadata values** | Framework Explorer, Gate Master | Query distinct values from `activity_metadata` JSON column |
| 2 | **Night Owl / Early Bird use server time, not user local time** | Night Owl, Early Bird | Pass user timezone in metadata and adjust server-side |
| 3 | **Achievement check scans ALL 44 achievements on every activity** | All | Add category/type filtering so only relevant achievements are evaluated |
| 4 | **No partial progress persistence for `distinct_activity_count`** | Framework Explorer, Gate Master | Store distinct-value sets in `user_achievements.progress` |
| 5 | **XP from achievement bonuses can itself trigger further achievements** | XP Milestones | This is intentional but creates a cascade — achievement XP is not re-checked recursively |

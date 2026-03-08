# 🏆 QCanvas Achievements & Badges Guide

> **Last Updated:** March 8, 2026  
> **Version:** 1.1  
> **Total Achievements:** 44

This document lists every badge and achievement in QCanvas, how to complete each one, what XP it rewards, and its rarity tier.

---

## 📖 Table of Contents

1. [How Achievements Work](#how-achievements-work)
2. [Rarity System](#rarity-system)
3. [🌟 Getting Started](#-getting-started-4-badges)
4. [🔬 Algorithms](#-algorithms-7-badges)
5. [🏆 Mastery](#-mastery-5-badges)
6. [📚 Learning](#-learning-4-badges)
7. [🔥 Streak](#-streak-4-badges)
8. [👥 Social](#-social-4-badges)
9. [🎓 Specialization](#-specialization-4-badges)
10. [🏅 Progression](#-progression-8-badges)
11. [🌈 Hidden / Secret](#-hidden--secret-4-badges)
12. [Quick Reference Table](#quick-reference-table)

---

## How Achievements Work

### Do achievements need to be unlocked before I can make progress?

**No.** All 44 achievements are **always active and tracking your progress from the moment you create your account.** There is no prerequisites, no unlock order, and no activation step. Simply use QCanvas — build circuits, run simulations, convert code, and your progress towards every achievement is recorded automatically in the background.

### Achievement States

Every achievement is always in one of three states:

| State | Icon | Description |
|-------|------|-------------|
| ✅ **Completed** | 🏆 Trophy | You have met all criteria. The badge is earned, XP has been awarded, and a timestamp shows when it was unlocked. |
| 🔄 **In Progress** | 🔓 Lock | You have made *partial* progress toward the criteria (e.g., 5 out of 10 simulations). Keep going! |
| ⬜ **Not Started** | 🔒 Lock | You have not yet made any progress toward this achievement (0 / target). The achievement is still active and will start tracking as soon as you perform the relevant activity. |

> **Key Point:** You do **not** need to complete one achievement before starting another. All 44 achievements track simultaneously.

### How Completion Works

1. You perform an activity (e.g., run a simulation, convert a circuit, save a file)
2. The system awards XP for that activity
3. **Immediately after**, the achievement engine checks all 44 achievement criteria against your stats
4. If any criteria are now met, the achievement is **automatically completed** and you receive:
   - The achievement's **bonus XP** reward
   - A **toast notification** showing the badge you just earned
   - The badge moves to the **Completed** section on the Achievements page

### Hidden Achievements

Achievements in the **Hidden** category have their name and description masked as `???` until completed. You can still see they exist and their rarity, but you won't know what they require until you discover them. Once completed, the name and description are revealed.

---

## Rarity System

Each badge has a rarity tier that reflects how difficult it is to earn:

| Rarity | Color | Description |
|--------|-------|-------------|
| ⬜ **Common** | Gray | Easy to obtain — participation-based milestones |
| 🟢 **Uncommon** | Green | Requires consistent effort over time |
| 🔵 **Rare** | Blue | Significant achievement — takes dedicated practice |
| 🟣 **Epic** | Purple | Exceptional accomplishment — mastery-level skill |
| 🟡 **Legendary** | Gold | Extremely rare — top-tier dedication and mastery |

> Badges at Epic and Legendary rarity display animated glow effects on your profile.

---

## 🌟 Getting Started (4 badges)

These are the first badges new users will encounter. They guide you through the core features of QCanvas.

---

### First Steps
| Field | Value |
|-------|-------|
| **Rarity** | ⬜ Common |
| **XP Reward** | +50 XP |
| **Category** | Getting Started |

**How to unlock:**  
Save your first quantum circuit on QCanvas. Open the circuit editor, build any circuit (even a single qubit with one gate), and save it.

**Tips:**
- This is the very first badge most users earn
- Any circuit works — there is no minimum size requirement
- Saving is triggered when you click the Save button or use Ctrl+S

---

### Hello Quantum
| Field | Value |
|-------|-------|
| **Rarity** | ⬜ Common |
| **XP Reward** | +75 XP |
| **Category** | Getting Started |

**How to unlock:**  
Run your first quantum simulation. Build any circuit and press the **Run** / **Simulate** button.

**Tips:**
- Complements "First Steps" — build a circuit, then run it
- A Bell state circuit (H gate on qubit 0 + CNOT between qubit 0 and 1) is a great first simulation
- Any successful simulation counts, regardless of complexity

---

### Framework Explorer
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +150 XP |
| **Category** | Getting Started |

**How to unlock:**  
Convert circuits in all 3 supported quantum frameworks: **Qiskit**, **Cirq**, and **PennyLane**.

**Steps:**
1. Write or open a circuit in any supported framework
2. Use the Converter to target a different framework
3. Repeat until you have converted to all three: Qiskit, Cirq, and PennyLane

**Tips:**
- You do not need to convert the same circuit — any 3 conversion targets count
- Converting Qiskit → Cirq, Cirq → PennyLane, and PennyLane → Qiskit would satisfy the requirement

---

### Gate Master
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +100 XP |
| **Category** | Getting Started |

**How to unlock:**  
Use all 4 basic quantum gates in your circuits across multiple simulations: **H** (Hadamard), **X** (Pauli-X), **Z** (Pauli-Z), and **CNOT** (Controlled-NOT).

**Steps:**
1. Run simulations that include an H gate
2. Run simulations that include an X gate
3. Run simulations that include a Z gate
4. Run simulations that include a CNOT gate

**Tips:**
- The gates can be spread across different simulations — you don't need all 4 in a single circuit
- A Bell state uses H + CNOT. Add X and Z in separate experiments to complete the set

---

## 🔬 Algorithms (7 badges)

These badges reward implementing specific quantum algorithms. They range from introductory entanglement to legendary algorithms like Shor's factoring.

---

### Entanglement Expert
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +200 XP |
| **Category** | Algorithms |

**How to unlock:**  
Create and simulate **10 entangled circuits**. An entangled circuit is any circuit that produces quantum entanglement between qubits.

**Steps:**
1. Build a circuit using at least an H gate followed by a CNOT gate on two qubits
2. Run the simulation so the entanglement is registered
3. Repeat 10 times total

**Tips:**
- The classic Bell state (`H(q0)` → `CNOT(q0, q1)`) counts every time
- You can vary qubits, gate orders, and backends — each successful simulation counts separately

---

### Superposition Savant
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +150 XP |
| **Category** | Algorithms |

**How to unlock:**  
Use superposition in **20 circuits**. Any circuit that applies an H (Hadamard) gate to put a qubit into superposition qualifies.

**Steps:**
1. Include at least one H gate in your circuit
2. Run the simulation
3. Repeat across 20 different simulation runs

**Tips:**
- Every Bell state you create also counts toward this badge
- Combine with Entanglement Expert for efficient progress on both

---

### Deutsch Detective
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +300 XP |
| **Category** | Algorithms |

**How to unlock:**  
Successfully implement the **Deutsch-Jozsa algorithm** in QCanvas.

**What the Deutsch-Jozsa algorithm does:**  
Determines whether a black-box function is constant (always 0 or always 1) or balanced (outputs 0 for half the inputs and 1 for the other half) with a single query — exponentially faster than any classical approach.

**Steps:**
1. Build a circuit that implements the Deutsch-Jozsa oracle
2. Apply Hadamard gates to all input qubits, apply the oracle, then apply Hadamard again
3. Measure and simulate
4. The system tracks this as an `algorithm_deutsch` activity

**Resources:**
- For a 1-qubit oracle (Deutsch's problem): H → Oracle → H → Measure
- For n qubits: Apply H to all n+1 qubits, apply oracle, apply H to first n qubits, measure

---

### Grover's Guardian
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +400 XP |
| **Category** | Algorithms |

**How to unlock:**  
Successfully implement **Grover's search algorithm** in QCanvas.

**What Grover's algorithm does:**  
Searches an unstructured database of N items in O(√N) time — a quadratic speedup over classical linear search.

**Steps:**
1. Initialize qubits in superposition using H gates
2. Apply the Grover oracle (marks the target state with a phase flip)
3. Apply the Grover diffusion operator (inversion about the mean)
4. Repeat oracle + diffusion for approximately √N iterations
5. Measure — the target state should have the highest probability

**Tips:**
- Even a 2-qubit Grover's search (searching 4 items) qualifies
- The system tracks this as an `algorithm_grover` activity

---

### Shor's Scholar
| Field | Value |
|-------|-------|
| **Rarity** | 🟡 Legendary |
| **XP Reward** | +500 XP |
| **Category** | Algorithms |

**How to unlock:**  
Successfully implement **Shor's factoring algorithm** in QCanvas.

**What Shor's algorithm does:**  
Factors an integer N in polynomial time using quantum Fourier transform and period-finding — a theoretically exponential speedup over the best known classical algorithms.

**Steps:**
1. Implement the quantum phase estimation subroutine (uses QFT)
2. Pick a random coprime `a < N`
3. Find the period `r` of the function `f(x) = a^x mod N` using quantum period-finding
4. Compute `gcd(a^(r/2) ± 1, N)` to extract factors
5. Simulate and measure

**Tips:**
- This is one of the hardest achievements — take your time
- Start with factoring small numbers (e.g., N = 15 = 3 × 5)
- The system tracks this as an `algorithm_shor` activity

---

### VQE Virtuoso
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +400 XP |
| **Category** | Algorithms |

**How to unlock:**  
Implement the **Variational Quantum Eigensolver (VQE)** algorithm.

**What VQE does:**  
A hybrid quantum-classical algorithm that finds the ground state energy of a quantum system (e.g., a molecule). It uses a classical optimizer to tune the parameters of a quantum ansatz circuit.

**Steps:**
1. Define a Hamiltonian (e.g., a simple Pauli operator)
2. Build a parameterized ansatz circuit (e.g., Ry rotations)
3. Estimate the expectation value ⟨ψ|H|ψ⟩ using the quantum circuit
4. Use a classical optimizer (e.g., gradient descent) to minimize the energy
5. Simulate and register as `algorithm_vqe`

---

### QAOA Champion
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +450 XP |
| **Category** | Algorithms |

**How to unlock:**  
Implement the **Quantum Approximate Optimization Algorithm (QAOA)**.

**What QAOA does:**  
A hybrid quantum-classical algorithm designed for combinatorial optimization problems (e.g., Max-Cut). It alternates between a cost unitary and a mixer unitary, optimized by a classical loop.

**Steps:**
1. Encode your combinatorial problem as a Hamiltonian (e.g., Max-Cut on a graph)
2. Build the QAOA ansatz: alternating cost and mixer layers
3. Optimize the circuit parameters (γ, β) classically
4. Simulate the final circuit
5. Register as `algorithm_qaoa`

---

## 🏆 Mastery (5 badges)

These badges reward putting in the work — lots of simulations, conversions, and fast circuits.

---

### Getting the Hang of It
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +100 XP |
| **Category** | Mastery |

**How to unlock:**  
Run **10 quantum simulations** successfully.

**Tips:**
- This is an early milestone that most active users will earn within their first few sessions
- Any simulation counts, regardless of complexity or backend
- Failed simulations (errors) do not count — make sure your circuits are valid

---

### Perfectionist
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +350 XP |
| **Category** | Mastery |

**How to unlock:**  
Run **25 error-free simulations**. Each successful simulation (no runtime errors) counts toward this total.

**Tips:**
- Validate your circuit syntax before running to avoid errors
- Use simple, well-tested circuits to rack up count quickly
- Progresses alongside "Getting the Hang of It" and "Qubit Wrangler"

---

### Qubit Wrangler
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Mastery |

**How to unlock:**  
Run **100 quantum circuit simulations** in total.

**Tips:**
- A long-term badge — plan to earn this over many sessions
- Every simulation you run counts toward both "Perfectionist" and "Qubit Wrangler"
- Using the simulator frequently for experiments and learning will naturally get you there

---

### Conversion King
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +250 XP |
| **Category** | Mastery |

**How to unlock:**  
Convert **50 circuits** between quantum frameworks using the QCanvas converter.

**Tips:**
- Every conversion (any pair of frameworks, any direction) counts
- Combine with "Framework Explorer" and the Specialization badges for efficient progress
- Converting the same circuit to different targets counts separately each time

---

### Speed Demon
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +200 XP |
| **Category** | Mastery |

**How to unlock:**  
Complete **10 circuits in under 5 minutes each** — from opening to running the simulation.

**Tips:**
- Pre-plan your circuit structure before starting the timer
- Simple circuits (Bell states, single-qubit rotations) are fastest to build
- Keyboard shortcuts and the circuit editor make this more achievable
- The system tracks this as a `fast_circuit` activity

---

## 📚 Learning (4 badges)

These badges reward engaging with QCanvas's structured learning content: tutorials, quizzes, and challenges.

---

### Concept Master
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +350 XP |
| **Category** | Learning |

**How to unlock:**  
Master **5 different quantum concepts**. A concept is considered mastered when you complete all associated exercises or modules for that topic.

**Tips:**
- Each concept mastery is registered as a `concept_mastered` activity
- Focus on foundational concepts first: superposition, entanglement, interference, measurement, quantum gates

---

### Quiz Master
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Learning |

**How to unlock:**  
Score **90% or higher on 10 quizzes**.

**Tips:**
- Read through the associated tutorial material before attempting each quiz
- Review your incorrect answers and retry — scores below 90% do not count
- Each qualifying score registers as a `quiz_passed` activity

---

### Challenge Accepted
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +400 XP |
| **Category** | Learning |

**How to unlock:**  
Complete **20 challenges** on QCanvas. Challenges include daily, weekly, and structured problem-solving tasks.

**Tips:**
- Daily challenges refresh every 24 hours — check in regularly
- Weekly quests count toward this total
- Each completed challenge is logged as a `challenge_completed` activity

---

### Tutorial Completionist
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +500 XP |
| **Category** | Learning |

**How to unlock:**  
Complete **all 10 available tutorials** on QCanvas.

**Tips:**
- Work through each tutorial in order — later ones build on earlier foundations
- Each completed tutorial registers as a `tutorial_completed` activity
- This badge pairs well with Concept Master and Quiz Master for a full learning sweep

---

## 🔥 Streak (4 badges)

These badges reward consistency. A "streak" is the number of consecutive calendar days on which you perform at least one activity on QCanvas.

> **⚠️ Streak Rules:**
> - A streak is broken if you skip a full calendar day with zero activity
> - Streak badges check your **longest ever streak**, not just the current one — so a broken streak doesn't prevent these badges if you already passed the milestone
> - Streak Freeze Tokens (earned every 7-day streak) can protect your streak if you miss a day

---

### 7-Day Streak
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +150 XP |
| **Category** | Streak |

**How to unlock:**  
Be active on QCanvas for **7 consecutive days**.

**Tips:**
- Any activity counts — run a simulation, convert a circuit, or save a file
- Log in every day for a week, even for a quick one-minute experiment
- Unlocking this badge also grants you your first **Streak Freeze Token**

---

### 30-Day Streak
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +500 XP |
| **Category** | Streak |

**How to unlock:**  
Be active on QCanvas for **30 consecutive days**.

**Tips:**
- Use your Streak Freeze Tokens for unavoidable missed days
- Set a daily reminder or calendar event to keep yourself on track
- Every 7-day streak milestone gives you a new Freeze Token (max 3 stored)

---

### 100-Day Streak
| Field | Value |
|-------|-------|
| **Rarity** | 🟡 Legendary |
| **XP Reward** | +1,500 XP |
| **Category** | Streak |

**How to unlock:**  
Be active on QCanvas for **100 consecutive days**.

**Tips:**
- This is the ultimate consistency badge — only the most dedicated users earn it
- Over 100 days you'll earn up to 14 Freeze Tokens (one every 7 days), giving you solid protection
- The XP reward is 1,500 XP — one of the highest single-badge payouts in the game

---

### Weekend Warrior
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Streak |

**How to unlock:**  
Complete **10 weekend challenges** (challenges completed on Saturdays or Sundays).

**Tips:**
- Check the daily/weekly challenges section every Saturday and Sunday
- Each weekend challenge completion is logged as a `weekend_challenge` activity
- Spread across 5 weekends minimum (2 per weekend)

---

## 👥 Social (4 badges)

These badges reward engaging with the QCanvas community — sharing your work and helping others.

---

### Collaborator
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +150 XP |
| **Category** | Social |

**How to unlock:**  
Share **10 circuits** publicly in the QCanvas circuit gallery.

**Steps:**
1. Build and run a circuit
2. Click the **Share** button and make it public
3. Repeat 10 times

**Tips:**
- Add descriptions and tags to your shared circuits for better community engagement
- Each share is logged as a `circuit_shared` activity

---

### Community Helper
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Social |

**How to unlock:**  
Help **10 other users** on QCanvas. This includes responding to questions, providing verified assistance, or contributing meaningful comments.

**Tips:**
- Each verified help action is logged as a `helped_user` activity
- Focus on quality over quantity — spammy or low-effort help may not qualify
- This badge pairs well toward unlocking the Mentor badge

---

### Upvote Champion
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +400 XP |
| **Category** | Social |

**How to unlock:**  
Have your circuits receive **100 upvotes** from the community in total.

**Tips:**
- Share high-quality, well-documented circuits with descriptive names and tags
- Interesting algorithms and novel implementations attract the most upvotes
- Each upvote received is logged as a `received_upvote` activity (max 100 XP from upvotes per day)

---

### Mentor
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +500 XP |
| **Category** | Social |

**How to unlock:**  
Help **5 beginners** complete their first quantum circuit through the mentorship program.

**Requirements:**
- You must be Level 30+ to access Mentor Mode
- Match with beginners through the mentorship system
- Each mentee who completes their first circuit with your guidance counts

**Tips:**
- Each successful mentorship logs as a `mentored_beginner` activity
- This is one of the most rewarding social badges — both XP-wise and for the community

---

## 🎓 Specialization (4 badges)

These badges reward deep expertise in a specific quantum computing framework.

---

### Qiskit Specialist
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Specialization |

**How to unlock:**  
Complete **50 circuits using the Qiskit framework**.

**Tips:**
- Write and simulate circuits using Qiskit syntax in QCanvas
- Each Qiskit circuit simulation registers as a `qiskit_circuit` activity
- A great complement to the Cirq Expert and PennyLane Pro badges

---

### Cirq Expert
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Specialization |

**How to unlock:**  
Complete **50 circuits using the Cirq framework**.

**Tips:**
- Write and simulate circuits using Cirq syntax in QCanvas
- Each Cirq circuit simulation registers as a `cirq_circuit` activity
- Explore Cirq's moment-based circuit structure and native gate set

---

### PennyLane Pro
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +300 XP |
| **Category** | Specialization |

**How to unlock:**  
Complete **50 circuits using the PennyLane framework**.

**Tips:**
- Write and simulate circuits using PennyLane syntax in QCanvas
- Each PennyLane circuit simulation registers as a `pennylane_circuit` activity
- PennyLane is especially useful for variational circuits and quantum machine learning

---

### Multi-Framework Master
| Field | Value |
|-------|-------|
| **Rarity** | 🟡 Legendary |
| **XP Reward** | +1,000 XP |
| **Category** | Specialization |

**How to unlock:**  
Become an expert in **all 3 frameworks** — complete at least **25 circuits in each** of Qiskit, Cirq, and PennyLane (75 total).

**Tips:**
- This badge requires earning Qiskit Specialist, Cirq Expert, and PennyLane Pro first (those require 50 each — well past the 25 threshold)
- Plan to earn the three individual specialization badges first; this one will unlock automatically at the 25-per-framework mark
- The 1,000 XP reward makes this one of the most valuable achievable badges

---

## 🏅 Progression (8 badges)

These badges track your overall growth on the platform — leveling up and accumulating XP.

---

### Level 5 Achieved
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +100 XP |
| **Category** | Progression |

**How to unlock:**  
Reach **Level 5** (requires 2,000 total XP at 500 XP per level).

---

### Level 10 Achieved
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +200 XP |
| **Category** | Progression |

**How to unlock:**  
Reach **Level 10** (requires 4,500 total XP).  
At this level your title becomes **Circuit Builder**.

---

### Level 20 Achieved
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +400 XP |
| **Category** | Progression |

**How to unlock:**  
Reach **Level 20** (requires 9,500 total XP).  
At this level your title becomes **Quantum Explorer**.

---

### Level 30 Achieved
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +600 XP |
| **Category** | Progression |

**How to unlock:**  
Reach **Level 30** (requires 14,500 total XP).  
At this level your title becomes **Algorithm Designer** and you unlock **Mentor Mode**.

---

### Level 50 Achieved
| Field | Value |
|-------|-------|
| **Rarity** | 🟡 Legendary |
| **XP Reward** | +1,000 XP |
| **Category** | Progression |

**How to unlock:**  
Reach **Level 50** (requires 24,500 total XP).  
At this level your title becomes **Quantum Master** — the pinnacle of the QCanvas leveling system.

---

### XP Milestone: 1K
| Field | Value |
|-------|-------|
| **Rarity** | ⬜ Common |
| **XP Reward** | +50 XP |
| **Category** | Progression |

**How to unlock:**  
Accumulate **1,000 total XP** from any activities.

---

### XP Milestone: 10K
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +200 XP |
| **Category** | Progression |

**How to unlock:**  
Accumulate **10,000 total XP** from any activities.

---

### XP Milestone: 50K
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +500 XP |
| **Category** | Progression |

**How to unlock:**  
Accumulate **50,000 total XP** from any activities.

---

## 🌈 Hidden / Secret (4 badges)

These badges are hidden until unlocked — their names and descriptions are shown as `???` on the achievements page. They reward unusual behavior and Easter eggs.

> **Note:** The unlock conditions listed here are spoilers. Read at your own risk!

---

### Easter Egg Hunter *(Hidden)*
| Field | Value |
|-------|-------|
| **Rarity** | 🟣 Epic |
| **XP Reward** | +250 XP |
| **Category** | Hidden |
| **Shown before unlock?** | No |

**How to unlock:**  
Find the **hidden feature** in QCanvas. This is an intentional Easter egg deliberately built into the platform.

**Hint:** Explore beyond the obvious UI — try unexpected interactions, keyboard shortcuts, or clicking on unusual interface elements.

---

### Night Owl *(Hidden)*
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +200 XP |
| **Category** | Hidden |
| **Shown before unlock?** | No |

**How to unlock:**  
Complete **10 circuit simulations after midnight** (local time, 12:00 AM – 5:59 AM).

**Tips:**
- Your device's local clock determines the time
- Spread this over multiple late-night sessions
- Each late-night simulation is logged as a `night_circuit` activity

---

### Early Bird *(Hidden)*
| Field | Value |
|-------|-------|
| **Rarity** | 🟢 Uncommon |
| **XP Reward** | +200 XP |
| **Category** | Hidden |
| **Shown before unlock?** | No |

**How to unlock:**  
Complete **10 circuit simulations before 6:00 AM** (local time).

**Tips:**
- The flip side of Night Owl — you can't earn both from the same sessions
- Each early-morning simulation is logged as an `early_circuit` activity
- Set your alarm a bit earlier and squeeze in a few circuits before the day starts

---

### Lucky Number *(Hidden)*
| Field | Value |
|-------|-------|
| **Rarity** | 🔵 Rare |
| **XP Reward** | +150 XP |
| **Category** | Hidden |
| **Shown before unlock?** | No |

**How to unlock:**  
Create and simulate a circuit with **exactly 42 gates** — not 41, not 43.

**Tips:**
- Count your gates carefully before running the simulation
- Any gate types can be used — the total gate count must equal exactly 42
- Logged as a `lucky_42_circuit` activity

---

## Quick Reference Table

All 44 achievements sorted by XP reward (descending):

| Badge | Category | Rarity | XP |
|-------|----------|--------|----|
| 100-Day Streak | Streak | 🟡 Legendary | 1,500 |
| Multi-Framework Master | Specialization | 🟡 Legendary | 1,000 |
| Level 50 Achieved | Progression | 🟡 Legendary | 1,000 |
| Tutorial Completionist | Learning | 🟣 Epic | 500 |
| Mentor | Social | 🟣 Epic | 500 |
| Shor's Scholar | Algorithms | 🟡 Legendary | 500 |
| 30-Day Streak | Streak | 🔵 Rare | 500 |
| XP Milestone: 50K | Progression | 🟣 Epic | 500 |
| QAOA Champion | Algorithms | 🟣 Epic | 450 |
| Grover's Guardian | Algorithms | 🟣 Epic | 400 |
| VQE Virtuoso | Algorithms | 🟣 Epic | 400 |
| Challenge Accepted | Learning | 🔵 Rare | 400 |
| Upvote Champion | Social | 🟣 Epic | 400 |
| Level 30 Achieved | Progression | 🟣 Epic | 600 |
| Level 20 Achieved | Progression | 🔵 Rare | 400 |
| Perfectionist | Mastery | 🔵 Rare | 350 |
| Concept Master | Learning | 🔵 Rare | 350 |
| Deutsch Detective | Algorithms | 🟣 Epic | 300 |
| Qubit Wrangler | Mastery | 🔵 Rare | 300 |
| Community Helper | Social | 🔵 Rare | 300 |
| Weekend Warrior | Streak | 🔵 Rare | 300 |
| Qiskit Specialist | Specialization | 🔵 Rare | 300 |
| Cirq Expert | Specialization | 🔵 Rare | 300 |
| PennyLane Pro | Specialization | 🔵 Rare | 300 |
| Quiz Master | Learning | 🔵 Rare | 300 |
| Easter Egg Hunter | Hidden | 🟣 Epic | 250 |
| Conversion King | Mastery | 🔵 Rare | 250 |
| Entanglement Expert | Algorithms | 🔵 Rare | 200 |
| Speed Demon | Mastery | 🟢 Uncommon | 200 |
| Night Owl | Hidden | 🟢 Uncommon | 200 |
| Early Bird | Hidden | 🟢 Uncommon | 200 |
| Level 10 Achieved | Progression | 🟢 Uncommon | 200 |
| XP Milestone: 10K | Progression | 🔵 Rare | 200 |
| Superposition Savant | Algorithms | 🔵 Rare | 150 |
| Framework Explorer | Getting Started | 🔵 Rare | 150 |
| 7-Day Streak | Streak | 🟢 Uncommon | 150 |
| Collaborator | Social | 🟢 Uncommon | 150 |
| Lucky Number | Hidden | 🔵 Rare | 150 |
| Gate Master | Getting Started | 🟢 Uncommon | 100 |
| Getting the Hang of It | Mastery | 🟢 Uncommon | 100 |
| Level 5 Achieved | Progression | 🟢 Uncommon | 100 |
| Hello Quantum | Getting Started | ⬜ Common | 75 |
| First Steps | Getting Started | ⬜ Common | 50 |
| XP Milestone: 1K | Progression | ⬜ Common | 50 |

---

*For questions about the gamification system, see the [Gamification Plan](./gamification_plan.md) or the [Gamification Implementation Guide](./gamification_implementation_guide.md).*

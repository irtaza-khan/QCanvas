# Design System Specification: Quantum Research & Computation

## 1. Overview & Creative North Star: "The Observational Void"
The Creative North Star for this design system is **"The Observational Void."** In quantum mechanics, the act of observation changes the state of the particle. This system mimics that precision and sensitivity. We move away from the "cluttered dashboard" trope into a high-fidelity, editorial environment that feels like a clean-room laboratory.

To break the "template" look, we utilize **Intentional Asymmetry**. Significant negative space (breathing room) is used to isolate critical data points, while overlapping glass layers create a sense of three-dimensional depth. This is not just a UI; it is a high-precision instrument.

---

## 2. Colors & Surface Logic

### The "No-Line" Rule
Standard 1px borders are strictly prohibited for sectioning. They create visual noise that competes with complex data. Boundaries must be defined solely through background color shifts. For example, a `surface_container_low` section sitting on a `surface` background provides all the separation necessary for the eye.

### Surface Hierarchy & Nesting
We treat the interface as a series of physical, translucent layers.
- **Base Layer:** `background` (#0A0E17). The absolute floor.
- **Sectioning:** Use `surface_container_low` (#0F131D) for large layout areas.
- **Interactive Containers:** Use `surface_container` (#151925) or `surface_container_high` (#1A1F2C) for cards and modules.
- **Floating Elements:** Use `surface_bright` (#262C3A) with 60% opacity and a 20px backdrop blur to create the "Glassmorphism" effect.

### Signature Textures & Gradients
Flatness is the enemy of premium design. 
- **The "Quantum Pulse" Gradient:** Use a linear gradient from `primary` (#69DAFF) to `primary_container` (#00CFFC) at a 135-degree angle for primary action buttons and progress indicators.
- **Success Glow:** For optimization states, use `secondary` (#00FC9A) with a soft outer glow (using a 15% opacity shadow of the same color) to signify a "resolved" quantum state.

---

### 3. Typography: Scientific Clarity
The typography system balances the technical rigor of `JetBrains Mono` (implied for code) with the clean, Swiss-inspired readability of `Inter` and `Space Grotesk`.

| Role | Token | Font | Size | Weight | Character Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | `display-lg` | Space Grotesk | 3.5rem | 500 | -0.02em |
| **Headline** | `headline-md` | Space Grotesk | 1.75rem | 500 | -0.01em |
| **Title** | `title-md` | Inter | 1.125rem | 600 | 0 |
| **Body** | `body-md` | Inter | 0.875rem | 400 | +0.01em |
| **Code** | (Custom) | JetBrains Mono | 0.875rem | 400 | 0 |

**Editorial Note:** Use `display-lg` sparingly for high-impact metrics (e.g., Qubit coherence times). Use `label-sm` in all-caps with 0.1em letter spacing for metadata to evoke a "classified document" aesthetic.

---

## 4. Elevation & Depth

### The Layering Principle
Depth is achieved by "stacking" Tonal Tiers. To lift a component, do not reach for a shadow; reach for a higher surface token.
*   **Step 1:** Base background is `surface_dim`.
*   **Step 2:** Main content area is `surface_container_low`.
*   **Step 3:** Hover states or active cards transition to `surface_container_highest`.

### Ambient Shadows
When an element must float (e.g., a context menu), use a "Quantum Shadow":
*   **Color:** `#000000` at 40% opacity.
*   **Blur:** 40px.
*   **Spread:** -5px.
*   **Offset:** Y: 20px.

### The "Ghost Border" Fallback
If accessibility requires a container definition, use the `outline_variant` token at **15% opacity**. This creates a suggestion of an edge that disappears into the dark background, maintaining the "No-Line" philosophy.

---

## 5. Components

### Buttons (The Action State)
*   **Primary:** Gradient of `primary` to `primary_container`. White text (`on_primary`). Border-radius: `md` (0.375rem).
*   **Secondary:** Ghost style. Transparent background with a `secondary` (#00FC9A) "Ghost Border."
*   **Tertiary:** Text-only using `primary` color, strictly for low-priority utilities.

### High-Contrast Code Blocks
Code blocks should use `surface_container_lowest` (#000000) for the background to provide maximum contrast against the `on_surface` text. Use `secondary` (#00FC9A) for syntax highlighting of successful functions and `error` (#FF716C) for anomalies.

### Data Visualization (Qubit Arrays)
*   **Active State:** `primary` (#69DAFF) with a 4px inner glow.
*   **Inactive State:** `surface_variant` (#202633).
*   **Entangled State:** A subtle CSS animation transition between `primary` and `secondary`.

### Input Fields
Inputs should not be boxes. Use a "Bottom-Line Only" approach or a very subtle `surface_container_high` fill. When focused, the bottom border should expand from the center using the `primary` electric blue.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical layouts. Push a metric to the far right while the label stays far left to create tension.
*   **Do** use `backdrop-filter: blur(12px)` on all modal overlays.
*   **Do** use `secondary_fixed` (#00FC9A) for any data point that represents "Optimization" or "Efficiency."

### Don't:
*   **Don't** use pure white (#FFFFFF) for body text. Use `on_surface_variant` (#A7ABB7) to reduce eye strain in the dark environment.
*   **Don't** use standard 1px dividers. Use a 24px vertical spacer or a subtle shift in surface color instead.
*   **Don't** use rounded corners larger than `xl` (0.75rem). This system is about precision; overly round "bubbly" corners degrade the scientific authority.

### Accessibility Note:
Ensure that all `primary` blue text on `surface` backgrounds maintains a 4.5:1 contrast ratio. If necessary, use `primary_dim` for smaller text elements to ensure legibility without sacrificing the neon aesthetic.
# Code Editor Functional Regressions (Current vs QCanvas-old)

Date: 2026-04-03  
Scope: Code-editor functionality only (no UI styling/visual issues)

## Summary
Compared to `QCanvas-old`, the current app shell has several functional regressions in editor workflows:
- Run/compile/execute/hybrid actions are disconnected from execution logic.
- Project/file data loading from DB is incomplete (projects are never loaded in active screen).
- New file and rename workflows lost key functionality (custom filename and rename path).
- One new-file path bypasses backend persistence.

---

## 1) Run Button Does Nothing in New IDE Shell

### What worked before (QCanvas-old)
- Main app mounted `TopBar`, which contained the actual execution logic:
  - `QCanvas-old/frontend/app/app/page.tsx` imports and renders `TopBar`.
  - `QCanvas-old/frontend/components/TopBar.tsx` handles compile/execute/hybrid logic directly.

### What changed now
- Main app no longer mounts `TopBar`:
  - `frontend/app/app/page.tsx` now renders `IDELayout` + `RunView`.
- `RunView` and `MenuBar` only dispatch a custom event `menu-run`:
  - `frontend/components/ide/RunView.tsx` (Run button dispatches `menu-run`)
  - `frontend/components/ide/MenuBar.tsx` (Run menu action dispatches `menu-run`)
- The only listener for `menu-run` is inside `TopBar`:
  - `frontend/components/TopBar.tsx` (adds event listener in `useEffect`)
- Since `TopBar` is not mounted in current app, no listener exists at runtime.

### Functional impact
- Clicking Run in new IDE does not trigger compile/execute/hybrid pipeline.
- This matches your symptom: run button appears non-functional.

---

## 2) Compile/Execute/Hybrid Pipeline Is Orphaned

### What worked before
- In old app flow, execution mode + run controls were tied to `TopBar`, which emitted expected events (`circuit-compile`, `circuit-execute`, `hybrid-execute`) consumed by results panel.

### What changed now
- Results still listen for these events:
  - `frontend/components/ResultsPane.tsx` listens for `circuit-compile`, `circuit-execute`, `hybrid-execute`.
- Event emitters for those are still in `TopBar` execution handlers.
- But `TopBar` is not used in current `frontend/app/app/page.tsx`.

### Functional impact
- Event-driven execution feedback chain is broken end-to-end.
- Compile/execute/hybrid actions can appear dead even though results panel is mounted.

---

## 3) Projects Are Not Loaded in Active App Screen

### What worked before (QCanvas-old)
- `Sidebar` was mounted by app page.
- `Sidebar` `useEffect` loaded projects and scope files:
  - `QCanvas-old/frontend/components/Sidebar.tsx` calls `fetchProjects(token)` and initial file fetch.

### What changed now
- Current app page does not mount `Sidebar`.
- Current mounted IDE components (`ExplorerView`, `MenuBar`, `RunView`) do not call `fetchProjects`.
- Search in current active screen flow shows `fetchProjects(...)` usage only inside unmounted `frontend/components/Sidebar.tsx`.

### Functional impact
- Project list/state is never initialized in current editor route.
- Database project/file navigation behavior is degraded (only generic/root file loading path runs via `fetchFiles()` in `frontend/app/app/page.tsx`).
- This aligns with your symptom that DB project/file data is not fetched correctly.

---

## 4) Cannot Create New File With Custom Name in New IDE Flow

### What worked before
- Old sidebar had explicit new-file input and confirmation flow (user-provided filename).

### What changed now
- `ExplorerView` New File button hardcodes filename to `new.py`:
  - `frontend/components/ide/ExplorerView.tsx`
- `MenuBar` New File action also hardcodes `new.py`:
  - `frontend/components/ide/MenuBar.tsx`

### Functional impact
- No active path in new IDE to create file with user-chosen name at creation time.
- This directly matches your symptom.

---

## 5) Rename File Functionality Is Missing in Mounted IDE Components

### What worked before
- Old sidebar had rename flow (`startRename`, input editing, `renameFile(...)`).

### What changed now
- `renameFile` still exists in store (`frontend/lib/store.ts`) but is not wired in mounted IDE components.
- In `frontend/components/ide/**`, there is no rename action path.

### Functional impact
- Users cannot rename files from current mounted editor flow.
- This directly matches your symptom.

---

## 6) One New-File Path Is Local-Only (Not Persisted to DB)

### What changed now
- `MenuBar` New File uses `addFile('new.py', '')` (local state only):
  - `frontend/components/ide/MenuBar.tsx`
- This bypasses backend create API used by `createFile(...)`.

### Functional impact
- Files created from that menu path may not exist in DB until separately saved/persisted.
- Can cause mismatch between editor state and DB-fetched state after reload.

---

## High-Confidence Root Cause Cluster
- Major refactor replaced `TopBar + Sidebar` shell with `IDELayout + MenuBar + ExplorerView + RunView`.
- Core functional handlers were not fully migrated from old mounted components to new mounted components.
- Result: behavior regressions in execution, project loading, file creation naming, and file renaming.

---

## Not Included (By Request)
- No visual/layout/theme/UI styling issues included.
- Only editor functionality regressions are reported.

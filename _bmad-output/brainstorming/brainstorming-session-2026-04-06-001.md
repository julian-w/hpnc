---
stepsCompleted: [1, 2, 3]
inputDocuments: [hpnc-konzept.md]
session_topic: 'HPNC — offene Architekturentscheidungen, blinde Flecken und Dispatcher-Design'
session_goals: 'Offene Entscheidungen aus §19 systematisch durcharbeiten, Risiken und blinde Flecken aufdecken, Dispatcher-Architektur fundamental klären'
selected_approach: 'ai-recommended'
techniques_used: ['Morphological Analysis', 'Chaos Engineering', 'Reverse Brainstorming', 'First Principles Thinking', 'Assumption Reversal']
ideas_generated: [35]
context_file: ''
technique_execution_complete: true
output_document: '_bmad-output/hpnc-konzept-v2.md'
---

# Brainstorming Session Results

**Facilitator:** Julian
**Date:** 2026-04-06

## Session Overview

**Topic:** HPNC (Human-Planned Night Crew) — lokale Orchestrierungsarchitektur für autonome Nacht-Implementierung mit AI-Agenten
**Goals:** Offene praktische Entscheidungen durcharbeiten, blinde Flecken aufdecken, Dispatcher-Architektur fundamental klären

### Session Setup

Drei-Runden-Ansatz mit steigender Tiefe:
- Runde 1: Morphological Analysis auf §19-Entscheidungen
- Runde 2: Chaos Engineering + Reverse Brainstorming für Risiken
- Runde 3: First Principles + Assumption Reversal für Dispatcher

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** HPNC Architekturentscheidungen mit Fokus auf praktische Umsetzbarkeit

**Recommended Techniques:**

- **Morphological Analysis:** Systematische Exploration aller Parameter-Kombinationen für die 8 offenen Entscheidungen aus §19
- **Chaos Engineering + Reverse Brainstorming:** Destruktiv-kreative Analyse — wie kann HPNC nachts scheitern?
- **First Principles + Assumption Reversal:** Fundamentale Klärung der Dispatcher-Architektur

**AI Rationale:** HPNC ist ein Multi-Parameter-Systementwurf mit klarer Struktur aber offenen Stellschrauben. Morphological Analysis passt ideal für systematische Optionsexploration. Die destruktiven Techniken decken auf, was positive Planung übersieht. First Principles verhindert, dass Framework-Annahmen die Architektur unnötig einengen.

---

## Technique Execution Results

### Runde 1: Morphological Analysis — §19 Entscheidungen

**8 Parameter systematisch durchgearbeitet, alle Entscheidungen getroffen:**

| # | Parameter | Entscheidung |
|---|-----------|-------------|
| 1 | Story-Format | BMAD-Artefakt: Frontmatter (Steuerung) + Body (Kontext). Builder als Modul. |
| 2 | Artefakte einlesen | Zwei-Schicht: Frontmatter = "darf", Queue = "soll heute". Dispatcher prüft beides. |
| 3 | Dispatcher-Basis | Eigenes Script mit State-Machine. Sprache offen. Kein UI initial. |
| 4 | Token-/Kosten | Pro Task `cost.json` via CLI-Output-Parsing. |
| 5 | Review-Speicherung | `review.md` mit Frontmatter + Body im Run-Ordner. Wird committet. |
| 6 | Morgenbericht | Markdown-Report (committet) + CLI-Kommando. Nummeriert. |
| 7 | Timeout/Retry | Story-Timeout + Watchdog. 1x technischer Retry. Modellwechsel = Warnsignal. |
| 8 | Parallelisierung | Start sequentiell. Ziel: konfigurierbar + modellbasiert parallel. |

**Zusätzliche Entscheidungen aus der Diskussion:**
- Run-Ordner nach `Jahr/Monat/Tag/Sequenz_Taskname` strukturiert
- `run.yaml` enthält `files_changed` und `story_source` für bidirektionale Navigation
- Run-Artefakte werden committet und nach `main` gemergt (für immer nachvollziehbar)
- Reports nummeriert (nicht an "morgens" gebunden, mehrfache Läufe pro Tag möglich)

### Runde 2: Chaos Engineering + Reverse Brainstorming — Blind Spots

**14 Szenarien durchgespielt, Absicherungen definiert:**

| # | Blind Spot | MVP? | Absicherung |
|---|-----------|------|-------------|
| 1 | Scope-Gate (Diff-Größe) | Später | Cross-Review reicht für MVP |
| 2 | `touches` + sequentielle Erzwingung | Konzept ja | `files` + `resources` Kategorien |
| 3 | Loop-Erkennung | Timeout ja | Token-Budget + Commit-Watchdog später |
| 4 | API/Abo-Limit-Erkennung | MVP | Pausieren, warten, fortsetzen |
| 5 | Test-Qualität vs. Test-Existenz | Phase 3 | Detail-Grad klären |
| 6 | Dispatcher-Crash-Recovery | MVP | State-Persistenz + Startup-Recovery |
| 7 | Secret-Schutz | MVP | Pre-Commit Hook (git-secrets/gitleaks) |
| 8 | Cross-Platform (Win/Linux/Mac) | Phase 3 | Checkliste: longpaths, gitattributes, Pfade |
| 9 | Story-Validierung / Dry-Run | MVP | `hpnc validate` + Laufzeit-Gate |
| 10 | Hartnäckiger Fix-Loop | MVP | 3 Versuche, Rollentausch nach 2, konfigurierbar |
| 11 | Task-Abhängigkeiten | MVP | `depends_on` + Queue-Reihenfolge |
| 12 | Protected Paths | MVP | Instruktion + Post-Run-Check |
| 13 | Testumgebung Dispatcher-gesteuert | MVP | `hpnc validate` prüft Services + Ports |
| 14 | `touches` files + resources | Konzept | Known Resources in Config, Validate warnt bei unbekannten |

### Runde 3: First Principles + Assumption Reversal — Dispatcher-Architektur

**7 Annahmen hinterfragt, fundamentale Architekturentscheidungen:**

| # | Annahme | Entscheidung |
|---|---------|-------------|
| 1 | "Läuft einmal pro Nacht" | Nacht-Modus bleibt Ziel. Token-Budget tagsüber für Planung. |
| 2 | "Ein Task = eine Story" | 1:1 bleibt. Aber `task_groups` mit `release_policy` (`all_ready` / `independent`). |
| 3 | "Executor braucht aufbereiteten Prompt" | Nein — BMAD-Pattern: Story + Config + System-Instruktionen als Dateien. |
| 4 | "Task-Runner muss BMAD-Workflow sein" | Eigener Code, BMAD-Patterns übernommen (Steps, State, Config). |
| 5 | "Immer über CLI" | Agent-Aufruf hinter AgentExecutor-Abstraktion. Dünn im MVP. |
| 6 | "Review immer opposite" | Reviewer-Pool, konfigurierbar (`opposite/codex/opus/skip`). |
| 7 | "Morgenbericht ist passiv" | CLI-gestützt: `status/show/diff`. Ziel: `hpnc resume`. |

**Kernentscheidung:** Dispatcher + Task-Runner getrennt (Ansatz B). Dispatcher = Scheduler (dumm, stabil). Task-Runner = Lifecycle-Manager (State-Machine, Fix-Loop, Gates).

### Bonus-Runde: Erweiterungen

| # | Thema | Entscheidung |
|---|-------|-------------|
| 1 | CLI-Interface | Komplett definiert: morgens/tagsüber/abends Workflows |
| 2 | BMAD-Integration | Story-Fertigstellung → Queue. Validate als BMAD-Skill. |
| 3 | Auto-Merge | Kontrolliert via `merge_policy` + `merge_target`. Default nie `main`. |
| 4 | HPNC zwei Schichten | Zentrales Tool + Projekt-Config in `_hpnc/`. Wie BMAD selbst. |
| 5 | Scope-Erkennung | Executor-Instruktion: bei Überschreitung → `blocked` melden |
| 6 | Notifications | MVP: `hpnc status`. Später: Desktop/E-Mail/Push. |
| 7 | Logging | Konfigurierbar: normal + truncated Agent-Output (500 Zeilen). |

---

## Output

Alle Entscheidungen eingearbeitet in: **`_bmad-output/hpnc-konzept-v2.md`**

### Creative Facilitation Narrative

Session begann mit systematischer Parameter-Analyse (Morphological Analysis) für die 8 offenen Entscheidungen. Julian zeigte dabei starkes architektonisches Gespür — besonders die Idee des Zwei-Schicht-Freigabemodells (Frontmatter = "darf", Queue = "soll") kam aus seiner Frage nach aktiver Steuerungskontrolle.

Die Chaos-Engineering-Runde deckte 14 blinde Flecken auf, von denen mehrere MVP-relevant sind (Crash-Recovery, API-Limits, Secret-Schutz). Julian's Beitrag zur API-Limit-Erkennung (Pausieren statt Abbrechen) und zum touches-System (files + abstrakte resources) waren entscheidende Verfeinerungen.

In der First-Principles-Runde fiel die wichtigste Architekturentscheidung: Dispatcher + Task-Runner getrennt (Ansatz B). Julian's Frage nach der State-Machine führte direkt zur Erkenntnis, dass die Lifecycle-Logik nicht im Dispatcher leben sollte.

Die Bonus-Runde ergänzte CLI-Design, BMAD-Integration, Auto-Merge-Kontrolle und die Zwei-Schichten-Architektur (zentrales Tool + Projekt-Config).

# HPNC — Human-Planned Night Crew

*Humans plan by day. Agents implement by night.*

**Kurze Beschreibung:** HPNC ist eine lokal laufende Orchestrierungs- und Ausführungsarchitektur für vorbereitete Software-Tasks. Menschen strukturieren und klären die Arbeit tagsüber mit BMAD; nachts übernimmt eine Crew aus AI-Agenten die autonome Implementierung, Reviews und Qualitätsgates in isolierten Worktrees.

> Zweck dieses Dokuments: Diese Datei dient als dauerhafte Grundlage für neue Sessions mit **Claude Code / Opus** und **Codex**. Sie fasst Entscheidungen, Gründe, Rollen, Tooling, Night-Policy und den geplanten Umsetzungsweg zusammen.
>
> Dieses Dokument ist bewusst so geschrieben, dass ein Agent in einer neuen Session schnell den Projektkontext verstehen und konsistent weiterarbeiten kann.
>
> **Version 2** — aktualisiert nach Brainstorming-Session vom 2026-04-06. Alle offenen Entscheidungen aus v1 §19 sind getroffen. Zusätzliche Architekturentscheidungen aus Blind-Spot-Analyse und First-Principles-Review eingearbeitet.

---

## 0. Projektidentität

**Projektname:** HPNC
**Langform:** Human-Planned Night Crew
**Claim:** *Humans plan by day. Agents implement by night.*

**Wofür der Name steht:** Der menschliche Teil liegt in der tagsüber geplanten, geklärten und strukturierten Vorbereitung. Die nächtliche Crew aus Agenten übernimmt danach die autonome Umsetzung innerhalb klarer Regeln, Reviews und Qualitätsgates.

**Abgrenzung:** BMAD bleibt der Planungs- und Strukturrahmen. HPNC ist die darauf aufbauende Orchestrierungs- und Nacht-Ausführungsschicht.

---

## 1. Zielbild

Es soll mit **HPNC** ein **lokal auf dem eigenen PC laufendes System** entstehen, das nachts **autonom an klar definierten Software-Tasks** arbeitet.

Wichtige Randbedingungen:

- **BMAD bleibt zentraler Planungs- und Strukturkern**.
- Es werden **keine lokalen LLMs** eingesetzt.
- Als Modelle/Agenten werden nur verwendet:
  - **Opus** (über Claude Code)
  - **Codex**
  - Architektur ist offen für zukünftige Agenten
- Das System soll **lokal gesteuert** werden, also auf dem eigenen Rechner laufen.
- Die Software ist oft **groß und komplex**, deshalb ist strukturierte Planung und Zerlegung wichtig.
- Nightly-Arbeit darf nur auf Tasks erfolgen, die **vollständig geklärt** sind und **keine Interaktion mit dem Menschen** benötigen.
- **Tests sind Pflicht**. Tests müssen vorab in der Story definiert/geplant sein.
- Bei UI-Aufgaben müssen zusätzlich die lokal definierten UI-Qualitätswerkzeuge verwendet werden.

Das System soll morgens nicht „irgendetwas gemacht haben", sondern klar nachvollziehbare Ergebnisse liefern:

- Branch / Worktree mit Änderungen
- Teststatus
- Reviewstatus
- Zusammenfassung
- offene Fragen oder Blocker

---

## 2. Zentrale Architekturentscheidung

### Entscheidung

Die Zielarchitektur basiert auf:

- **BMAD** als Denk-, Planungs- und Strukturrahmen
- **Claude Code / Opus** als Lead-Agent für komplexe Planung, komplexe Umsetzung und Reviews
- **Codex** als fokussierter Implementierungs-Agent für klar geschnittene Tasks
- **lokaler UI-Qualitätssicherung** mit Storybook, Storybook-Tests und Playwright
- einem **lokalen Night Dispatcher + Task-Runner**, der nachts freigegebene Tasks ausführt

### Begründung

- **BMAD** ist wichtig, weil die Software groß und komplex ist und von sauberer Zerlegung profitiert.
- **Opus** ist besser für komplexe, planungsnahe und systemübergreifende Aufgaben.
- **Codex** ist oft besser für konkrete, klar umrissene Implementierungsschritte.
- **Cross-Review durch das jeweils andere Modell** erhöht die Robustheit.
- Eine **lokale-only Architektur** ist gewünscht; deshalb scheiden Cloud-zentrierte Qualitätstools wie Chromatic aus.
- Nightly-Automation muss **planbar, nachvollziehbar und deterministisch** sein, nicht frei improvisierend.

---

## 3. Dinge, die bewusst **nicht** Teil der Kernarchitektur sind

### 3.1 Chromatic

**Entscheidung:** Nicht verwenden.

**Grund:** Chromatic ist cloud-basiert. Die Zielarchitektur soll lokal auf dem eigenen PC laufen.

**Ersatz:**

- Storybook lokal
- Storybook Test Runner lokal
- Playwright lokal
- lokale Screenshot-/Visual-Regression-Tests

### 3.2 bmalph als Zentrale

**Entscheidung:** Nicht als Kern des Systems verwenden.

**Grund:** bmalph ist als Bundle interessant, wirkt aber für die angestrebte Architektur zu eng gekoppelt. Gewünscht ist eine flexiblere Architektur mit BMAD als festem Kern und frei kombinierbaren lokalen Agenten-Executors.

### 3.3 Lokale Modelle

**Entscheidung:** Nicht verwenden.

**Grund:** Es sollen ausschließlich **Opus** und **Codex** verwendet werden. Architektur erlaubt spätere Ergänzung weiterer Agenten.

---

## 4. Modellrollen und Verantwortlichkeiten

### 4.1 Opus / Claude Code

**Rolle:** Lead-Agent für Komplexität, Planung und Review.

**Zuständig für:**

- komplexe oder große Tasks
- Planung und Zerlegung
- systemübergreifende Änderungen
- Refactorings mit größerem Scope
- schwierige Bugs und Debugging
- Reviews von Codex-Ergebnissen
- Abschlussbewertung eines Laufs

### 4.2 Codex

**Rolle:** fokussierter Implementierungs-Agent.

**Zuständig für:**

- klar definierte Implementierungsaufgaben
- kleinere bis mittlere Features
- kleinere Refactorings
- Tests ergänzen oder reparieren
- Storybook-/Playwright-bezogene konkrete Umsetzungen
- Routineaufgaben

### 4.3 Reviewer-Pool

**Regel:** Der Reviewer wird aus den verfügbaren Modellen gewählt. Hauptregel: **nicht der eigene Executor**.

Konfigurierbar pro Story:

- `opposite` — das jeweils andere Modell (Default)
- `codex` — explizit Codex
- `opus` — explizit Opus
- `skip` — kein Review (nur für triviale Tasks wie Dependency-Updates)

**Warum Pool statt hartes "opposite":**

- zukunftssicher für neue Agenten
- erlaubt `skip` für triviale Tasks (Token-Einsparung)
- bei zwei Modellen identisch mit "opposite"

### 4.4 Agent-Abstraktion

Alle Agent-Aufrufe laufen über eine **AgentExecutor-Abstraktion**. Nicht direkt CLI-Aufrufe im Code, sondern:

```
TaskRunner
  → AgentExecutor (Interface)
      → ClaudeCodeExecutor (CLI)
      → CodexExecutor (CLI)
      → ZukünftigerAgentExecutor (API/SDK/...)
```

**MVP:** Dünne Abstraktion, je ein Executor für Claude Code und Codex.
**Später:** Erweiterbar für neue Agenten, SDKs, APIs.

---

## 5. Night-Policy

### 5.1 Was nachts laufen darf

Es dürfen nur Tasks laufen, bei denen:

- keine Interaktion mit dem Menschen nötig ist
- fachlich alles geklärt ist
- Akzeptanzkriterien klar sind
- Tests vorher schriftlich festgehalten/geplant sind
- die Aufgabe für Nachtbetrieb freigegeben wurde

### 5.2 Was **nicht** nachts laufen darf

- Tasks mit offenen fachlichen Fragen
- Änderungen, bei denen menschliche Entscheidungen nötig sind
- Tasks ohne definierte Tests
- UI-Tasks ohne definierte UI-Prüfkriterien
- riskante Themen ohne klaren Rahmen

### 5.3 Ergebnisarten

#### `done`

- alle Gates grün
- Review durch Gegenmodell grün
- keine offenen Fragen
- Ergebnis ist merge-bereit

#### `proposal`

- technisch vorbereitet
- aber noch menschlicher Input oder Freigabe nötig
- nicht als fertig behandeln

#### `blocked`

- Agent konnte ohne menschliche Entscheidung nicht sinnvoll weiterarbeiten
- keine stillschweigende Spekulation
- auch bei Scope-Erkennung: Aufgabe deutlich größer als Story → `blocked` mit Aufteilungsempfehlung

#### `failed`

- Build kaputt
- Tests/Gates kaputt
- Task entgleist
- Agent festgelaufen

#### `interrupted`

- Dispatcher oder Agent-Prozess unerwartet abgebrochen
- Strom weg, Windows-Update, Crash
- Mensch entscheidet morgens ob Neustart

#### `merged`

- Task erfolgreich in Ziel-Branch gemergt
- Worktree aufgeräumt

### 5.4 Zusatzregel

Ein Nachttask darf nur laufen, wenn in **einem klaren Satz** beschrieben werden kann, was „fertig" bedeutet.

**Gut:**

> Das Formular speichert erfolgreich, zeigt Validierungsfehler korrekt und besitzt Storybook- sowie Playwright-Tests.

**Schlecht:**

> Mach die UI besser.

---

## 6. Story-Format und `night-ready`-Schema

### 6.1 Format-Entscheidung

Stories nutzen das **BMAD-Artefakt-Format**: YAML-Frontmatter (Steuerung) + Markdown-Body (Kontext).

**Rollenaufteilung:**

- **Frontmatter** → Dispatcher/Task-Runner liest: *"Darf das laufen? Wer macht's? Welche Gates?"*
- **Body** → Executor liest: *"Was genau soll ich tun und warum?"*

Der BMad Builder kann das als **BMAD-Modul** standardisieren (Templates, Validierung, Workflow-Integration).

### 6.2 Story-Beispiel

```yaml
---
title: "Login-Formular Validierungsfehler anzeigen"
epic: auth
status: night-ready

# === HPNC Night-Ready Block ===
night_ready: true
executor: codex
reviewer: opposite
risk: low
ui_impact: component
db_impact: none
merge_policy: done
merge_target: develop
human_input_needed: false
timeout: 30m
acceptance_criteria:
  - Validierungsfehler werden inline unter dem Feld angezeigt
  - Fehlermeldungen verschwinden nach Korrektur
  - Storybook-Story zeigt alle Fehlerzustände
tests_required:
  - unit: Validierungslogik
  - storybook: Error-States Story
  - playwright: Login-Flow mit ungültigen Eingaben
  - a11y: Fehlermeldungen sind screen-reader-lesbar
blocking_questions: []
touches:
  files:
    - src/components/LoginForm.tsx
    - src/components/LoginForm.test.tsx
  resources:
    - auth
---

## Kontext

Das Login-Formular zeigt aktuell keine Validierungsfehler an. Benutzer sehen
nur einen generischen Fehler nach dem Absenden.

## Akzeptanzkriterien

- Validierungsfehler werden inline unter dem jeweiligen Feld angezeigt
- Fehlermeldungen verschwinden nach Korrektur der Eingabe
- Storybook-Story zeigt alle Fehlerzustände (leer, zu kurz, ungültig)

## Technische Hinweise

- Bestehende Form-Bibliothek unter `src/lib/forms/` nutzen
- Validierungsregeln in `src/validation/auth.ts` definiert
```

### 6.3 Pflichtfelder für `night-ready`

- `night_ready`: explizite Freigabe für Nachtlauf
- `executor`: `opus`, `codex` oder `auto`
- `reviewer`: `opposite`, `opus`, `codex` oder `skip`
- `risk`: mindestens Klassifizierung des Risikos
- `ui_impact`: `none`, `component`, `page`
- `db_impact`: `none`, `safe`, `review`
- `merge_policy`: `done`, `proposal`, `branch-only`
- `merge_target`: Ziel-Branch (optional, sonst Projekt-Default)
- `human_input_needed`: muss für Nachtlauf `false` sein
- `acceptance_criteria`: fachlich und technisch klar
- `tests_required`: schriftlich vorab definiert/geplant
- `blocking_questions`: muss leer sein
- `touches`: Dateien und abstrakte Ressourcen die berührt werden

### 6.4 `touches`-System

Zweck: Überschneidungserkennung bei parallelen Tasks.

```yaml
touches:
  files:
    - src/components/LoginForm.tsx      # Konkrete Dateien
    - src/api/auth/                     # Oder Ordner
  resources:
    - db-migrations                     # Abstrakte Ressourcen
    - api-definitions
    - auth
```

- **Überschätzend ausfüllen:** "wird angefasst" + "wird vermutlich angefasst"
- Bekannte Ressourcen werden in `_hpnc/config.yaml` definiert
- `hpnc validate` warnt bei unbekannten Ressourcen (Tippfehler-Schutz)
- Bei Überschneidung: Dispatcher erzwingt sequentielle Ausführung

---

## 7. Zwei-Schicht-Freigabemodell

### 7.1 Schicht 1: Frontmatter — "Darf laufen" (Qualitätsfreigabe)

Das `night_ready: true` im Story-Frontmatter bestätigt: Diese Story ist fachlich geklärt, Tests definiert, keine offenen Fragen.

### 7.2 Schicht 2: Queue — "Soll heute laufen" (Scheduling)

Die `night-queue.yaml` bestimmt: Welche der freigegebenen Stories laufen **heute Nacht**.

```yaml
# _hpnc/night-queue.yaml
date: 2026-04-06

task_groups:
  - name: user-profile-epic
    release_policy: all_ready
    tasks:
      - story: stories/user-profile-api.md
        priority: 1
      - story: stories/user-profile-form.md
        priority: 2
        depends_on: [user-profile-api]
      - story: stories/user-profile-e2e.md
        priority: 3
        depends_on: [user-profile-api, user-profile-form]

  - story: stories/fix-button-color.md
    priority: 4
```

### 7.3 Dispatcher prüft beides

- Story steht in Queue **UND** hat `night_ready: true` → läuft
- Story steht in Queue aber ist **nicht** `night_ready` → Warnung, wird übersprungen
- Story ist `night_ready` aber **nicht** in Queue → läuft nicht (bewusste Selektion)

### 7.4 Task-Groups und `release_policy`

| Policy | Beschreibung |
|--------|-------------|
| `all_ready` | Gruppe startet nur wenn alle Stories `night_ready` sind |
| `independent` | Jede Story startet sobald ihre `depends_on` erfüllt sind |

### 7.5 Task-Abhängigkeiten

- `depends_on` deklariert: "Dieser Task braucht Task X zuerst"
- Queue-Reihenfolge (priority) ist der schnelle Hebel
- `depends_on` verhindert Fehler bei falscher Sortierung
- Bei Parallelisierung: Dispatcher startet abhängige Tasks erst wenn Dependency `done` ist
- Dependency `failed`/`blocked` → abhängiger Task wird `blocked` mit Verweis

### 7.6 Queue-Management

Zwei gleichberechtigte Wege:

- **BMAD-Integration:** Story-Fertigstellung kann direkt in Queue münden. BMAD-Skill fragt "Night-ready? In die Queue schieben?"
- **CLI:** `hpnc queue add/remove/reorder`
- **Manuell:** `night-queue.yaml` direkt editieren

Queue wird nach Abschluss automatisch aufgeräumt (done-Tasks entfernt).

---

## 8. Routing-Regeln: Wann Opus, wann Codex?

### Codex bekommt den Task, wenn

- der Task klar geschnitten ist
- der Scope lokal und konkret ist
- die Änderungen überschaubar sind
- Tests eindeutig sind
- keine größere Architekturentscheidung nötig ist

### Opus bekommt den Task, wenn

- der Task komplex ist
- mehrere Bereiche betroffen sind
- Planung/Zerlegung nötig ist
- Refactoring oder Architekturthema im Spiel ist
- die Aufgabe systemübergreifend ist
- ein schwieriger Fehler untersucht werden muss

### Empfohlener Mischmodus

- **Opus plant**
- **Codex implementiert**
- **Opus reviewed**

---

## 9. Qualitätsgates

### 9.1 Gates für **alle** Tasks

- Build erfolgreich
- relevante Tests grün
- Lint/Format grün
- Review durch Reviewer-Pool erfolgt
- Secret-Scan grün (Pre-Commit Hook)
- Protected Paths nicht verändert

### 9.2 Zusätzliche Gates für **UI-Tasks**

Pflichtwerkzeuge:

- Storybook
- Storybook Test Runner
- lokale Accessibility-Prüfungen
- Playwright

Pflichtkriterien:

- passende Storybook-Stories vorhanden oder angepasst
- Storybook-Tests grün
- A11y-Checks grün
- Playwright grün
- visuelle Änderungen dokumentiert und nachvollziehbar

### 9.3 Zusätzliche Gates für **DB-bezogene Tasks**

- reproduzierbare Reinitialisierung / Reset
- Setup/Migrations-Tests grün
- keine unkontrollierten destruktiven Änderungen
- nur `safe`-klassifizierte DB-Tickets nachts
- Konflikt-Vermeidung über `touches.resources: db-migrations`

---

## 10. Lokaler UI-Workflow

### 10.1 Storybook

**Rolle:** Lokale UI-Werkstatt für isolierte Komponenten- und Zustandsdarstellung.

### 10.2 Storybook Test Runner

**Rolle:** Lokale automatisierte Prüfung von Storybook-Stories.

### 10.3 Lokale A11y-Checks

**Rolle:** Frühe Accessibility-Basissicherung auf Story- und Seiten-Ebene.

### 10.4 Playwright

**Rolle:** End-to-End- und Layout-/Visual-Qualitätssicherung.

### 10.5 Konsequenz für UI-Tickets

UI-Tickets dürfen nachts nur laufen, wenn:

- die Stories definiert sind oder mit dem Ticket zusammen definiert werden können
- die UI-Tests schriftlich festgelegt sind
- klar ist, woran „fertig" erkannt wird

---

## 11. Kernarchitektur: Dispatcher + Task-Runner

### 11.1 Architektur-Entscheidung: Trennung Dispatcher / Task-Runner

**Entscheidung:** Ansatz B — Dispatcher ist Scheduler, Task-Runner steuert den Lifecycle.

| Komponente | Verantwortung |
|-----------|---------------|
| **Dispatcher** | Queue einlesen, Tasks validieren, Task-Runner starten, auf Ergebnis warten, Report erstellen |
| **Task-Runner** | State-Machine pro Task: Worktree → Implementierung → Review → Fix-Loop → Gates → Status |

**Warum diese Trennung:**

- Dispatcher bleibt dumm und stabil
- Task-Runner ist pro Task isoliert
- Parallelisierung wird trivial (mehrere Task-Runner starten)
- Crash-Recovery einfacher (jeder schreibt seinen eigenen State)
- Neue Task-Typen brauchen keine Dispatcher-Änderung

### 11.2 Dispatcher — Aufgaben

1. `night-queue.yaml` einlesen
2. Für jeden Task: Story-Frontmatter prüfen (`night_ready: true`, Pflichtfelder)
3. `depends_on` und `release_policy` auswerten
4. Task-Runner starten
5. Auf Ergebnis warten
6. Dispatcher-State persistieren nach jedem Schritt
7. Worktrees aufräumen (done-Tasks)
8. Queue aufräumen (done-Tasks entfernen)
9. Report erstellen

### 11.3 Task-Runner — State-Machine

```
queued
  → setup_worktree
  → implementation (Executor)
  → review (Reviewer)
      → review_pass → gates
      → review_fail → fix_attempt
          → fix_attempt (max 3, Rollentausch nach 2)
          → review
          → nach max_fix_attempts → blocked
  → gates
      → gates_pass → done
      → gates_fail → failed
  → timeout → interrupted
  → api_limit → paused → resume
```

### 11.4 Hartnäckiger Fix-Loop mit Rollentausch

Der Task-Runner gibt nicht beim ersten Review-Fail auf:

```
Implementierung (Codex)
    → Review (Opus) → fail
    → Fix-Versuch 1 (Codex)
    → Review (Opus) → fail
    → Fix-Versuch 2 (Opus)        ← Rollentausch
    → Review (Codex)
    → immer noch fail → blocked
```

**Default-Parameter:**

| Parameter | Default | Konfigurierbar |
|-----------|---------|---------------|
| `max_fix_attempts` | 3 | Ja, pro Story |
| `swap_executor_after` | 2 | Nach X Versuchen wechselt der Executor |
| `max_review_rounds` | 4 | Gesamte Review-Zyklen inkl. Initial |

Jede Runde wird in `run.yaml` dokumentiert. Bei Rollentausch: prominent im Report als Warnsignal.

### 11.5 Kontext-Übergabe an Agenten

**BMAD-Pattern übernommen:** Kein aufbereiteter Prompt. Story-Datei + Config + System-Instruktionen als separate Dateien übergeben.

```
Task-Runner übergibt:
  1. Story-Datei (komplett, Frontmatter + Body)
  2. Projekt-Config (_hpnc/config.yaml + _bmad/config)
  3. System-Instruktionen (_hpnc/executor-instructions.md)
  4. Optional: zusätzliche Context-Files aus der Story
```

### 11.6 Executor-Instruktionen

Feste Datei pro Projekt:

```markdown
# _hpnc/executor-instructions.md

## Regeln
- Ändere NUR Dateien die zum Task gehören
- Fasse NIEMALS an: _hpnc/, _bmad/, .claude/
- Committe nach jedem logischen Schritt
- Schreibe Tests gemäß tests_required
- Bei Unklarheiten: STOPP, nicht raten
- Wenn die Aufgabe deutlich größer ist als die Story beschreibt:
  STOPP, melde blocked mit Einschätzung zur Aufteilung
```

### 11.7 Task-Runner — eigener Code mit BMAD-Patterns

**Entscheidung:** Task-Runner ist eigener Code (Sprache noch offen), übernimmt BMAD-Patterns:

- Step-basierter Aufbau
- Frontmatter-State-Tracking
- Config-Loading

Kein BMAD-Workflow, weil Prozess-Steuerung (CLI aufrufen, Prozesse warten, Exit-Codes) und spätere Parallelisierung zu komplex für einen reinen BMAD-Skill.

---

## 12. Timeout, Retry und Limits

### 12.1 Timeout

- **Story-Feld `timeout`** mit konfigurierbarem Default (z.B. 30min)
- **Aktivitäts-Watchdog** als Sicherheitsnetz: wenn kein Output mehr → Abbruch
- Timeout greift über den gesamten Fix-Loop

### 12.2 Retry

- **Ein technischer Retry** bei API-Fehlern, Rate-Limits, Timeouts
- **Nicht** bei inhaltlichem Scheitern
- Bei Executor-Wechsel durch Retry: prominent im Report als Warnsignal

### 12.3 API/Abo-Limit-Erkennung

- Wenn Limit erreicht: alle laufenden Tasks **pausieren** (nicht abbrechen)
- Warten bis Limit reset
- Dann fortsetzen
- Im Report dokumentieren: "Task X pausiert von 03:12 bis 04:00 wegen Rate-Limit"

### 12.4 Ausbaustufen (nicht MVP)

- Token-Budget pro Task
- Commit-Watchdog (kein Commit nach X Minuten → vermutlich Loop)
- Test-Retry-Limit (max 3 Versuche einen Test grün zu bekommen)

---

## 13. Crash-Recovery und State-Persistenz

### 13.1 `run.yaml` — sofort schreiben

Status wird bei **jedem Statuswechsel** sofort auf Disk geschrieben, nicht erst am Ende.

### 13.2 `dispatcher-state.yaml` — Gesamtzustand

```yaml
# _hpnc/dispatcher-state.yaml
run_date: 2026-04-06
started: 2026-04-06T01:00:00
queue_file: night-queue.yaml
current_task: 2
tasks:
  - story: login-validation
    status: done
  - story: button-states
    status: running
    phase: implementation
    started: 2026-04-06T01:32:00
  - story: user-profile-api
    status: queued
```

### 13.3 Startup-Recovery

Beim nächsten Start prüft der Dispatcher:

- Runs mit Status `running` → markiert als `interrupted`
- Queue-Fortschritt beibehalten → nicht von vorne anfangen
- Agent-Kontext ist nicht wiederherstellbar → Mensch entscheidet morgens ob Neustart

---

## 14. Lokale Ausführung und Infrastruktur

### 14.1 Grundsatz

Das System läuft **lokal auf dem PC** — keine lokalen LLMs, aber lokale Steuerung, Worktrees, Tests, Logs, Reports und Orchestrierung.

### 14.2 Worktrees / Branch-Isolation

Jeder Night-Task läuft in einem **eigenen Git-Worktree** mit eigenem Branch.

- Schutz des Hauptbranches
- saubere Isolation paralleler Tasks
- bessere Nachvollziehbarkeit
- einfacher Rückbau bei Fehlern
- Worktree wird nach Task-Abschluss aufgeräumt (alles ist in Git)

### 14.3 Kein Direktzugriff auf produktive Branches

- niemals direkt auf `main` (außer explizit als `merge_target` konfiguriert)
- Default `merge_target` wird pro Projekt konfiguriert (z.B. `develop`)
- Nightly-Arbeit endet in Branches, Merge ist kontrolliert

### 14.4 Auto-Merge

| `merge_policy` | Verhalten |
|----------------|-----------|
| `done` | Automatisch in `merge_target` mergen wenn alle Gates grün |
| `proposal` | Branch bleibt stehen, Mensch entscheidet morgens |
| `branch-only` | Kein Merge, nur Branch + Report |

### 14.5 Testumgebung — Dispatcher-gesteuert

- Dispatcher startet/stoppt benötigte Services (Dev-Server, DB) pro Task
- Bei Parallelisierung: Port-Zuweisung pro Worktree
- `hpnc validate` prüft vor dem Start ob alle Services startbar sind

### 14.6 Cross-Platform

HPNC soll auf **Windows und Linux** laufen. Mac perspektivisch.

Checkliste für Phase 3:

- Git `core.longpaths = true`
- `.gitattributes` sauber definieren
- Plattformunabhängige Pfadbehandlung
- Dateisperren-Handling (relevant bei Parallelisierung)
- Sleep/Hibernate-Erkennung (Zeitsprünge)
- Task-Namen kurz halten (Pfadlängen)

### 14.7 Secret-Schutz

- **MVP:** Pre-Commit Hook (git-secrets / gitleaks)
- **Später:** Zusätzlicher Gate-Check durch Dispatcher nach Agent-Lauf

### 14.8 Protected Paths

Agenten dürfen bestimmte Pfade nicht ändern:

- `_hpnc/`
- `_bmad/`
- `.claude/`
- Weitere projektspezifisch konfigurierbar

Durchgesetzt über:

- Executor-Instruktionen (Prompt)
- Post-Run-Check: `git diff --name-only` gegen Blocklist. Bei Verstoß → `failed`

---

## 15. Parallelisierung

### 15.1 MVP: Sequentiell

Ein Task nach dem anderen. Kein Risiko von Konflikten.

### 15.2 Zielarchitektur: Konfigurierbar

```yaml
# night-queue.yaml oder _hpnc/config.yaml
max_parallel: 2
```

### 15.3 Modell-basierte Parallelität

Max 1 Opus + 1 Codex gleichzeitig. Nutzt beide Modelle parallel ohne API-Konkurrenz. Erweiterbar für neue Agenten.

### 15.4 Konfliktvermeidung

- `touches.files` und `touches.resources` werden geprüft
- Bei Überschneidung: sequentielle Ausführung erzwungen
- Automatische Merge-Konflikt-Lösung durch AI = spätere Ausbaustufe, nicht MVP

---

## 16. Run-Artefakte und Nachvollziehbarkeit

### 16.1 Verzeichnisstruktur

```
_hpnc/
  config.yaml
  executor-instructions.md
  known-resources.yaml
  night-queue.yaml
  dispatcher-state.yaml
  runs/
    2026/
      04/
        06/
          001_login-validation/
            run.yaml
            cost.json
            review.md
            dispatcher.log
          002_button-states/
            run.yaml
            cost.json
            review.md
            dispatcher.log
  reports/
    2026/
      04/
        06/
          001-report.md
          002-report.md
```

### 16.2 `run.yaml`

```yaml
status: done
executor: codex
original_executor: codex
reviewer: opus
retry: false
branch: night/login-validation
started: 2026-04-06T01:23:00
finished: 2026-04-06T01:47:00
story_source: stories/login-validation.md
files_changed:
  - src/components/LoginForm.tsx
  - src/components/LoginForm.test.tsx
  - stories/LoginForm.stories.tsx
fix_rounds: []
```

Bei Retry mit Rollentausch:

```yaml
status: done
executor: opus
original_executor: codex
retry: true
retry_reason: "codex timeout nach 25min"
reviewer: codex
fix_rounds:
  - round: 1
    executor: codex
    reviewer: opus
    result: fail
    findings: "Validierungslogik nicht vollständig"
  - round: 2
    executor: opus
    reviewer: codex
    result: pass
```

### 16.3 `cost.json`

Token-Verbrauch pro Task via CLI-Output-Parsing:

```json
{
  "model": "opus",
  "tokens_in": 45000,
  "tokens_out": 12000,
  "duration_seconds": 840,
  "phases": {
    "implementation": { "tokens_in": 30000, "tokens_out": 8000 },
    "review": { "tokens_in": 15000, "tokens_out": 4000 }
  }
}
```

### 16.4 `review.md`

Gleiches Pattern wie Stories — Frontmatter (Maschine) + Body (Mensch):

```markdown
---
review_status: pass
reviewer: opus
blocking_findings: []
non_blocking_findings:
  - severity: low
    area: naming
    description: "Variable 'x' in utils.ts:42 könnte aussagekräftiger sein"
---

## Review: Login-Validierung

### Zusammenfassung
Code ist sauber, Tests decken die Akzeptanzkriterien ab.

### Details
...
```

### 16.5 Alles wird committet

Run-Artefakte werden in den Task-Branch committet und nach `main` gemergt. Damit:

- `git log` zeigt was geändert wurde UND was es gekostet hat
- Bidirektionale Navigation: Datei → Run und Run → Dateien
- Komplette Projekthistorie in `main`, für immer nachvollziehbar

### 16.6 Logging

```yaml
# _hpnc/config.yaml
logging:
  dispatcher: normal          # minimal | normal | verbose
  agent_output: truncated     # full | truncated | none
  max_agent_log_lines: 500
```

---

## 17. CLI-Interface

### 17.1 Morgens

```bash
$ hpnc status                          # Was ist letzte Nacht passiert?
$ hpnc show <task>                     # Details zu einem Task
$ hpnc diff <task>                     # Code-Änderungen anschauen
$ hpnc resume <task>                   # Blocked Task in Claude Code Session weiterarbeiten (Ziel)
```

### 17.2 Tagsüber

```bash
$ hpnc queue                           # Aktuelle Queue anzeigen
$ hpnc queue add <story>               # Story zur Queue hinzufügen
$ hpnc queue remove <task>             # Story aus Queue nehmen
$ hpnc queue reorder                   # Reihenfolge ändern
```

Alternativ über BMAD-Integration: Story-Fertigstellung mündet direkt in Queue.

### 17.3 Vor Feierabend

```bash
$ hpnc validate                        # Alles bereit für die Nacht?
$ hpnc start                           # Sofort starten
$ hpnc start --at 23:00                # Um 23 Uhr starten
$ hpnc start --delay 2h                # In 2 Stunden starten
$ hpnc start --dry-run                 # Nur zeigen was laufen würde
```

### 17.4 Optional

```bash
$ hpnc history                         # Vergangene Runs anzeigen
$ hpnc costs                           # Token-Verbrauch über Zeit
$ hpnc config                          # HPNC-Konfiguration anzeigen/ändern
```

### 17.5 `hpnc validate` — der Feierabend-Check

Prüft vor dem Start:

- Queue geladen, Stories vorhanden
- Alle Stories `night_ready`, Pflichtfelder vollständig
- `blocking_questions` leer
- `tests_required` definiert
- `depends_on` Abhängigkeiten konsistent
- `touches` Überschneidungen erkannt
- Unbekannte Ressourcen gemeldet
- Dev-Server startbar, Ports frei
- DB-Verbindung ok, Migrations aktuell
- Git-Worktrees anlegbar
- Secrets-Hook aktiv
- Disk-Space ausreichend

### 17.6 Report-Format

```markdown
## HPNC Nachtlauf — 2026-04-06 Report #001

### Zusammenfassung
4 Tasks ausgeführt: 2 done, 1 blocked, 1 failed

### Ergebnisse

| # | Task | Executor | Status | Tokens | Dauer |
|---|------|----------|--------|--------|-------|
| 1 | login-validation | codex | done | 42k | 24min |
| 2 | button-states | codex | done | 18k | 12min |
| 3 | nav-refactor | opus | blocked | 95k | 30min |
| 4 | user-api | codex | failed | 31k | 15min |

### Tasks mit Fix-Runden

| Task | Runden | Rollentausch | Ergebnis |
|------|--------|-------------|----------|
| nav-refactor | 3 | ja (ab Runde 3) | blocked |

→ nav-refactor: Nach 3 Runden + Rollentausch nicht gelöst. Story prüfen.

### Tasks mit Retry

| Task | Original | Retry mit | Grund |
|------|----------|-----------|-------|
| — | — | — | — |

### Epic-Fortschritt

**User Profile:** 2/3 done

### Gesamtkosten
Tokens: 186k | Geschätzte Dauer: 1h 21min
```

---

## 18. HPNC als Zwei-Schichten-System

### 18.1 Zentrales Tool

Einmal installiert (npm/pip/binary):

- Dispatcher
- Task-Runner
- State-Machine
- CLI (`hpnc start/status/validate/...`)
- AgentExecutor-Abstraktionen

### 18.2 Projekt-Config

Im Repo (`_hpnc/`):

- `config.yaml` — Projekt-spezifische Konfiguration
- `executor-instructions.md` — Agenten-Regeln für dieses Projekt
- `known-resources.yaml` — Abstrakte Ressourcen
- `night-queue.yaml` — Aktuelle Queue
- `runs/` — Run-History
- `reports/` — Reports

### 18.3 Perspektive

Gleiche Architektur wie BMAD selbst. Perspektivisch als **BMAD-Modul** installierbar.

---

## 19. Nacht-Ablauf (Gesamtsequenz)

```
VOR FEIERABEND:
  $ hpnc validate
  ✅ Alles bereit
  $ hpnc start --at 23:00

23:00 DISPATCHER STARTET:
  1. night-queue.yaml einlesen
  2. Stories validieren (Frontmatter, Pflichtfelder)
  3. release_policy prüfen (task_groups)
  4. depends_on Reihenfolge bestimmen

  PRO TASK:
    5. Task-Runner starten
    6. Task-Runner: Worktree anlegen
    7. Task-Runner: Executor starten (Story + Config + Instruktionen)
    8. Task-Runner: Review anstoßen (Gegenmodell)
    9. Task-Runner: Bei Review-Fail → Fix-Loop (max 3, Rollentausch nach 2)
    10. Task-Runner: Gates ausführen (Build, Tests, Lint, Secrets, Protected Paths)
    11. Task-Runner: Status setzen, run.yaml + cost.json + review.md schreiben
    12. Task-Runner: Ergebnis an Dispatcher melden
    13. Dispatcher: Worktree aufräumen (bei done)
    14. Dispatcher: Auto-Merge wenn merge_policy: done
    15. Dispatcher: dispatcher-state.yaml aktualisieren

  BEI API-LIMIT:
    → Alle Tasks pausieren, warten, fortsetzen

  BEI CRASH:
    → Startup-Recovery: running → interrupted, Queue-Fortschritt beibehalten

05:00 POST-RUN PHASE:
  16. Post-Merge-Checks (wenn auto-merge aktiv)
  17. Report generieren
  18. Queue aufräumen (done-Tasks entfernen)

MORGENS:
  $ hpnc status
  Report bereit.
```

---

## 20. BMAD bleibt Kernbestandteil

### Entscheidung

BMAD wird **nicht ersetzt** und bleibt der zentrale Strukturrahmen.

### Konsequenz

Der Night Dispatcher arbeitet **nicht gegen lose Ideen**, sondern gegen **BMAD-strukturierte Stories**.

### BMAD-Integration

- Story-Fertigstellung kann direkt in HPNC-Queue münden
- `hpnc validate` auch als BMAD-Skill nutzbar
- Story-Templates mit Night-Ready-Feldern via BMad Builder standardisierbar
- Perspektivisch: HPNC als eigenes BMAD-Modul

---

## 21. Rolle von TEA

**Vorläufige Entscheidung:** Sinnvoll, aber eher in einer späteren Ausbaustufe.

Spätere Verwendung:

- bessere Rückverfolgbarkeit von Anforderungen zu Tests
- strukturiertere Quality Gates
- testbezogene Artefakte über mehrere Stories hinweg

---

## 22. Rolle von BMad Builder

**Einsatz ab Phase 2:**

- Night-Ready Story-Templates standardisieren
- Validierungs-Skills für `night_ready`-Prüfung
- Workflow-Integration (Story → Queue)
- Perspektivisch: HPNC als BMAD-Modul bauen

---

## 23. Umsetzungsplan

### Phase 1 — Night Policy und Story-Format festziehen

- `night-ready`-Schema finalisieren (§6)
- Statusklassen finalisieren (§5.3)
- Routing-Regeln finalisieren (§8)
- Pflicht-Gates definieren (§9)
- Zwei-Schicht-Freigabemodell definieren (§7)

### Phase 2 — BMAD anpassen

- BMAD-Artefakte um Night-Ready-Felder erweitern
- BMad Builder: Story-Templates, Validierungs-Skills
- BMAD-Integration: Story-Fertigstellung → Queue

### Phase 3 — Lokale Toolchain festziehen

- Claude Code / Opus CLI-Verhalten testen
- Codex CLI-Verhalten testen
- CLI-Output-Parsing für Token-Tracking validieren
- API-Limit-Erkennung testen (Exit-Codes, Error-Output)
- Git-Worktree-Strategie implementieren
- Storybook + Test Runner + Playwright lokal validieren
- Cross-Platform-Checkliste abarbeiten (Win/Linux)
- Pre-Commit Hook (git-secrets/gitleaks) einrichten
- `.gitattributes` definieren
- Test-Detail-Grad für `tests_required` klären

### Phase 4 — Dispatcher + Task-Runner bauen

**Dispatcher (MVP):**

- Queue einlesen + Frontmatter-Validierung
- `depends_on` + `release_policy` auswerten
- Task-Runner starten (sequentiell)
- State persistieren (`dispatcher-state.yaml`)
- Startup-Recovery
- Worktree/Queue aufräumen
- Report generieren

**Task-Runner (MVP):**

- State-Machine (queued → implementation → review → fix-loop → gates → done/failed/blocked)
- AgentExecutor-Abstraktion (Claude Code + Codex)
- Fix-Loop mit Rollentausch (3 Versuche, Swap nach 2)
- API-Limit-Erkennung + Pause
- `run.yaml` + `cost.json` + `review.md` schreiben
- Protected Paths Post-Run-Check
- Timeout + Aktivitäts-Watchdog

**CLI (MVP):**

- `hpnc start` (mit `--at`, `--delay`, `--dry-run`)
- `hpnc validate`
- `hpnc status`
- `hpnc show <task>`
- `hpnc diff <task>`
- `hpnc queue` (add/remove/reorder)
- `hpnc history`
- `hpnc costs`
- `hpnc config`

### Phase 5 — Pilotbetrieb

Nur sehr sichere, klar definierte Tasks (Welle 1):

- kleine UI-Fixes
- Storybook-Stories ergänzen
- Playwright-Tests ergänzen oder reparieren
- Unit-Tests ergänzen
- kleine Refactorings

### Phase 6 — Ausbau

- Parallelisierung (konfigurierbar + modellbasiert)
- `hpnc resume` (Claude Code Session mit Task-Kontext)
- TEA-Integration
- Scope-Gate (Diff-Größe, Datei-Anzahl)
- Token-Budget pro Task
- Notifications (Desktop/E-Mail/Push)
- Bessere Dashboards / Metriken
- Retry-Strategien (Commit-Watchdog, Test-Retry-Limit)
- Auto-Merge-Konflikt-Lösung durch AI
- HPNC als BMAD-Modul
- Builder-basierte Erweiterungen

---

## 24. Erste Betriebsstrategie

### Welle 1

- kleine UI-Fixes
- Storybook-Stories ergänzen
- Playwright-Tests ergänzen oder reparieren
- Unit-Tests ergänzen
- kleine Refactorings

### Welle 2

- kleine echte Features
- kleinere Backend-/Frontend-Erweiterungen
- klar definierte CRUD-Arbeiten

### Welle 3

- größere Features
- breitere Refactorings
- komplexere cross-cutting Änderungen

---

## 25. HPNC-Konfiguration

```yaml
# _hpnc/config.yaml

# Projekt
project_name: "mein-projekt"

# Defaults
defaults:
  merge_target: develop
  executor: auto
  reviewer: opposite
  timeout: 30m
  max_fix_attempts: 3
  swap_executor_after: 2
  max_review_rounds: 4

# Schedule
schedule:
  start: "23:00"
  report_ready_by: "05:00"
  post_run_checks: true

# Parallelisierung
parallelization:
  max_parallel: 1                  # MVP: sequentiell

# Logging
logging:
  dispatcher: normal
  agent_output: truncated
  max_agent_log_lines: 500

# Protected Paths
protected_paths:
  - _hpnc/
  - _bmad/
  - .claude/

# Known Resources
known_resources:
  - db-migrations
  - api-definitions
  - protocols
  - auth
  - routing
```

---

## 26. Betriebsregeln für Agenten in neuen Sessions

1. **BMAD ist der zentrale Planungsrahmen.**
2. **Nightly-Arbeit darf nur auf `night-ready`-Stories erfolgen.**
3. **Keine Annahmen treffen, wenn menschlicher Input nötig ist.**
4. **Tests sind Pflicht. Tests müssen vorab geplant sein.**
5. **UI-Tickets brauchen Storybook + Storybook-Tests + Playwright + A11y-Checks.**
6. **Review über Reviewer-Pool, nie durch den eigenen Executor.**
7. **Keine direkten produktiven Merges außer explizit konfiguriert.**
8. **Isolation über Branch/Worktree.**
9. **Nur lokal-only Architektur; keine Chromatic-Abhängigkeit.**
10. **Status sauber protokollieren: `done`, `proposal`, `blocked`, `failed`, `interrupted`, `merged`.**
11. **Protected Paths nie anfassen.**
12. **Bei Scope-Überschreitung: `blocked` melden, nicht weitermachen.**

---

## 27. Kurzfassung für eine neue Agent-Session

- Dieses Projekt baut **HPNC**, eine lokale Night-Agent-Architektur.
- **BMAD bleibt zentral**.
- Es werden **Opus und Codex** verwendet, Architektur offen für weitere Agenten.
- **Opus** ist für komplexe Planung/Review, **Codex** für konkrete Implementierung.
- **Reviewer-Pool:** Review nie durch den eigenen Executor. Konfigurierbar, `skip` möglich.
- Nachts laufen nur **vollständig geklärte, testdefinierte `night-ready`-Tasks**.
- **Zwei-Schicht-Freigabe:** Frontmatter = "darf", Queue = "soll heute".
- **Dispatcher + Task-Runner getrennt.** Dispatcher ist Scheduler, Task-Runner steuert Lifecycle.
- **Hartnäckiger Fix-Loop** mit Rollentausch (3 Versuche, Swap nach 2).
- **Chromatic ausgeschlossen**, lokal-only.
- UI-Qualität lokal über **Storybook + Storybook Test Runner + Playwright + A11y-Checks**.
- Ergebnisse in **isolierten Branches/Worktrees**, Run-Artefakte werden committet.
- Status: `done`, `proposal`, `blocked`, `failed`, `interrupted`, `merged`.
- **CLI-gesteuert:** `hpnc start/validate/status/show/diff/queue`.
- **HPNC = zentrales Tool + projektspezifische Config in `_hpnc/`**.
- Spätere Ausbaustufen: **TEA**, **Builder**, Parallelisierung, `hpnc resume`, Notifications.

# FERTIG 1.2.0 — persönliche KI, die man durch Vormachen programmiert

The current portable contract is documented in
[docs/architecture.md](docs/architecture.md). In particular, the exact
unified solver is `bindings → semantic → math → miner → abstain`; the larger
desktop and HSSLM surfaces are optional extensions, not prerequisites.

FERTIG verbindet inzwischen zwei nutzbare Ebenen:

- **Lokale Desktop-Skills:** Ein Mensch zeigt auf macOS eine Aufgabe, gibt ihr
  einen Namen und ruft sie später in normaler deutscher oder englischer Sprache
  auf. FERTIG findet sichtbare Ziele nach Layoutänderungen wieder, handelt
  schrittweise, prüft jede sichtbare Wirkung und speichert die Fähigkeit lokal.
- **Grounded Werkzeuge:** Mathematik, quantitative Fakten und
  `.causal`-Graphen bleiben explizite, nachrechenbare Ausführungspfade hinter
  derselben Chat-Oberfläche.

Die Produktidee lautet: **Ein Begriff ist eine ausführbare grounded Skill.**
Zeigen ist Programmieren; ein Satz ist der Aufruf. Der Desktop ist der heute
implementierte Adapter, Kamera und Robotik sind der Moonshot.

Der historische Graph-/Korpus-Kern bleibt gewicht-frei und deterministisch:
Entitäten und Mechanismen kommen aus `.causal`-Graphen, Sprachübergänge aus
gemessenen Zählungen. Daneben gibt es den lernenden Desktop-Pfad und das kleine
trainierte HSSLM, das nur innerhalb bereits belegter Kandidaten ranken darf.

---

## Schnellstart

```bash
pip install -r requirements.txt          # numpy + msgpack + torch

# Sofortiger kompletter Produktbeweis ohne macOS-Rechte oder echte Eingaben
python3 -m fertig product-demo

# Lokale Desktop-Alpha
python3 -m fertig desktop-doctor         # alle Mac-Rechte + HSSLM, niemals Eingabe
python3 -m fertig teach "rechnung herunterladen"  # vormachen, mit F8 stoppen
python3 -m fertig explain "rechnung herunterladen"
python3 -m fertig do "rechnung herunterladen"
python3 -m fertig tasks

# Vorhandene Skills komponieren, Textschritte parametrisieren und korrigieren
python3 -m fertig compose "address report" --from "open editor" "fill recipient"
python3 -m fertig template "send named report" --base "address report" \
  --slot recipient=1 --optional-slot subject=2
python3 -m fertig do "send named report" \
  "recipient=Alice Example" "subject=August report"
python3 -m fertig correct "fill recipient" --step 0  # atomarer Ein-Schritt-Skill

# Gemeinsame natürlichsprachliche Oberfläche; ohne Text startet ein Dialog
python3 -m fertig assistant
python3 -m fertig chat "How fast can a cheetah run?"
python3 -m fertig chat "Why does smoking affect health?"
python3 -m fertig hsslm-status

# Garantiert nur auflösen, nie Bildschirm aufnehmen oder Eingaben senden
python3 -m fertig assistant --resolve-only "mach rechnung herunterladen"

# Symbolischer Graph-/Korpus-Kern
python3 -m fertig info
python3 -m fertig graph
python3 -m fertig speech
python3 -m fertig chains
python3 -m fertig corpus "the candle"
python3 -m fertig intent -x "explain how smoking affects health"
```

Tests: `python3 -m pytest tests/ -q`

`product-demo` zeigt drei sichtbare atomare Fähigkeiten, baut daraus per
natürlicher Sprache einen Workflow und eine Textvorlage, lädt beide Stores in
einem neuen Assistenten und führt den Workflow mit einem neuen Textwert auf
verschobenem Layout aus. Alle drei Wirkungen werden sichtbar verifiziert;
dieselben absoluten Demonstrationskoordinaten scheitern als Kontrolllauf.
`--json` liefert den vollständigen maschinenlesbaren Report.

---

## Shipbare Produkt-Alpha: FERTIG Apprentice

Die Desktop-Alpha ist nicht mehr nur Roadmap. Der komplette Vertikalschnitt ist
implementiert:

1. `teach` zeichnet eine menschliche Demonstration mit einem passiven lokalen
   macOS-`CGEventTap` und parallelen Screenshots auf; F8 beendet die Aufnahme.
2. Das zustandsabhängige Screen-Modell lernt visuelle Anker, Form, lokalen
   Kontext und den relativen Klickpunkt statt bloßer Koordinaten. Retina-Pixel
   werden dabei auf dieselben logischen Koordinaten wie Mausereignisse normiert.
3. Der persistente `TaskStore` speichert benannte Tasks; rohe Demonstrationen
   bleiben als versionierte JSON/NPZ-Paare erhalten. Wiederholtes `teach` für
   denselben Namen erweitert die Prototypen, statt alte Erfahrung zu löschen.
   Kompositionen liegen mit den Tasks in `data/desktop_tasks.json`, Vorlagen
   separat in `data/desktop_templates.json`.
4. `do` arbeitet geschlossen: beobachten → eine Aktion → sichtbare Wirkung
   verifizieren → neu planen. Fehlende oder mehrdeutige Ziele stoppen vor der
   nächsten Eingabe mit `UNKNOWN`.
5. `compose` speichert neue Abläufe aus vorhandenen atomaren oder bereits
   komponierten Skills. Die Verschachtelung wird in Ausführungsreihenfolge zu
   atomaren Blättern aufgelöst.
6. `template` macht ausgewählte demonstrierte Textaktionen zu erforderlichen
   oder optionalen Laufzeitwerten; ihr Beispieltext wird direkt aus der
   Demonstration abgeleitet.
7. `correct` ersetzt genau einen Schritt eines atomaren Skills durch eine neue
   Ein-Aktions-Demonstration und persistiert den neuen visuellen Prototyp.
8. `assistant`/`chat` verbindet Desktop-Skills, Mathematik, quantitative
   Antworten und kausale Graphwerkzeuge in natürlicher Sprache.

Sichere beziehungsweise nicht verlässlich als unsicher bestimmbare Textfelder
werden beim passiven Mitschnitt standardmäßig nicht aufgezeichnet. Die reale
macOS-Nutzung benötigt Screen Recording sowie Input Monitoring/Accessibility.
Die heutige Alpha zielt auf kurze, sichtbare und reversible Aufgaben; Text ist
dynamisch, wo explizite Text-Slots deklariert wurden, und Skills können
hierarchisch komponiert werden. Automatisches Herauslesen neuer Werte aus dem
Bildschirm, bedingte Verzweigungen und robuste offene UI-Wahrnehmung sind die
nächsten Produktlifte.

Der frühere additive RGB-Kernel bleibt als kleine kontrollierte Lernkurve
verfügbar:

```bash
python3 -m fertig apprentice --steps 8 --compare-shuffled
python3 -m fertig apprentice --steps 16 --json
```

Die disruptive, aber greifbare Zielarchitektur – persönliche KI durch Vormachen,
Desktop heute, Kamera/Robotik später – steht mit aktuellem Implementierungsstand
und ehrlichen Grenzen in [MOONSHOT_APPRENTICE.md](MOONSHOT_APPRENTICE.md).

### Skills zusammensetzen, parametrisieren und korrigieren

Die direkte CLI-Grammatik lautet:

```text
# NAME führt TASKs in genau dieser Reihenfolge aus; mindestens zwei sind nötig
fertig compose NAME --from TASK TASK...

# field wird aus der Textaktion am globalen Schritt STEP abgeleitet
fertig template NAME --base TASK --slot field=STEP [--optional-slot other=STEP]

# Werte mit Leerzeichen bleiben jeweils ein quotiertes slot=value-Argument
fertig do 'TEMPLATE' 'field=Value with spaces'

# Genau eine Ersatzaktion vormachen und danach F8 drücken
fertig correct TASK --step N
```

Alle sichtbaren Schrittindizes sind **nullbasiert**. Bei einer Vorlage auf
einer Komposition ist `STEP` der **globale Index der abgeflachten
Aktionsfolge**, nicht der lokale Index eines Kind-Skills. `explain NAME` zeigt
diese Zuordnung samt dem aus der Demonstration übernommenen Beispielwert.
Erforderliche Slots müssen beim Aufruf gesetzt werden; ein ausgelassener
optionaler Slot behält seinen demonstrierten Text.

Vor dem ersten Desktop-Input prüft FERTIG Namen, Pflichtwerte, unbekannte oder
doppelte Slots, Zielindizes, Textaktions-Typ und den aktuellen Basis-Task. Ein
fehlgeschlagener Preflight führt **null Aktionen** aus. Nach erfolgreichem
Preflight bleibt die normale visuelle Schleife aktiv: Auch komponierte und
parametrisierte Skills relokalisieren sichtbare Ziele und verifizieren nach
jeder Aktion den Folgezustand.

Kompositionen dürfen atomare Skills und andere Kompositionen enthalten;
unbekannte Referenzen, Duplikate, Zyklen und eine pathologische Tiefe werden
abgelehnt. Korrekturen erfolgen bewusst am atomaren Blatt: Die Aufnahme muss
genau eine Aktion enthalten und wird mit F8 beendet. Der `--step`-Index ist
dort ebenfalls nullbasiert.

Dieselben Operationen funktionieren in der natürlichen Oberfläche:

```text
compose address report = open editor + fill recipient
template send named report from address report recipient=1 subject?=2
do send named report recipient="Alice Example" subject="August report"
korrigiere fill recipient schritt=0

komponiere address report = open editor + fill recipient
parameterisiere send named report aus address report recipient=1 subject?=2
mach send named report recipient="Alice Example" subject="August report"
```

---

## Fähigkeiten (Moonshots)

```bash
# Moonshoot A: Video → Plan → Prosa → Rück-Verifikation (FREIGEGEBEN/VERWORFEN)
python3 -m fertig erzaehlen data/puls.gif
python3 -m fertig erzaehlen data/wander.gif

# Der o1-Schreiber (Endgame): FERTIG spricht von alleine perfekte Sätze.
# Fakten aus dem Graphen (Wahrheit = Konstruktionsbedingung) -> HSSLM
# RANKT Übergänge/Pronomen/Fügungen per Logprob im Kontext (erzeugt nie
# Wörter, es wählt) -> unsichtbare Prüfung -> AUSGELIEFERT/ZURÜCKGEHALTEN.
python3 -m fertig schreiben smoking
python3 -m fertig schreiben exercise
python3 -m fertig schreiben caffeine --graph data/chained.causal

# Diskurs-Komponist + Text-Zertifikat (FE6-FE8): Given-New-Ordnung,
# Pronomen nur mit Ohr-Garantie, Claims+Quittungen+SHA — Tamper =
# VERWORFEN, maschinell nachgerechnet.
python3 erweiterung/diskurs.py

# Form-Arena (FE3-FE5): beste belegte Prosa-Variante pro Kante
# (UID-Regel: min uid_var -> max fluency; Ohr-Richter pfeift)
python3 -m fertig formarena

# Utterance-IR: Plan ⇄ Prosa ⇄ Plan — narrative Aussagen gegen den .causal-Graph
# rückverifiziert; unbelegte Inferenz-Kanten werden VERWORFEN (Accountability).
python3 -m fertig sprechen smoking
python3 -m fertig sprechen exercise

# Moonshoot B: kleiner HSSLM-Formkern. Plan → Kandidaten → HSSLM-Ranking
# → IR-Verifikation; nur belegte Varianten werden freigegeben. Das Modell
# liefert keine Fakten und erfindet keine ausführbaren Skills.
python3 -m fertig sprechen --engine hsslm smoking

# GroundZero (Codex-Labor, integriert): formale Symbol-Grounding-Zertifikate
# v1: 10/10 Achsen bestanden (estimate 1.0), 3 Negativ-Kontrollen korrekt
#     abgelehnt (0.0) — data/world.causal, data/chained.causal
# Grade-3: noncompensatory Diagnostik, isolierte Child-Prozesse, 8/8 Achsen
python3 -m fertig bench groundzero            # v1 (10 Achsen)
python3 -m fertig bench groundzero --grade3   # Grade-3 (isolierte Prozesse)
python3 -m fertig bench causal-v2             # P0: aktive Kausal-Induktion
                                              # (64/64 Blöcke, aktiv>passiv p<1e-17)
```

Die exakte Größe von `data/hsslm_form.pt` ist **2.214.368 eindeutige
trainierbare Parameter** beziehungsweise **2.316.768 serialisierte
Tensor-Einträge** bei **8.911.799 Byte**. Die Differenz entsteht durch
gebundene Embedding-/Output-Gewichte. `python3 -m fertig hsslm-status` misst
diese Werte direkt am Checkpoint.

HSSLM ist ein schmales englisches Formmodell, kein allwissendes LLM. Sein
produktiver Einsatz ist constrained scoring: Es rankt bereits grounded Skills,
Antwortformen oder Graphkandidaten; Fakten und Handlungsrechte kommen aus den
deterministischen Werkzeugen und dem endlichen Skill-Speicher.

---

## Erweiterung 2026-08-11 (David) — FERTIG spricht Gelebtes

```bash
# Das Weltbuch: gelebte Evidenz (o1-state acted-Records, 5159) -> Kausal-
# Kanten MIT Quittung (Zählung + Frame + SHA-256) -> bit-exaktes Replay
# durch die Vendor-Welt -> FREIGEGEBEN/VERWORFEN. Nie ohne Beleg.
python3 -m fertig weltbuch

# PS-Lifted-Impuls-Walk (Fiedler-Fluss, p_continue .95) — deterministisch,
# nur echte Kausal-Kanten; Verdict: Health-Demo-Graph = Null-Habitat
# (zyklenfrei) — Einsatzort sind gewachsene Graphen.
python3 erweiterung/lifted_walk.py
```

- **Weltbuch-Prinzip**: jeder Satz trägt Quittung („gelebt 856×; frame 5,
  sha 791451165c…“), Provenance-Gate spielt 5 Belege bit-exakt nach —
  Harnads *direkte sensorimotorische Evidenz* (Codex-Evidenz-Tier 1),
  erster Graph, dessen Kanten nicht gelesen, sondern GELEBT wurden.
- **Befunde gefixt**: (1) CRC-Integritätscheck toleriert jetzt
  Writer/Reader-Algorithmus-Drift (xxh64 vs md5[:8]) — kein Fehlalarm
  mehr in Umgebungen ohne xxhash; (2) fehlendes msgpack/xxhash meldet
  sich laut per RuntimeWarning statt stiller Fallbacks.

---

## Architektur

Der Produktpfad ist eine direkte, geschlossene Schleife:

```
natürliche Sprache ──► assistant/chat ──► TaskStore / Rechen- / Quant- / Graphwerkzeug
       teach ──► passiver CGEventTap + Screenshots ──► ScreenTaskModel
compose/template ──► persistente Skill-Hierarchie + dynamische Text-Slots
     correct ──► eine neue atomare Transition ──► Prototyp aktualisieren
          do ──► beobachten ──► relokalisieren ──► eine Aktion
                          ▲                         │
                          └── Wirkung prüfen ◄── Screenshot ──┘
```

Der optionale HSSLM-Layer sitzt nur innerhalb von `assistant/chat` und darf
Formulierungen oder echte lexikalische Gleichstände ranken. Er umgeht weder
den `TaskStore` noch die sichtbare Ergebnisprüfung.

### Architektur des symbolischen Kerns

```
.causal-Graph / Korpus
        │
        ▼
[load_graph / build_vocab]      gemessene Kanten: Adjazenz bzw. Trigramm-Zählungen
        │
        ▼
[inference.pass1/2/3]           (Graph-Modus) Jaro-Winkler + exakte Ketten + Richtung
        │
        ▼
[Walk]                          Kontraktions-Sampler (tau-kontrolliert, Zeno-Schedule),
        │                       Ginibre-Kern-Gewichtung, BvN-Pfad-Integral
        ▼
[Berry-Phasen-Wächter]          bphm: Schleifen-Erkennung auf Hyperboloid-Zuständen
        │
        ▼
[verbalize / verbalize_mined]   Form: Polaritäts-bewusste Verknüpfer,
                                handgeschrieben oder aus Korpus gemessen
```

### Module

| Modul | Quelle | Rolle |
|---|---|---|
| `sampler` | SYMBOLISCH/hsslm_s | tau→Temperatur (F36), Kontraktions-Sampling (F33–F40), Zeno/Anti-Zeno (F35), Ginibre-Kern (F38), BvN-Zerlegung (F63–F68) |
| `state_init` | fable language/hsslm_s | Hyperboloide Symbol-Zustände (Minkowski-Norm −1) |
| `bphm` | fable language/hsslm_s | Berry-Phasen-Wiederholungs-Erkennung, Fidelity, BvN-Modulation |
| `pattern_bank` | fable language/hsslm_s | Aus Korpora gemessene Satz-Skelette + Opener, F30-Weak-Signal-Backoff |
| `inference` | fable language/hsslm_s | Jaro-Winkler, Möbius-Konfidenz, 3-Pass-Ketten (exakt → Richtung → fuzzy) |
| `pipeline` | SYMBOLISCH run_causal/speak_causal | Graph laden, Walk, Verbalisierung (Polaritäts-Vorzeichenregel) |
| `corpus` | SYMBOLISCH run_symbolic | Vokabular + Trigramm/Bigramm-Kanten, Fortsetzung mit Rezenz-Penalty |
| `mined` | SYMBOLISCH speak_mined | Verbalisierung mit gemessener Muster-Bank (echter RNG nur in der Form) |
| `intent` | neu (FERTIG) | NeuroSymbolische Intent-Maschine: NL → Parse-Baum → Intent-Tupel (Aktion, Ziel, Konfidenz, Grounding) — Wirkung-Stil-Parsimonie-Scoring, Which-Path-Visibility, Jaro-Winkler-Ziel-Matching |
| `tools` | neu (FERTIG) | Tool-Schicht (Stufe 5 der Foss-Lernhierarchie): speech/chain/prevent/consult/help — Intents werden zu registrierten Tool-Calls |
| `learn` | neu (FERTIG) | Lern-Modul: gemessene Lexika wachsen aus Korpora (Verb-/Nomen-Slots, deterministisches Zählen) — erweitert die Intent-Coverage ohne Code-Änderung |
| `arena` | neu (FERTIG) | Präregistrierter Selbst-Benchmark: 12 Befehle, 100% deterministisch — die Zahlen sind Ledger-Einträge |
| `desktop` / `macos_recording` | FERTIG | Strikte Aktions- und Adaptergrenze, echte macOS-Screenshots/Eingaben und passiver `CGEventTap`-Demorecorder |
| `screen_model` / `desktop_agent` | FERTIG | Zustandsabhängige visuelle Relokalisierung, Wirkungskontrolle, persistente atomare und verschachtelt komponierte Tasks sowie Ein-Schritt-Korrektur |
| `skill_slots` | FERTIG | Persistente dynamische Textvorlagen, globale nullbasierte Schrittbindung, Demo-Beispiele und aktionsfreier Invocation-Preflight |
| `assistant` / `chat` | FERTIG | Deutsche/englische Teach-/Do-/Explain-/Compose-/Template-/Correct-Oberfläche und gemeinsamer Router für Desktop, Mathematik, Messwerte und Graphen |
| `hsslm_interface` | FERTIG | Lazy Runtime, exakte Checkpoint-Messung und constrained Ranking über bereits grounded Kandidaten |
| `_vendor/dotcausal` | fable package/src/dotcausal | .causal-Format (core/io/inference), vendored, unverändert |

Die historischen Kernmodule stammen aus den angegebenen Quellen. Die
Produktmodule für Desktop, Sprache, Persistenz und HSSLM-Anbindung sind native
FERTIG-Komponenten.

---

## Grundlagen — die Preprints, auf denen alles beruht

Die Mechanik des Systems ist die direkte Umsetzung der Foss-Preprints
(`SYMBOLISCH/preprints md/`):

| Baustein | Preprint | Umsetzung |
|---|---|---|
| **Kontraktion** | *Collapse Is Contraction* | `sampler.contraction_sample` — tau in [0, 0.95] ist der Kontraktionskoeffizient; bei tau→1 Phasenübergang (F35, `TAU_MAX`). Tau ist der Birkhoff-Ordnungsparameter: τ<1 = klassische Phase |
| **Möbius-Kopplung** | *MarkovChains to MinkowskiSpace* | `tau_to_temperature`: T(tau) = (1 − tau²)^(−1/2) − 1 — wörtlich der Lorentz-Faktor γ(λ) aus dem Paper; die Möbius-Kopplung f(λ,v) = (λ+v)/(1+λv) in Temperaturform |
| **Ginibre-Kerne** | *One Constant Rules All 2D Spectra* + *Universal Phase Transition GOE→Ginibre* | `ginibre_select_weights` (F38): w = s³·exp(−1.2·s²) — das s³ ist die kubische NND-Repulsion (β=3) aus dem Paper; Sinkhorn in `bvn_decompose` = KL-Gradientenfluss (Sättigung ≤10 Iterationen); `TAU_MAX` = kritischer Punkt |
| **BvN-Pfade** | *Non-Reversibility Is All You Need* | `bvn_decompose` / `bvn_path_integral_sample` (F63): 414 Permutations-Pfade („Parallel-Universen“), globale Summe in 11 Runden (`convergence_rounds`, F65) |
| **Spektrale Lücke** | *Linear Cheeger Improvement (Foss Gap Theorem)* + *Constant-Round Gossip* | `consensus_convergence_bound` (F67): (1 − λ₂/M)^t; und der Sampler-Default `tau=0.65` entspricht der optimalen Vorwärtswahrscheinlichkeit p_c ≈ 0.65 aus dem Gap-Theorem |
| **Topologischer Schutz** | *Unitarity Is the Boundary* | Berry-Phasen-Wächter in `bphm` = das dritte universelle Gesetz des Foss-Boundary-Theorems (topological protection) im Zustandsraum |
| **Lernhierarchie** | *Emergent Gravity / Foss Brain v2* | Die sechsstufige Lernhierarchie des Foss Brain (Habituation, Konditionierung, Raumgedächtnis, Grenz-Kommunikation) erscheint in FERTIG als: Rezenz-Penalty (Habituation), Konfidenz-Aktualisierung (Rescorla-Wagner), Hyperboloid-Zustände (Raumgedächtnis), ehrliche Graph-Sackgassen (Grenz-Kommunikation) |

**Determinismus-Trennung im symbolischen Kern:** *Fakten* müssen
deterministisch sein (Graph-Lookup, Zählungen); *Form* darf je nach Befehl
zufällig oder durch HSSLM gerankt sein. Die Desktop-Alpha lernt dagegen
absichtlich aus lokalen Demonstrationen und realen Screenshots.

---

## Daten

- `data/chained.causal` — der mitgelieferte Beispiel-Graph (3 KB), Quelle:
  `kimi/workspace/AI_Causal_Work/.../corpora/chained.causal`
- `data/faraday_candle.txt` — Faraday-Korpus für Korpus-Modus und
  Muster-Bank-Mining (223 KB)
- Eigene Graphen/Korpora: einfach `--graph`/`--corpus` auf eigene Dateien
  zeigen; das System ist format-getrieben, nicht daten-getrieben.

## Die Kette: labern → verstehen → lernen → toolcalls → benchmarks

FERTIG ist jetzt eine geschlossene Kette, jede Stufe deterministisch und gemessen:

1. **Labern** — `graph`/`speech`/`corpus`/`mined`: gewicht-freie Sprache aus
   gemessenen Übergängen (Fakten exakt, Form generiert).
2. **Verstehen** — `intent`: NL-Befehl → Intent-Tupel. Deterministischer Parse
   (Aktion aus gemessenem Lexikon, Ziel per Jaro-Winkler gegen das
   Graph-Vokabular), Parsimonie-Scoring im Wirkung-Stil
   (`score = log(fit) − 0.5·complexity`), Which-Path-Visibility als
   Ambiguitäts-Detektor. Fehler sind sichtbar (Parse-Baum), nie geraten.
3. **Lernen** — `learn`: gemessene Lexika wachsen aus Korpora (Verb-/Nomen-
   Slot-Zählen). Neue Verben werden Aktionen, neue Nomen Ziel-Kandidaten —
   Coverage compoundiert, ohne Code-Änderung.
4. **Tool-Calls** — `intent -x`: Intent → registrierter Tool-Call
   (speech/chain/prevent/consult/help). Nur grounded Intents werden
   ausgeführt; Fehlschläge sind ehrlich („kein Reduktor im Graphen").
5. **Benchmarks** — `arena`: präregistrierter Evaluations-Satz, 100%
   deterministisch. Stand (v1): 12/12 Volltreffer bei Aktion UND Ziel.

Der nächste Schritt der Vision: dieselbe Kette gegen ein LLM in einer
präregistrierten Arena (Intent-Präzision auf öffentlichen NLU-Sets).

## SOTA-Benchmarks — wo FERTIG steht (gemessen, nicht behauptet)

```bash
python3 -m fertig bench snips    # Intent-Klassifikation (SNIPS, 7 Intents)
python3 -m fertig bench blimp    # Grammatikalität (BLiMP, 8 Subtasks)
```

### SNIPS (Intent) — v2: 88.3% (Chance: 14.3%, DeepSeek gemessen: 98–100%)

Verb-Bigramme + Objekt-Slot-Signale (gemessene Interpolation): 5 Intents bei
92–98%. Die LLM-Arena (scripts/llm_arena.py) misst DeepSeek auf denselben
Daten: der Abstand ist das Goal.

### BLiMP (Grammatikalität) — v2: 52.9% über Chance (67 Subtasks, 67k Paare)

Struktur-Regeln (Kongruenz + Inseln) heben das System über die 50%-Chance:
  determiner_noun 87–90%, left_branch_island 7.9% → **82.6%**,
  wh_questions_subject_gap 74.9%. Anaphern (24.9%) und wh_with_gap
  (38.8%) sind die nächsten Ziele.

### HumanEval (Code) — v2: 0% ungesehen, 80.0% Retention

Nach dem Fix des Funktionsnamen-Parsings (Unterstriche!) erreicht der
Compounding-Loop 24/30 auf gelernten Problemen. Unseen bleibt 0% —
Fragment-Retrieval generalisiert nicht; das ist FORGEs Territorium.

### HellaSwag / WinoGrande / LAMBADA — die Statistik-Floor-Karte

  HellaSwag 26.7% (Chance 25%) | WinoGrande 50.9% (Chance 50%) |
  LAMBADA 0% (by Konstruktion n-gram-ausgefiltert)

Diese Benchmarks brauchen Weltwissen, nicht Struktur — die ehrliche
Grenze der Statistik-Schicht. WinoGrande-Kongruenz-Regeln wurden gebaut,
gemessen (48% auf gefeuerten Fällen) und verworfen: debiased gegen
Shortcuts.

### LLM-Arena (präregistriert, scripts/llm_arena.py)

DeepSeek auf denselben Samples: HellaSwag 45% vs 26.7% | WinoGrande 70%
vs 50.9% | BLiMP-Sample 85% vs (24.9%/82.6%) | SNIPS 100% vs 88.3%.
FERTIG gewinnt: Kosten (0€, offline, ms), Determinismus (bit-identisch),
Struktur-Subtasks (left_branch 82.6% ≈ DeepSeek-Niveau).

### Die Goals (aus den Zahlen abgeleitet, nicht aus Meinungen)

1. SNIPS: 88.3% → 93%+ (SearchScreeningEvent 68.6%: Film-Slots)
2. BLiMP: 52.9% → 58%+ (Anaphern 24.9% → 60%, wh_with_gap 38.8% → 60%)
3. HumanEval Retention: 80% → 90%+ (Imports der Bodies)
4. HellaSwag: 26.7% → 30%+ (4-gram-Erweiterung)

Jede Verbesserung ist ein Ledger-Eintrag: gleiche Benchmarks, gleiche
Argumente, deterministisch reproduzierbar.

## Der Gap-Loop: das Internet als Online-Learning

```bash
python3 -m fertig grow "vitamin d"          # ein Ziel, alle 7 Quellen
python3 -m fertig grow --gaps              # Lücken aus der Arena automatisch
python3 -m fertig grow sugar --sources wikipedia,pubmed   # Quellen wählen
```

**Lücke erkennen → Query formulieren → scrapen → extrahieren → speichern →
neu messen.** Der Kreislauf (F4: externer Index, on demand):

1. **Gap-Detection** existiert: `unknown-target`-Status + Arena-Fehlschläge
2. **8 Quellen** (`fertig/sources.py`, je fetch+parse getrennt):
   **web (generisch: Suche → beliebige Seiten → Text, Trafilatura +
   stdlib-Fallback)**, wikipedia (Infobox 0.7), wiktionary (0.45),
   pubmed (0.40), arxiv (0.35), semantic_scholar (0.35), openalex (0.35),
   duckduckgo-Snippets (0.30)
3. **Beliebige URL direkt**: `fertig crawl <url> --store` — eine Schicht
   für jede Website statt tausend Einzel-Adapter (Trafilatura für
   Boilerplate-Removal, stdlib-Fallback ohne Dependencies)
3. **Kausaler Satz-Extraktor**: (NP, Kausal-Verb, NP) mit Negations-Schutz —
   "no evidence that X causes Y" erzeugt keine Kante
4. **Evidenz-Aggregation**: gleiches Triplett aus n Quellen →
   conf = min(0.95, max_conf + 0.06·(n−1))
5. **Speicherung**: `data/world.causal` (CausalWriter) — wird von pipeline/
   intent/tools automatisch gemergt (`load_graph_merged`)
6. **Messbar**: derselbe Befehl vorher (unknown) vs. nachher (grounded)

Neue Quellen = eine parse-Funktion + ein Konfidenz-Tier + Registrierung in
`SOURCES`. Kein Repo-Import, kein Supply-Chain-Risiko — jeder Fetcher ist
~40 Zeilen audit-fähiger Code.

## Die Grounding-Schicht: Erdungs-Ebenen (ehrliche Terminologie)

```bash
python3 -m fertig ground cheetah          # Symbol verankern (Ebenen L1/L2)
python3 -m fertig ground --all            # alle Graph-Symbole + Coverage
python3 -m fertig quant --all             # quantitative QA (Anker-Beweis)
python3 -m fertig vision cheetah giraffe elephant -u   # Harnad-Ebene (L3)
```

**Wichtige Einschränkung**: Nichts davon ist „vollständig geerdet" im
Harnad-Sinn (1990). CLIP-Text-Encoder sind aus menschlichen Texten
trainiert, Wikipedia-Bilder sind menschenkuratiert, Zahlenstrings sind
menschliche Symbole — alles ist menschlich vermittelt. Die ehrlichen
Ebenen:

| Ebene | Anker | Vermittlung |
|---|---|---|
| L0 | nur Wort↔Wort-Kanten | reiner Regress |
| L1 | quantitative Anker (Zahlen+Einheiten) | menschlicher Text, aber nicht-lexikalische Denotation |
| L2 | perzeptuelle Bindung (CLIP/Commons-Bilder) | Pixel primär, Wort↔Bild-Zuordnung kuratiert |
| L3 | **unüberwachte Kategorien aus Pixel-Struktur** (fertig.vision) | Kategorien entstehen ohne Labels — die nächste Annäherung an Harnads sensorische Transduktion |

Die L3-Mechanik ist deterministisch (kein neuronales Netz):
Signatur(Bild) = HSV-Histogramme ⊕ Textur ⊕ Form-Gitter; k-means über
Signaturen findet die Kategorien; Wörter werden erst NACH der
Cluster-Bildung zugeordnet. Lokal verifiziert: 3 Arten, 12 Bilder,
keine Labels → Purity 100%.

Die kategorielle Wahrnehmung (Harnad 2005: „To cognize is to
categorize") ist messbar: within-category-Distanz < between-category-
Distanz (harnad_ratio < 1).

## Stream-Lernen: das Internet als permanenter Video-Lehrer (O(1))

```bash
python3 -m fertig stream data/puls.gif --seconds 10
python3 -m fertig stream "https://www.youtube.com/watch?v=..." --seconds 60
```

Die o1-state-Philosophie auf Video: **Der Stream ist ein Iterator, kein
Objekt.** `fertig/stream.py` verdichtet jeden Frame in gleitende
Statistiken — konstantes Memory bei unendlichem Input:

- **Prototyp**: EMA der Frame-Signaturen (was ist typisch?)
- **Bewegung**: EMA der Signatur-Distanz + Pixel-Differenz (zwei
  komplementäre Primitive — Histogramme sind translations-invariant!)
- **Grammatik**: begrenzte Code-Übergänge (Top-K pro Code, verdrängt)
- **Periodizität/Szenenwechsel**: Noether-Detektoren auf dem Fenster

Quellen: ffmpeg (Datei/URL) + **yt-dlp** (YouTube, Live-Streams).
Live getestet: „Me at the zoo" → yt-dlp → ffmpeg → 16 Frames gelernt,
Periodizität erkannt, 11 Grammatik-Kanten, stabile Zyklus-Fortsetzung.

**Der Lern-Zyklus schließt sich** (`--name` + `--recognize`):

```bash
python3 -m fertig stream video_a.gif --name puls     # Kategorie lernen
python3 -m fertig stream video_b.gif --name wander   # + speichern
python3 -m fertig stream video_x.gif --recognize     # gegen die Bank
```

Gelernte Streams werden VideoBank-Kategorien (data/video_bank.json) und
schreiben Struktur-Fakten in den Welt-Graphen (`hat_bewegung`,
`ist_periodisch`, `hat_szenenwechsel`) — der Stream wird Wissen.
Live getestet: „Me at the zoo" wurde als Kategorie `zoo` gelernt und
hat die Fakten `(zoo, hat_bewegung, 0.0416)` + `(zoo, ist_periodisch, 1)`
in den Graphen geschrieben.

**Sehen wird Sprache** — die VideoBank ist ein Intent-Tool:

```bash
python3 -m fertig intent -x --video data/puls.gif "erkenne dieses video"
# -> [Tool video] Das Video zeigt: puls
```

Unbekannte Videos werden ehrlich abgelehnt (Distanz über der Schwelle)
statt geraten. Stresstest: 5 Video-Arten, 10/10 ungesehene Varianten
korrekt erkannt.

## Interpolations-Lernen mit Stützrädern (fertig.interp)

```bash
python3 -m fertig interp data/puls48.gif            # Stützräder-Metrik
python3 -m fertig interp data/puls48.gif -s          # self-paced Curriculum
```

**Fahrradfahren**: Lücke k=1 (benachbarte Frames) ist fast gegeben;
mit wachsender Lücke muss das System echte Dynamik verstehen. Die
**beherrschte Lücke** (größte Lücke mit Interpolations-Fehler unter der
Schwelle) ist die Fortschritts-Metrik.

- **Kein Warp**: Interpolation im Code-Raum (gemessene Übergänge +
  Code-Prototypen) — Warp-Artefakte sind per Konstruktion unmöglich.
- **Richtungs-Bit**: Der Code trägt wächst/schrumpft — ohne es wäre er
  phasenblind und der Prototyp mittelte Anstieg+Abfall zu Unschärfe.
- **Self-paced (F1-Prinzip)**: Die eigene Surprise stellt die
  Stützräder ein — Fehler klein → Lücke wächst, Fehler groß → Lücke
  schrumpft. Live: gap-Verlauf [2,3,6,5,4,5,6,5,6,7] auf puls48.gif.
- **Ehrliche Grenzen**: wander (Translation) bleibt bei gap=2 — die
  Maschine weiß, was sie nicht kann, statt zu raten.

## Garantien des symbolischen Kerns

1. **Determinismus**: `info`, `chains`, `graph`, `speech`, `corpus` liefern bei
   gleichen Argumenten bit-identische Ausgaben (getestet).
2. **Keine erfundenen Fakten**: Im Graph-Modus stammen alle Entitäten und
   Mechanismen wörtlich aus dem `.causal`-Graphen; nur die Satzform wird
   generiert.
3. **Ehrliche Sackgassen**: Endet der Graph, endet der Walk — kein Füllsel.
4. **Kein Training im Graph-/Korpuspfad**: keine Gradienten, Embeddings oder
   Gewichte; dort gelten reines Zählen, Ziehen und gemessene Übergänge. Das
   separat ausgewiesene HSSLM ist ein trainierter Checkpoint, und der
   Desktop-Pfad lernt absichtlich lokale Task-Modelle aus Demonstrationen.

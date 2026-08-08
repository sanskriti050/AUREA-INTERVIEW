"""Deterministic local question generation and rubric-based feedback."""
from __future__ import annotations
import hashlib
import re

THEORY_TOPICS = ["Resume & Projects", "Data Structures", "DBMS & SQL", "Operating Systems", "Computer Networks", "OOP & Design", "System Design", "Behavioral"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
ROLES = ["Software Engineer", "Python Developer", "Java Developer", "Frontend Developer", "Data Analyst", "Data Scientist", "AI / ML Engineer"]

CONCEPTS = {
 "Resume & Projects": ["problem", "role", "decision", "trade-off", "result", "metric"],
 "Data Structures": ["complexity", "time", "space", "edge case", "data structure"],
 "DBMS & SQL": ["index", "transaction", "normalization", "join", "consistency"],
 "Operating Systems": ["process", "thread", "memory", "scheduling", "concurrency"],
 "Computer Networks": ["tcp", "http", "dns", "latency", "security"],
 "OOP & Design": ["encapsulation", "abstraction", "polymorphism", "interface", "composition"],
 "System Design": ["scale", "availability", "database", "cache", "trade-off"],
 "Behavioral": ["situation", "task", "action", "result", "learning"],
}

BASE = {
 "Resume & Projects": {
  "Easy": ["Walk me through one project relevant to {role}. What problem did it solve?", "Which skill on your resume are you most confident defending for a {role} role?", "What was your personal contribution to your strongest project?"],
  "Medium": ["Choose a project and explain one technical decision, an alternative, and the measured outcome.", "What failed in your strongest project, how did you diagnose it, and what changed afterward?", "If you rebuilt your resume project for ten times the users, what would you change first and why?"],
  "Hard": ["Defend the architecture of your strongest project under reliability, security and cost constraints.", "Identify a claim on your resume an expert interviewer should challenge. Prove it with evidence.", "How would you migrate your project with zero downtime while preserving data correctness?"]},
 "Data Structures": {
  "Easy": ["Compare an array and a linked list. When would you choose each as a {role}?", "Explain average and worst-case lookup in a hash table.", "When do you use a stack rather than a queue? Give a practical example."],
  "Medium": ["Design an LRU cache and justify the data structures and complexity.", "How would you detect a cycle in a directed graph? Compare two approaches.", "Find the top-k frequent items in a stream and discuss complexity."],
  "Hard": ["Design a thread-safe in-memory key-value store with expiry and explain complexity.", "How would you maintain a dynamic median under high update volume?", "Compare suffix arrays, tries and rolling hashes for large-scale substring search."]},
 "DBMS & SQL": {
  "Easy": ["Explain primary and foreign keys using a real schema.", "What is the difference between WHERE and HAVING?", "Why do databases use indexes, and what do they cost?"],
  "Medium": ["A query became slow after the table reached 50 million rows. How would you investigate?", "Explain isolation levels using a concurrent money-transfer example.", "Design a normalized schema for an interview scheduling product."],
  "Hard": ["Choose a partitioning strategy for a multi-tenant event store and defend rebalancing behavior.", "How would you prevent double booking across concurrent transactions?", "Compare optimistic and pessimistic concurrency for a high-contention workload."]},
 "Operating Systems": {
  "Easy": ["Explain process versus thread and what resources they share.", "What is virtual memory and why is it useful?", "Name the four deadlock conditions and give an example."],
  "Medium": ["Diagnose a service with high context switching but low CPU utilization.", "Compare mutexes, semaphores and condition variables.", "Explain copy-on-write and where an application benefits from it."],
  "Hard": ["Design a scheduler for mixed latency-sensitive and batch workloads.", "Explain how memory ordering can break apparently correct concurrent code.", "How would you investigate intermittent deadlock in production?"]},
 "Computer Networks": {
  "Easy": ["What happens from entering a URL until the page loads?", "Compare TCP and UDP with suitable applications.", "Explain DNS resolution and caching."],
  "Medium": ["Diagnose an API whose p99 latency is high while the median is healthy.", "Explain TLS handshake and certificate validation.", "How do retries, timeouts and idempotency interact?"],
  "Hard": ["Design resilient cross-region traffic routing during partial network failure.", "How would you distinguish packet loss, server saturation and DNS failure from telemetry?", "Explain head-of-line blocking and how HTTP/2 and HTTP/3 differ."]},
 "OOP & Design": {
  "Easy": ["Explain encapsulation, abstraction, inheritance and polymorphism with one example.", "Interface versus abstract class: how do you decide?", "Why can composition be preferable to inheritance?"],
  "Medium": ["Design an extensible notification service using SOLID principles.", "Refactor a large conditional payment flow into testable objects.", "How would you model permissions without a fragile inheritance hierarchy?"],
  "Hard": ["Design a plugin architecture that supports versioning and failure isolation.", "Critique the use of dependency injection in a small versus large codebase.", "How do you preserve invariants in a rich domain model under concurrency?"]},
 "System Design": {
  "Easy": ["What questions do you ask before designing a URL shortener?", "Explain horizontal versus vertical scaling.", "When does a cache help, and when can it hurt correctness?"],
  "Medium": ["Design a scalable interview scheduling service for one million users.", "Design a rate limiter and compare fixed window, sliding window and token bucket.", "Design a notification pipeline with retries and deduplication."],
  "Hard": ["Design a globally distributed collaborative editor and resolve conflicts.", "Design an event ingestion platform handling one million events per second.", "Design multi-region payments with auditable exactly-once business effects."]},
 "Behavioral": {
  "Easy": ["Tell me about a time you learned a new skill quickly.", "Why are you targeting a {role} position?", "Describe a contribution you are proud of."],
  "Medium": ["Tell me about a disagreement where you changed your approach based on evidence.", "Describe a missed deadline: what did you communicate and improve?", "Tell me about ambiguous requirements you turned into an outcome."],
  "Hard": ["Describe a decision that produced a poor result despite good intent. What changed in your judgment?", "Tell me about influencing a critical decision without formal authority.", "Describe an ethical or quality trade-off you refused and how you handled consequences."]},
}

ROLE_LENS = {
 "Software Engineer": "Emphasize maintainability, testing and engineering trade-offs.",
 "Python Developer": "Include Pythonic design, typing, packaging or performance where relevant.",
 "Java Developer": "Include JVM, concurrency, type design or Spring concerns where relevant.",
 "Frontend Developer": "Include browser performance, accessibility and state management where relevant.",
 "Data Analyst": "Connect the answer to SQL, metrics, data quality and stakeholder decisions.",
 "Data Scientist": "Address experimentation, leakage, statistical validity and business impact.",
 "AI / ML Engineer": "Address model quality, serving, drift, observability and responsible AI.",
}


def question_set(role: str, topic: str, difficulty: str, skills: list[str] | None = None) -> list[dict]:
    raw = BASE[topic][difficulty]
    skill = (skills or ["your strongest resume skill"])[0]
    followups = {
        "Resume & Projects": ["state the baseline", "name your ownership", "explain the implementation boundary", "quantify the outcome", "identify a risk", "describe validation", "compare an alternative", "explain stakeholder impact", "describe a failure mode", "name the data used", "explain the rollout", "describe testing", "state the constraint", "explain a trade-off", "describe collaboration", "show evidence", "describe iteration", "state what you would change", "connect it to the role", "end with a measurable lesson"],
        "Data Structures": ["state the invariant", "compare time and space", "cover empty input", "cover duplicate values", "justify the chosen structure", "explain worst-case behavior", "walk through a sample", "name an alternative", "explain why it scales", "state mutation effects", "describe memory cost", "cover boundary indices", "discuss ordering", "explain lookup behavior", "show failure handling", "consider concurrency implications", "explain testing", "state assumptions", "give a production use case", "summarize the trade-off"],
        "DBMS & SQL": ["state the schema assumption", "address data integrity", "discuss query cost", "consider concurrent writes", "name an index decision", "explain a transaction boundary", "cover NULL behavior", "compare normalization choices", "give a query-plan check", "address scale", "explain a failure case", "consider auditability", "name a consistency risk", "discuss locking", "explain a migration concern", "cover permissions", "state a test query", "consider partitioning", "give a practical example", "summarize the trade-off"],
        "Operating Systems": ["state the resource boundary", "consider scheduling", "describe synchronization", "name a failure mode", "explain memory impact", "compare alternatives", "cover contention", "describe observability", "state an assumption", "explain isolation", "consider I/O", "discuss fairness", "cover cleanup", "explain testing", "name a race risk", "consider latency", "describe recovery", "state a production example", "explain cost", "summarize the trade-off"],
        "Computer Networks": ["name the protocol layer", "consider timeout behavior", "address retries", "explain latency impact", "cover security", "discuss observability", "compare protocols", "state a failure mode", "consider caching", "explain idempotency", "cover load balancing", "name a metric", "describe packet loss handling", "consider TLS", "explain DNS impact", "state assumptions", "cover a regional failure", "give a practical example", "explain a trade-off", "summarize mitigation"],
        "OOP & Design": ["state the interface boundary", "explain extensibility", "consider testability", "name an invariant", "compare composition", "address coupling", "show error handling", "describe ownership", "consider versioning", "explain a trade-off", "state a design pattern only if justified", "cover validation", "consider concurrency", "name a failure mode", "explain dependency direction", "describe testing", "state an alternative", "give a practical example", "address maintainability", "summarize the decision"],
        "System Design": ["state assumptions and scale", "define the API boundary", "address availability", "consider consistency", "name the data model", "explain caching", "cover failure recovery", "describe observability", "consider rate limits", "explain capacity", "address security", "name a bottleneck", "consider multi-region behavior", "explain a trade-off", "cover asynchronous work", "describe rollout", "state SLOs", "consider cost", "give an edge case", "summarize the design"],
        "Behavioral": ["use a specific situation", "name your personal action", "quantify the result", "explain a decision", "describe feedback", "name a constraint", "show collaboration", "explain a trade-off", "state what changed", "describe communication", "show ownership", "explain prioritization", "name a failure", "state a learning", "describe conflict resolution", "show ethical judgment", "give evidence", "explain the outcome", "connect it to the role", "close with a lesson"],
    }[topic]
    seed = int(hashlib.sha256(f"{role}|{topic}|{difficulty}|{skill}".encode()).hexdigest()[:8], 16)
    out = []
    for n, followup in enumerate(followups):
        base = raw[(seed + n * 7) % len(raw)].format(role=role)
        prompt = f"{base} As a {role}, {followup}; relate it to {skill} when relevant."
        out.append({"id": f"{topic}|{difficulty}|{n + 1}", "question": prompt, "lens": ROLE_LENS[role], "concepts": CONCEPTS[topic]})
    return out


def _reference_answer(topic: str, difficulty: str, question: str) -> dict:
    answers = {
      "Data Structures": ("Choose the structure from the operations that dominate. State the invariant, then justify time and space costs.", ["Name the data structure and its invariant.", "Walk through one small example, including an edge case.", "Give average and worst-case time/space and an alternative."], "For example, an LRU cache combines a hash map for O(1) lookup with a doubly linked list for O(1) recency updates.", "Mention collisions, empty input, duplicates, or concurrent access when relevant."),
      "DBMS & SQL": ("Start with correctness: schema, constraints and transaction boundary; then discuss the query plan and scale trade-off.", ["State assumptions about keys, NULLs and data volume.", "Explain integrity/concurrency protection before optimisation.", "Use EXPLAIN, indexes and measured latency to validate the choice."], "For a slow query, reproduce it with representative data, inspect EXPLAIN ANALYZE, verify selectivity and indexes.", "Indexes speed reads but add write/storage cost; isolation protects correctness but can reduce concurrency."),
      "Operating Systems": ("Separate the resource boundary from the scheduling and synchronization decision, then name the failure mode.", ["Define the OS concept precisely.", "Explain who owns memory, files and execution state.", "Describe contention, cleanup and one observable metric."], "A process has its own virtual address space; threads share a process address space while each keeps its own stack.", "Call out races, deadlock, starvation, context-switch overhead or memory pressure where appropriate."),
      "Computer Networks": ("Trace the request path, identify the layer and failure signal, then explain the reliability trade-off.", ["Name protocol/layer and expected behavior.", "State timeout, retry and idempotency behavior.", "Use latency, loss, error and saturation metrics to distinguish causes."], "For a URL load: DNS resolves the name, TCP connection is established, HTTP is sent, browser renders resources.", "Retries without idempotency can duplicate effects; timeouts must have bounded budgets."),
      "OOP & Design": ("Define the interface and invariants first. Prefer composition when behavior should vary independently of the type hierarchy.", ["State responsibilities and public contract.", "Keep dependencies pointing toward stable abstractions.", "Explain testability, extension point and one rejected alternative."], "For an extensible notification service, define a NotificationChannel interface, implement adapters, inject dependencies.", "Avoid inheritance used only for code reuse; protect invariants through encapsulation and validation."),
      "System Design": ("Begin with requirements and scale assumptions, then present the data flow, storage choice, failure handling and a conscious consistency trade-off.", ["State functional and non-functional requirements.", "Estimate traffic/storage and identify the bottleneck.", "Cover API, data model, cache/queue, observability and failure recovery."], "A sound design partitions stateless services behind a load balancer, uses durable storage as the source of truth.", "Name SLOs and explain the availability/consistency/cost trade-off rather than claiming every property at once."),
      "Behavioral": ("Use a truthful STAR story with most detail on your personal actions, the measurable outcome and what you learned.", ["Situation and task: set a concise context.", "Action: explain what you personally decided and did.", "Result: quantify impact and close with a lesson relevant to the role."], "Example: 'Our release was slipping. I proposed a smaller milestone, aligned stakeholders daily, and added a visible risk log.'", "Do not invent achievements; select a real project and be specific about ownership."),
      "Resume & Projects": ("Use evidence from your real project: problem, your ownership, decision, measurable result and what you would improve.", ["State the user/problem and baseline.", "Separate your contribution from the team's work.", "Explain one decision, alternative, result and limitation."], "Example: 'The problem was X. I owned Y. I chose Z because of this constraint, rejected A, and measured B.'", "Only claim metrics and technologies you can defend with concrete evidence."),
    }
    direct, points, example, caveat = answers[topic]
    if difficulty == "Hard":
        points.append("State assumptions, failure modes and why the chosen alternative is acceptable.")
    elif difficulty == "Medium":
        points.append("Compare one practical alternative and explain the trade-off.")
    return {"direct_answer": direct, "key_points": points, "example": example, "caveat": caveat, "for_question": question}


def evaluate_theory(answer: str, topic: str, difficulty: str, question: str) -> dict:
    text = answer.strip()
    reference = _reference_answer(topic, difficulty, question)
    words = re.findall(r"\b[\w+#.-]+\b", text.lower())
    if not words:
        return {"score": 0, "verdict": "No answer yet", "strengths": [], "gaps": ["A complete answer is required."], "tips": ["Start with a one-sentence direct answer, then explain and illustrate it."], "sample": "Use: direct claim → reasoning/trade-off → concrete example → concise conclusion.", "model_answer": reference}
    expected = CONCEPTS[topic]
    hits = [x for x in expected if x in text.lower()]
    structure = sum(bool(re.search(p, text.lower())) for p in [r"for example|for instance|in my", r"because|therefore|so that", r"however|trade-?off|whereas", r"result|outcome|impact"])
    length_target = {"Easy": 70, "Medium": 120, "Hard": 170}[difficulty]
    score = min(94, round(18 + 35 * min(len(words), length_target) / length_target + 32 * len(hits) / len(expected) + 4 * structure))
    strengths = []
    if len(words) >= length_target * .65: strengths.append("The answer has enough substance to assess.")
    if hits: strengths.append("Relevant concepts used: " + ", ".join(hits) + ".")
    if structure >= 2: strengths.append("Reasoning includes evidence, causality or trade-offs.")
    gaps = []
    missing = [x for x in expected if x not in hits]
    if missing: gaps.append("Make these concepts explicit where relevant: " + ", ".join(missing[:3]) + ".")
    if len(words) < length_target * .55: gaps.append(f"Too brief for {difficulty.lower()} depth; target roughly {length_target} focused words.")
    if structure < 2: gaps.append("Add a concrete example and explain the decision/trade-off, not only definitions.")
    tips = ["Lead with the direct answer in one sentence.", "Use a named example, boundary condition or metric."]
    if topic == "Behavioral": tips.append("Use STAR, but spend most time on your actions and quantified result.")
    elif difficulty == "Hard": tips.append("State assumptions, failure modes and why an alternative was rejected.")
    else: tips.append("Close with complexity, risk or practical implication as appropriate.")
    sample = f"A stronger response to '{question[:80]}…' would follow: direct position → define {expected[0]} → explain {expected[1]} → give a concrete example → discuss {expected[-1]} and a trade-off."
    verdict = "Interview-ready" if score >= 75 else "Promising, needs depth" if score >= 55 else "Needs a clearer, more complete answer"
    return {"score": score, "verdict": verdict, "strengths": strengths or ["You attempted the question directly."], "gaps": gaps or ["Polish concision and delivery under a timer."], "tips": tips, "sample": sample, "model_answer": reference}


def answer_guide(topic: str, difficulty: str, question: str) -> dict:
    reference = _reference_answer(topic, difficulty, question)
    level_note = {"Easy": "Keep the delivery clear and about 60–90 seconds.", "Medium": "Aim for a structured 90–120 second explanation with one justified alternative.", "Hard": "Start by stating assumptions, then defend trade-offs, risks and failure handling in roughly two minutes."}[difficulty]
    model = (f"For this question, begin by framing the decision directly: {reference['direct_answer']} Then make the answer concrete. {reference['example']} Finally, show mature judgment: {reference['caveat']}")
    return {**reference, "question": question, "writing_formula": "Direct answer → explanation → concrete example → trade-off → conclusion", "delivery_note": level_note, "model_response": model}

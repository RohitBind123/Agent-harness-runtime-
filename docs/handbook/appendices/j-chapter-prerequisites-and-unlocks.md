# Appendix J — Chapter Prerequisites and Unlocks

> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.

The dependency spine as a flat table, taken from the header block of every chapter. `Requires` names chapters that must precede; `Unlocks` names chapters that build on this one. The linter enforces the direction of both, so a cycle is not expressible.

50 chapters across 6 levels.

---

## The spine

| Chapter | Title | Level | Tier | Requires | Unlocks |
|---|---|---:|---|---|---|
| [Ch 0](../chapters/00-evolution-of-ai-systems.md) | Evolution of AI Systems | 0 | Light | nothing | C1 Anatomy of an Agent, C2 Why a Runtime Is a Distributed System, C3 Mental Models and the Reference System |
| [Ch 1](../chapters/01-anatomy-of-an-agent.md) | Anatomy of an Agent: Model, Harness, Environment | 0 | Light | C0 Evolution of AI Systems | C2 Why a Runtime Is a Distributed System, C3 Mental Models, C14 Tool Execution Engine, C43 Component Observability |
| [Ch 2](../chapters/02-why-an-agent-runtime-is-a-distributed-system.md) | Why an Agent Runtime Is a Distributed System | 0 | Light | C0 Evolution of AI Systems, C1 Anatomy of an Agent | C3 Mental Models, and all of Level 1 |
| [Ch 3](../chapters/03-mental-models-and-reference-system.md) | Mental Models and the Reference System | 0 | Light | C0 Evolution of AI Systems, C1 Anatomy of an Agent, C2 Why a Runtime Is a Distributed System | all of Level 1; the reference system is used in every later chapter |
| [Ch 4](../chapters/04-complete-runtime-layers-and-process-topology.md) | The Complete Runtime: Layers and Process Topology | 1 | Full | C0-C3 (all of Level 0) | C5 Five Nouns, C6 State Separation, C7 The Edge, C8 Lifecycles, C9 Three Flows — and every chapter after |
| [Ch 5](../chapters/05-five-nouns.md) | The Five Nouns: Run, Episode, Step, Activity, Park | 1 | Core | C4 The Complete Runtime | C6 State Separation, C8 Lifecycles, C17 State Manager, C18 The Runtime Loop, C21 Durable Execution |
| [Ch 6](../chapters/06-state-separation.md) | State Separation: Run, Domain, Model — and Harness | 1 | Core | C4 The Complete Runtime, C5 The Five Nouns | C7 The Edge, C11 Context, C12 Memory, C17 State Manager, C21 Durable Execution, C32 Distributed Execution, C37 Tenancy, C47 Attribution |
| [Ch 7](../chapters/07-edge-and-client-contract.md) | The Edge and the Client Contract | 1 | Core | C4 The Complete Runtime, C5 The Five Nouns, C6 State Separation | C8 Lifecycles, C9 Three Flows, C30 Human Authority, C34 Observability, C37 Tenancy |
| [Ch 8](../chapters/08-request-and-runtime-lifecycles.md) | Request Lifecycle and Runtime Lifecycle | 1 | Core | C4 The Complete Runtime, C5 The Five Nouns, C6 State Separation, C7 The Edge | C9 Three Flows, C17 State Manager, C18 The Runtime Loop, C27 Failure and Recovery, C38 Deployment |
| [Ch 9](../chapters/09-three-flows-data-control-event.md) | Three Flows: Data, Control, Event | 1 | Core | C4 The Complete Runtime, C5 The Five Nouns, C6 State Separation, C7 The Edge, C8 Lifecycles | all of Level 2; C22 The Event Spine, C34 Observability, C35 Cost Engineering |
| [Ch 10](../chapters/10-the-planner.md) | The Planner | 2 | Full | C5 The Five Nouns, C6 State Separation, C8 Lifecycles, C9 Three Flows | C21 Durable Execution, C24 The Task Graph, C26 Planning Algorithms, C30 Human Authority |
| [Ch 11](../chapters/11-the-context-system.md) | The Context System | 2 | Full | C6 State Separation, C9 Three Flows, C10 The Planner | C12 The Memory System, C13 The Reasoning Engine, C18 The Runtime Loop, C35 Cost Engineering, C44 Experience Observability |
| [Ch 12](../chapters/12-the-memory-system.md) | The Memory System | 2 | Full | C6 State Separation, C10 The Planner, C11 The Context System | C16 The Observation System, C25 The World Model, C37 Tenancy and Data Governance, C43 Component Observability, C46 The Evolve Agent |
| [Ch 13](../chapters/13-the-reasoning-engine.md) | The Reasoning Engine | 2 | Full | C6 State Separation, C9 Three Flows, C11 The Context System | C14 The Tool Execution Engine, C18 The Runtime Loop, C21 Durable Execution, C35 Cost Engineering, C38 Deployment and Versioning |
| [Ch 14](../chapters/14-the-tool-execution-engine.md) | The Tool Execution Engine | 2 | Full | C9 Three Flows, C10 The Planner, C11 The Context System, C13 The Reasoning Engine | C15 Agent-Computer Interface Design, C18 The Runtime Loop, C21 Durable Execution, C30 Human Authority, C31 Safety and Sandboxing, C46 The Evolve Agent |
| [Ch 15](../chapters/15-agent-computer-interface-design.md) | Agent-Computer Interface Design | 2 | Full | C13 Reasoning Engine, C14 Tool Execution Engine | C44 Agent Debugger, C46 Evolve Agent |
| [Ch 16](../chapters/16-the-observation-system.md) | The Observation System | 2 | Full | C9 Three Flows, C11 The Context System, C13 The Reasoning Engine, C14 The Tool Execution Engine, C15 Agent-Computer Interface Design | C34 Observability, C37 Tenancy and Data Governance, C40 Testing, C41 Evaluation Infrastructure, C44 Experience Observability |
| [Ch 17](../chapters/17-the-state-manager.md) | The State Manager | 2 | Full | C5 The Five Nouns, C6 State Separation, C8 Lifecycles, C9 Three Flows | C18 The Runtime Loop, C21 Durable Execution, C23 The Scheduler, C27 Failure and Recovery, C32 Distributed Execution |
| [Ch 18](../chapters/18-the-runtime-loop.md) | The Runtime Loop | 2 | Full | C5 The Five Nouns, C8 Lifecycles, C10 The Planner, C13 The Reasoning Engine, C14 The Tool Execution Engine, C17 The State Manager | C21 Durable Execution, C23 The Scheduler, C29 Long-Running Agents, C33 Scalability, C35 Cost Engineering |
| [Ch 19](../chapters/19-the-multi-agent-runtime.md) | The Multi-Agent Runtime | 2 | Full | C11 The Context System, C14 The Tool Execution Engine, C16 The Observation System, C18 The Runtime Loop | C24 The Task Graph, C29 Long-Running Agents, C31 Safety and Sandboxing, C44 Experience Observability |
| [Ch 20](../chapters/20-the-self-evolving-runtime-overview.md) | The Self-Evolving Runtime (AHE) — Overview | 2 | Full | C14 The Tool Execution Engine, C15 ACI Design, C16 The Observation System, C18 The Runtime Loop, C19 The Multi-Agent Runtime | C34 Observability, C39 GitOps, C41 Evaluation Infrastructure, and all of Level 5 |
| [Ch 21](../chapters/21-durable-execution.md) | Durable Execution | 3 | Full | C5 The Five Nouns, C8 Lifecycles, C14 The Tool Execution Engine, C17 The State Manager, C18 The Runtime Loop | C27 Failure and Recovery, C32 Distributed Execution, C40 Testing, C47 Attribution |
| [Ch 22](../chapters/22-the-event-spine.md) | The Event Spine: Outbox, Relay, Command Port | 3 | Full | C4 The Complete Runtime, C9 Three Flows, C17 The State Manager, C21 Durable Execution | C24 The Task Graph, C27 Failure and Recovery, C30 Human Authority, C32 Distributed Execution, C34 Observability |
| [Ch 23](../chapters/23-the-scheduler.md) | The Scheduler: Queues, Work Classes, Admission | 3 | Full | C17 The State Manager, C18 The Runtime Loop, C21 Durable Execution, C22 The Event Spine | C29 Long-Running Agents, C33 Scalability, C36 Reliability and SLOs, C37 Tenancy |
| [Ch 24](../chapters/24-the-task-graph.md) | The Task Graph | 3 | Core | C10 The Planner, C17 The State Manager, C18 The Runtime Loop, C21 Durable Execution, C22 The Event Spine | C26 Planning Algorithms, C27 Failure and Rollback, C29 Long-Running Agents, C32 Distributed Execution |
| [Ch 25](../chapters/25-the-world-model.md) | The World Model | 3 | Core | C11 The Context System, C12 The Memory System, C14 The Tool Execution Engine, C22 The Event Spine, C24 The Task Graph | C26 Planning Algorithms, C31 Safety and Sandboxing, C34 Observability |
| [Ch 26](../chapters/26-planning-algorithms.md) | Planning Algorithms | 3 | Core | C10 The Planner, C13 The Reasoning Engine, C24 The Task Graph, C25 The World Model | C27 Failure and Rollback, C28 Grading, C30 Human Authority, C41 Evaluation Infrastructure |
| [Ch 27](../chapters/27-failure-recovery-and-rollback.md) | Failure, Recovery, and Rollback | 3 | Core | C14 The Tool Execution Engine, C17 The State Manager, C21 Durable Execution, C24 The Task Graph, C26 Planning Algorithms | C30 Human Authority, C31 Safety and Sandboxing, C39 GitOps and CI/CD, C47 Rollback of Harness Edits |
| [Ch 28](../chapters/28-reflection-grading-and-self-correction.md) | Reflection, Grading, and Self-Correction | 3 | Core | C13 The Reasoning Engine, C16 The Observation System, C24 The Task Graph, C26 Planning Algorithms | C41 Evaluation Infrastructure, C44 The Evolve Agent, C46 Reward Design |
| [Ch 29](../chapters/29-long-running-agents.md) | Long-Running Agents | 3 | Core | C8 Request and Runtime Lifecycles, C11 The Context System, C21 Durable Execution, C24 The Task Graph, C26 Planning Algorithms | C33 Scalability, C35 Cost Engineering, C36 Reliability and SLOs |
| [Ch 30](../chapters/30-human-authority.md) | Human Authority | 3 | Full | C10 The Planner, C14 The Tool Execution Engine, C17 The State Manager, C27 Failure and Rollback, C29 Long-Running Agents | C31 Safety and Sandboxing, C36 Reliability and SLOs, C43 The Evolution Loop, C48 Governance |
| [Ch 31](../chapters/31-safety-sandboxing-and-untrusted-content.md) | Safety, Sandboxing, and Untrusted Content | 3 | Core | C14 The Tool Execution Engine, C16 The Observation System, C27 Failure and Rollback, C30 Human Authority | C37 Tenancy and Data Governance, C43 The Evolution Loop, C48 Governance |
| [Ch 32](../chapters/32-distributed-execution.md) | Distributed Execution | 3 | Full | C17 The State Manager, C21 Durable Execution, C22 The Event Spine, C23 The Scheduler, C24 The Task Graph | C33 Scalability, C34 Observability, C36 Reliability and SLOs |
| [Ch 33](../chapters/33-scalability-and-capacity-planning.md) | Scalability and Capacity Planning | 4 | Core | C23 The Scheduler, C29 Long-Running Agents, C32 Distributed Execution | C35 Cost Engineering, C36 Reliability and SLOs, C41 Evaluation Infrastructure |
| [Ch 34](../chapters/34-observability.md) | Observability | 4 | Core | C9 Three Flows, C16 The Observation System, C21 Durable Execution, C33 Scalability | C36 Reliability and SLOs, C37 Tenancy and Governance, C41 Evaluation Infrastructure |
| [Ch 35](../chapters/35-cost-engineering-and-token-economics.md) | Cost Engineering and Token Economics | 4 | Core | C11 The Context System, C13 The Reasoning Engine, C28 Grading, C33 Scalability | C36 Reliability and SLOs, C41 Evaluation Infrastructure, C46 Reward Design |
| [Ch 36](../chapters/36-reliability-and-slos.md) | Reliability and SLOs | 4 | Core | C27 Failure and Rollback, C28 Grading, C34 Observability, C35 Cost Engineering | C41 Evaluation Infrastructure, C48 Governance |
| [Ch 37](../chapters/37-tenancy-secrets-and-data-governance.md) | Tenancy, Secrets, and Data Governance | 4 | Core | C12 The Memory System, C16 The Observation System, C25 The World Model, C31 Safety and Sandboxing, C34 Observability | C41 Evaluation Infrastructure, C44 The Evolve Agent, C48 Governance |
| [Ch 38](../chapters/38-deployment-versioning-and-configuration.md) | Deployment, Versioning, and Configuration | 4 | Core | C11 The Context System, C29 Long-Running Agents, C33 Scalability, C35 Cost Engineering | C39 GitOps and CI/CD, C41 Evaluation Infrastructure, C47 Attribution and Rollback |
| [Ch 39](../chapters/39-gitops-and-cicd-for-agent-systems.md) | GitOps and CI/CD for Agent Systems | 4 | Core | C27 Failure and Rollback, C28 Grading, C38 Deployment and Versioning | C40 Testing, C41 Evaluation Infrastructure, C47 Attribution and Rollback |
| [Ch 40](../chapters/40-testing-a-non-deterministic-system.md) | Testing a Non-Deterministic System | 4 | Core | C13 The Reasoning Engine, C21 Durable Execution, C32 Distributed Execution, C34 Observability, C39 GitOps and CI/CD | C41 Evaluation Infrastructure, C47 Attribution and Rollback |
| [Ch 41](../chapters/41-evaluation-infrastructure.md) | Evaluation Infrastructure | 4 | Core | C28 Grading, C34 Observability, C36 Reliability and SLOs, C38 Deployment and Versioning, C39 GitOps and CI/CD, C40 Testing | all of Level 5 |
| [Ch 42](../chapters/42-the-case-for-harness-evolution.md) | The Case for Harness Evolution | 5 | Core | C20 The Self-Evolving Runtime (Overview), C38 Deployment and Versioning, C41 Evaluation Infrastructure | C43 Component Observability, C46 The Evolve Agent, C49 Continuous Improvement and Governance |
| [Ch 43](../chapters/43-component-observability.md) | Component Observability | 5 | Full | C1 Anatomy of an Agent, C14 The Tool Execution Engine, C39 GitOps and CI/CD, C42 The Case for Harness Evolution | C44 Experience Observability, C45 Decision Observability, C46 The Evolve Agent |
| [Ch 44](../chapters/44-experience-observability.md) | Experience Observability | 5 | Full | C11 The Context System, C16 The Observation System, C34 Observability, C37 Tenancy and Data Governance, C43 Component Observability | C45 Decision Observability, C46 The Evolve Agent, C47 Attribution and Rollback |
| [Ch 45](../chapters/45-decision-observability.md) | Decision Observability | 5 | Full | C20 The Self-Evolving Runtime (Overview), C26 Planning Algorithms, C41 Evaluation Infrastructure, C43 Component Observability, C44 Experience Observability | C46 The Evolve Agent, C47 Attribution and Rollback, C49 Continuous Improvement and Governance |
| [Ch 46](../chapters/46-the-evolve-agent.md) | The Evolve Agent | 5 | Full | C30 Human Authority, C43 Component Observability, C44 Experience Observability, C45 Decision Observability | C47 Attribution and Rollback, C48 Limits, C49 Continuous Improvement and Governance |
| [Ch 47](../chapters/47-attribution-verdicts-and-rollback.md) | Attribution, Verdicts, and Rollback | 5 | Core | C27 Failure, Recovery, and Rollback, C40 Testing, C41 Evaluation Infrastructure, C45 Decision Observability, C46 The Evolve Agent | C48 Limits, C49 Continuous Improvement and Governance |
| [Ch 48](../chapters/48-limits.md) | Limits | 5 | Core | C31 Safety and Sandboxing, C41 Evaluation Infrastructure, C46 The Evolve Agent, C47 Attribution, Verdicts, and Rollback | C49 Continuous Improvement and Governance |
| [Ch 49](../chapters/49-continuous-improvement-and-governance.md) | Continuous Improvement and Governance | 5 | Core | C30 Human Authority, C37 Tenancy, Secrets, and Data Governance, C46 The Evolve Agent, C48 Limits | -- the book ends here |

---

## Load-bearing chapters

Ranked by how many later chapters declare them a prerequisite. These are the chapters a reader cannot skip, and the ones an edit is most expensive in.

| Chapter | Title | Required by | Which |
|---|---|---:|---|
| Ch 14 | The Tool Execution Engine | 11 | Ch 15, Ch 16, Ch 18, Ch 19, Ch 20, Ch 21, Ch 25, Ch 27, Ch 30, Ch 31, Ch 43 |
| Ch 11 | The Context System | 10 | Ch 12, Ch 13, Ch 14, Ch 16, Ch 19, Ch 25, Ch 29, Ch 35, Ch 38, Ch 44 |
| Ch 21 | Durable Execution | 8 | Ch 22, Ch 23, Ch 24, Ch 27, Ch 29, Ch 32, Ch 34, Ch 40 |
| Ch 17 | The State Manager | 8 | Ch 18, Ch 21, Ch 22, Ch 23, Ch 24, Ch 27, Ch 30, Ch 32 |
| Ch 13 | The Reasoning Engine | 8 | Ch 14, Ch 15, Ch 16, Ch 18, Ch 26, Ch 28, Ch 35, Ch 40 |
| Ch 9 | Three Flows: Data, Control, Event | 8 | Ch 10, Ch 11, Ch 13, Ch 14, Ch 16, Ch 17, Ch 22, Ch 34 |
| Ch 6 | State Separation: Run, Domain, Model — and Harness | 8 | Ch 7, Ch 8, Ch 9, Ch 10, Ch 11, Ch 12, Ch 13, Ch 17 |
| Ch 5 | The Five Nouns: Run, Episode, Step, Activity, Park | 8 | Ch 6, Ch 7, Ch 8, Ch 9, Ch 10, Ch 17, Ch 18, Ch 21 |
| Ch 16 | The Observation System | 7 | Ch 19, Ch 20, Ch 28, Ch 31, Ch 34, Ch 37, Ch 44 |
| Ch 10 | The Planner | 7 | Ch 11, Ch 12, Ch 14, Ch 18, Ch 24, Ch 26, Ch 30 |
| Ch 24 | The Task Graph | 6 | Ch 25, Ch 26, Ch 27, Ch 28, Ch 29, Ch 32 |
| Ch 8 | Request Lifecycle and Runtime Lifecycle | 6 | Ch 9, Ch 10, Ch 17, Ch 18, Ch 21, Ch 29 |

---

## Entry points

Chapters that declare no prerequisite, and can therefore be read first:

- (none)

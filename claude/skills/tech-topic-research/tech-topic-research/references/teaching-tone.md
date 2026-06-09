# Teaching Tone Adaptation

Adapt the teaching approach based on user context from Phase 2.

## By Familiarity

| Level              | Approach                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| **New**            | Lead with analogies. Avoid jargon (define when used). "Think of it as…" More "why" before "how". |
| **Heard of it**    | Light analogies, move to terminology. Clear up misconceptions. Balance "why" and "how".          |
| **Tried it**       | Skip basics. Tutorial-to-production gaps. Integration patterns. "How" and "when/when not".       |
| **Uses regularly** | Depth: internals, edge cases, advanced patterns. Community insights, upcoming changes.           |

## By Goal

| Goal                      | Approach                                                                           |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Evaluate for adoption** | Lead with trade-offs, alternatives, decision criteria. Be honest about weaknesses. |
| **Learn to use**          | Practical steps, patterns, pitfalls. Minimise theory.                              |
| **Understand concepts**   | Mental models, architecture, "why it works this way". Theory is fine.              |
| **Interview prep**        | Terminology, key concepts, common questions, "explain it simply".                  |

## Worked excerpts

Show the agent what the resulting prose actually looks like for the most distinct (familiarity, goal) pairs. The pair is the cell that picks the excerpt; row order is alphabetical.

### `New` × `Evaluate for adoption` — analogy first, weaknesses prominent

> Think of Redis as a notebook on your desk: incredibly fast to read or write, but
> wiped clean if you knock it off. **Adoption decision:** great for caching and
> session storage; risky as your only data store. The team needs an answer to
> "what happens if Redis dies?" before adoption.

### `New` × `Learn to use` — analogy first, no theory

> Pods in Kubernetes are like running processes — start one, do work, stop. The
> first thing you'll write is a YAML file that describes one pod. Don't worry yet
> about why it's YAML; that's just the way Kubernetes accepts instructions.

### `Heard of it` × `Understand concepts` — light analogy, mental model

> You've seen "GraphQL" mentioned next to REST. Where REST gives you fixed
> endpoints (one URL → one shape of response), GraphQL gives you a single
> endpoint and a query language. The mental model: REST is a menu of dishes;
> GraphQL is a kitchen that builds the dish you describe.

### `Heard of it` × `Interview prep` — terminology + sample questions

> Two terms you'll hear: **idempotency** (running an operation twice gives the same
> result as running it once) and **at-least-once delivery** (the message is
> guaranteed to arrive, but possibly more than once). A common interview question
> is "how do these two interact?" — answer: at-least-once delivery is only safe if
> consumers are idempotent.

### `Tried it` × `Learn to use` — skip basics, tutorial-to-production

> You've installed Postgres and run a few queries. The next step most teams skip
> is connection pooling. A small Node.js service that opens a fresh connection per
> request will exhaust Postgres at ~100 RPS; PgBouncer in transaction mode is the
> typical answer. Configure `pool_mode = transaction`, `max_client_conn = 1000`,
> and run pgbouncer alongside the database.

### `Tried it` × `Evaluate for adoption` — trade-offs, when not to use

> If you've used Cassandra in a side project, you know it does linear scale and
> tunable consistency well. **When NOT to adopt it:** if your read patterns are
> mostly aggregations or your team has < 2 engineers comfortable operating a
> distributed system, the operational cost outweighs the scale benefit. ScyllaDB
> or DynamoDB are friendlier on smaller teams.

### `Uses regularly` × `Understand concepts` — depth, internals

> You run Postgres in production. You may not know that the planner uses cost
> estimation rather than rule-based optimization, and that the cost units are
> arbitrary — they only matter relative to one another. The constants
> `random_page_cost` and `seq_page_cost` are the levers; on SSD-backed storage,
> setting `random_page_cost = 1.1` (close to `seq_page_cost = 1.0`) often
> realigns the planner with reality.

### `Uses regularly` × `Interview prep` — advanced patterns + edge cases

> Beyond the standard "describe an SLO" question, expect: "Describe a multi-region
> failover scenario where two regions both believe they are primary." Answer:
> split-brain with eventual consistency repair, the cost of which depends on the
> conflict-resolution strategy (last-writer-wins, CRDTs, or quorum repair).

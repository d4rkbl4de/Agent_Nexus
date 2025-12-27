agent_nexus_frontend/
│
├── README.md
├── package.json
├── package-lock.json
├── tsconfig.json
├── next.config.mjs
├── .eslintrc.json
├── tailwind.config.ts
├── postcss.config.mjs
├── .env.example
│
├── public/
│   ├── icons/
│   │   ├── agent.svg
│   │   ├── brain.svg
│   │   ├── command.svg
│   │   ├── memory.svg
│   │   ├── warning.svg
│   │   └── success.svg
│   ├── logos/
│   │   ├── nexus-mark.svg
│   │   ├── nexus-wordmark.svg
│   │   └── nexus-mono.svg
│   ├── agents/
│   │   ├── chatbuddy.png
│   │   ├── insightmate.png
│   │   ├── studyflow.png
│   │   └── autoagent.png
│   ├── illustrations/
│   │   ├── empty-state.svg
│   │   ├── loading.svg
│   │   └── error.svg
│   ├── backgrounds/
│   │   ├── grid.png
│   │   ├── noise.png
│   │   └── gradient.webp
│   ├── sounds/
│   │   ├── notify.wav
│   │   ├── error.wav
│   │   └── success.wav
│   └── shaders/
│       ├── glow.glsl
│       ├── distortion.glsl
│       └── scanline.glsl
│
├── .storybook/
│   ├── main.ts
│   ├── preview.ts
│   ├── theme.ts
│   ├── decorators.ts
│   └── stories/
│       ├── ui/
│       │   ├── Button.stories.tsx
│       │   ├── Input.stories.tsx
│       │   ├── Modal.stories.tsx
│       │   └── Tooltip.stories.tsx
│       ├── motion/
│       │   ├── Fade.stories.tsx
│       │   ├── Slide.stories.tsx
│       │   └── Scale.stories.tsx
│       ├── visualization/
│       │   ├── TokenStream.stories.tsx
│       │   ├── EventTimeline.stories.tsx
│       │   └── AgentGraph.stories.tsx
│       └── shell/
│           ├── Sidebar.stories.tsx
│           ├── Header.stories.tsx
│           └── CommandPalette.stories.tsx
│
├── src/
│
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── callback/page.tsx
│   │   ├── (lobes)/
│   │   │   ├── chat/page.tsx
│   │   │   ├── insightmate/page.tsx
│   │   │   ├── studyflow/page.tsx
│   │   │   └── autoagent/page.tsx
│   │   ├── (dashboards)/
│   │   │   ├── agent/page.tsx
│   │   │   ├── system/page.tsx
│   │   │   └── performance/page.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── middleware.ts
│   │   └── globals.css
│
│   ├── shell/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── navigation/
│   │   │   ├── NavTree.tsx
│   │   │   ├── NavItem.tsx
│   │   │   └── routes.ts
│   │   ├── commands/
│   │   │   ├── CommandPalette.tsx
│   │   │   ├── command.contract.ts
│   │   │   └── command.registry.ts
│   │   ├── notifications/
│   │   │   ├── NotificationCenter.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── notification.contract.ts
│   │   │   └── sounds.ts
│   │   └── index.ts
│
│   ├── design-system/
│   │   ├── tokens/
│   │   │   ├── colors.ts
│   │   │   ├── spacing.ts
│   │   │   ├── typography.ts
│   │   │   └── radii.ts
│   │   ├── themes/
│   │   │   ├── dark.ts
│   │   │   ├── light.ts
│   │   │   └── system.ts
│   │   ├── layouts/
│   │   │   ├── Stack.tsx
│   │   │   ├── Grid.tsx
│   │   │   └── Panel.tsx
│   │   ├── icons/
│   │   │   ├── Icon.tsx
│   │   │   └── registry.ts
│   │   └── index.ts
│
│   ├── motion/
│   │   ├── tokens/
│   │   │   ├── easing.ts
│   │   │   ├── duration.ts
│   │   │   └── spring.ts
│   │   ├── primitives/
│   │   │   ├── Fade.tsx
│   │   │   ├── Slide.tsx
│   │   │   └── Scale.tsx
│   │   ├── orchestration/
│   │   │   ├── MotionTimeline.ts
│   │   │   └── MotionSequence.ts
│   │   ├── hooks/
│   │   │   ├── useMotion.ts
│   │   │   └── useReducedMotion.ts
│   │   ├── performance/
│   │   │   ├── frameBudget.ts
│   │   │   └── scheduler.ts
│   │   └── index.ts
│
│   ├── visualization/
│   │   ├── charts/
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   └── Heatmap.tsx
│   │   ├── timelines/
│   │   │   ├── EventTimeline.tsx
│   │   │   └── ExecutionTimeline.tsx
│   │   ├── streams/
│   │   │   ├── TokenStream.tsx
│   │   │   ├── ThoughtStream.tsx
│   │   │   └── LogStream.tsx
│   │   ├── graphs/
│   │   │   ├── AgentGraph.tsx
│   │   │   └── DependencyGraph.tsx
│   │   ├── renderers/
│   │   │   ├── CanvasRenderer.tsx
│   │   │   └── WebGLRenderer.tsx
│   │   └── index.ts
│
│   ├── dashboards/
│   │   ├── agent/
│   │   │   ├── AgentOverview.tsx
│   │   │   ├── AgentMemory.tsx
│   │   │   └── AgentReasoning.tsx
│   │   ├── system/
│   │   │   ├── HealthPanel.tsx
│   │   │   ├── QueuePanel.tsx
│   │   │   └── DatabasePanel.tsx
│   │   └── performance/
│   │       ├── LatencyPanel.tsx
│   │       ├── ThroughputPanel.tsx
│   │       └── CostPanel.tsx
│
│   ├── introspection/
│   │   ├── identity/AgentIdentity.tsx
│   │   ├── state/AgentState.tsx
│   │   ├── memory/MemoryInspector.tsx
│   │   ├── reasoning/ReasoningTrace.tsx
│   │   ├── execution/ExecutionTrace.tsx
│   │   ├── failures/FailureLog.tsx
│   │   └── index.ts
│
│   ├── contracts/
│   │   ├── shared/
│   │   │   ├── meta.contract.ts
│   │   │   ├── pagination.contract.ts
│   │   │   └── temporal.contract.ts
│   │   ├── agent.contract.ts
│   │   ├── chat.contract.ts
│   │   ├── insight.contract.ts
│   │   ├── study.contract.ts
│   │   └── user.contract.ts
│
│   ├── core/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── endpoints.ts
│   │   │   └── errors.ts
│   │   ├── mediator/
│   │   │   ├── eventBus.ts
│   │   │   ├── event.contract.ts
│   │   │   ├── causalGraph.ts
│   │   │   ├── replayController.ts
│   │   │   └── registry.ts
│   │   ├── stores/
│   │   │   ├── app.store.ts
│   │   │   ├── system.store.ts
│   │   │   ├── agentRun.store.ts
│   │   │   └── session.store.ts
│   │   ├── selectors/
│   │   │   ├── agent.selectors.ts
│   │   │   ├── system.selectors.ts
│   │   │   └── run.selectors.ts
│   │   ├── providers/
│   │   │   ├── ThemeProvider.tsx
│   │   │   ├── QueryProvider.tsx
│   │   │   └── SessionProvider.tsx
│   │   ├── hooks/
│   │   │   ├── useAgentRun.ts
│   │   │   ├── useSystemState.ts
│   │   │   └── useSession.ts
│   │   └── index.ts
│
│   ├── shared/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Tooltip.tsx
│   │   ├── motion/
│   │   │   └── MotionBoundary.tsx
│   │   ├── formatting/
│   │   │   ├── format.ts
│   │   │   └── normalize.ts
│   │   ├── timing/
│   │   │   ├── debounce.ts
│   │   │   └── throttle.ts
│   │   └── index.ts
│
│   ├── lobes/
│   │   ├── chat/
│   │   │   ├── ChatView.tsx
│   │   │   ├── ChatComposer.tsx
│   │   │   ├── ChatTimeline.tsx
│   │   │   ├── chat.events.ts
│   │   │   └── chat.boundary.ts
│   │   ├── insightmate/
│   │   │   ├── InsightView.tsx
│   │   │   ├── SummaryPanel.tsx
│   │   │   ├── insight.events.ts
│   │   │   └── insight.boundary.ts
│   │   ├── studyflow/
│   │   │   ├── StudyPlanner.tsx
│   │   │   ├── KnowledgeGraph.tsx
│   │   │   ├── study.events.ts
│   │   │   └── study.boundary.ts
│   │   ├── autoagent/
│   │   │   ├── PlannerView.tsx
│   │   │   ├── ToolExecutionView.tsx
│   │   │   ├── ExecutionTimeline.tsx
│   │   │   ├── autoagent.events.ts
│   │   │   └── autoagent.boundary.ts
│   │   └── sandbox/
│   │       ├── Playground.tsx
│   │       ├── Experiments.tsx
│   │       └── sandbox.boundary.ts
│
│   ├── experiments/
│   │   └── motion-lab.tsx
│
│   ├── performance/
│   │   ├── profiler.ts
│   │   └── metrics.ts
│
│   ├── mocks/
│   │   ├── agent.mock.ts
│   │   ├── chat.mock.ts
│   │   └── replay.mock.ts
│
│   ├── tests/
│   │   ├── invariants/
│   │   │   ├── no-cross-lobe-import.test.ts
│   │   │   ├── route-purity.test.ts
│   │   │   ├── mediator-enforcement.test.ts
│   │   │   └── monotonic-state.test.ts
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│
│   ├── types/
│   │   ├── agent.ts
│   │   ├── run.ts
│   │   ├── system.ts
│   │   ├── temporal.ts
│   │   └── api.ts
│
│   ├── utils/
│   │   ├── logger.ts
│   │   ├── assert.ts
│   │   ├── invariant.ts
│   │   └── id.ts
│
│   └── index.ts
│
└── .github/
    └── workflows/
        ├── ci.yml
        ├── lint.yml
        └── invariants.yml

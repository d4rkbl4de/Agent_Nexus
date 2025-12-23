'use client';

import { emit } from '../../../core/mediator/emit';
import { useAgentPulseSelector } from '../../../core/hooks/useAgentPulseSelector';
import { AgentPulse } from '../../../contracts/shared.schema'; // Import the type for explicit casting

const TEST_AGENT_ID = 'insightmate-agent-001';

const AgentMonitor = () => {
  const pulse = useAgentPulseSelector(TEST_AGENT_ID);

  if (!pulse) {
    return <p className="text-gray-500">Agent Pulse: Awaiting initialization...</p>;
  }

  return (
    <div className="p-4 border border-blue-500 rounded-lg bg-blue-50">
      <h3 className="text-lg font-semibold text-blue-700">Agent ID: {pulse.agentId}</h3>
      <p>Status: <span className="font-bold text-green-600">{pulse.status}</span></p>
      <p>Confidence: {pulse.confidence.toFixed(2)}</p>
      <p>Timestamp Cursor: {new Date(pulse.timestamp).toLocaleTimeString()}</p>
      <p className="mt-2 p-2 bg-white border rounded">Thought: {pulse.thoughtChunk}</p>
    </div>
  );
};

const InsightMatePage = () => {
  
  const generateFakePulse = () => {
    // FIX: Define the array of statuses with explicit type casting to satisfy the AgentPulse contract.
    const statuses: AgentPulse['status'][] = ['running', 'running', 'paused', 'complete'];
    
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    
    const fakePulsePayload: AgentPulse = { // Cast the whole payload explicitly as well
      agentId: TEST_AGENT_ID,
      status: randomStatus,
      thoughtChunk: `Processing step ${Math.floor(Math.random() * 100)}: Analyzing data chunk...`,
      confidence: Math.random(),
      timestamp: Date.now(),
    };

    emit('AGENT_STATUS_UPDATE', fakePulsePayload);
    console.log('[Test Emitter] Fired AGENT_STATUS_UPDATE event.');
  };
  
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">InsightMate Lobe - Cognitive Substrate Verification</h1>
      
      <button
        onClick={generateFakePulse}
        className="px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Simulate Agent Pulse Update (Fake WS)
      </button>

      <div className="mt-8">
        <AgentMonitor />
      </div>
    </div>
  );
};

export default InsightMatePage;
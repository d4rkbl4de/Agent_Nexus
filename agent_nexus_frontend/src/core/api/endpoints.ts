export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    REFRESH_TOKEN: '/auth/refresh',
    GET_PROFILE: '/users/me',
    UPDATE_PROFILE: '/users/me',
    LIST_USERS: '/users',
    GET_USER: (id: string) => `/users/${id}`,
  },

  AGENTS: {
    LIST: '/agents',
    CREATE: '/agents',
    GET: (id: string) => `/agents/${id}`,
    UPDATE: (id: string) => `/agents/${id}`,
    DELETE: (id: string) => `/agents/${id}`,
    DEPLOY: (id: string) => `/agents/${id}/deploy`,
    TELEMETRY: (id: string) => `/agents/${id}/telemetry`,
    CONFIG: (id: string) => `/agents/${id}/config`,
  },

  TASKS: {
    LIST: '/tasks',
    GET: (id: string) => `/tasks/${id}`,
    GET_LOGS: (id: string) => `/tasks/${id}/logs`,
    CREATE_TASK: '/tasks',
    CANCEL_TASK: (id: string) => `/tasks/${id}/cancel`,
  },

  CHAT: {
    LIST_SESSIONS: (agentId: string) => `/agents/${agentId}/sessions`,
    GET_SESSION: (sessionId: string) => `/chat/sessions/${sessionId}`,
    CREATE_SESSION: (agentId: string) => `/agents/${agentId}/sessions`,
    SEND_MESSAGE: (sessionId: string) => `/chat/sessions/${sessionId}/messages`,
    STREAM_SESSION: (sessionId: string) => `/ws/chat/${sessionId}/stream`, 
  },
  
  STUDIES: {
    LIST: '/studies',
    CREATE: '/studies',
    GET: (id: string) => `/studies/${id}`,
    UPDATE: (id: string) => `/studies/${id}`,
    START: (id: string) => `/studies/${id}/start`,
    RESULTS: (id: string) => `/studies/${id}/results`,
    TEST_PROMPTS: (studyId: string) => `/studies/${studyId}/prompts`,
  },

  PERFORMANCE: {
    GET_DASHBOARD: '/performance/dashboard',
    GET_METRIC: (metricName: string) => `/performance/metrics/${metricName}`,
    GET_INSIGHTS: '/performance/insights',
    GET_RESOURCE_USAGE: '/performance/usage',
  },
};
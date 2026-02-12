/**
 * API Load Test for ALGORITHMIC ARTS Platform
 * Using k6 for performance testing
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Number of virtual users
  vus: 100,
  
  // Duration of the test
  duration: '30s',
  
  // Thresholds for performance metrics
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests < 500ms, 99% < 1000ms
    http_req_failed: ['rate<0.01'], // Less than 1% failure rate
  },
};

// Base URL for the API (can be overridden with environment variables)
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

export default function () {
  // Test health check endpoint
  const healthCheckRes = http.get(`${BASE_URL}/health`);
  check(healthCheckRes, {
    'health check status is 200': (r) => r.status === 200,
    'health check returns healthy': (r) => r.json().status === 'healthy',
  });
  
  // Test auth endpoints (register and login)
  const registerData = {
    email: `test-${Math.random().toString(36).substr(2, 9)}@example.com`,
    full_name: 'Load Test User',
    password: 'password123'
  };
  
  const registerRes = http.post(`${BASE_URL}/auth/register`, JSON.stringify(registerData), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(registerRes, {
    'register status is 201': (r) => r.status === 201,
  });
  
  // Login with registered user
  const loginData = {
    email: registerData.email,
    password: registerData.password
  };
  
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify(loginData), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'login returns access token': (r) => r.json().access_token !== undefined,
  });
  
  // Test company search endpoint (requires auth token)
  const authToken = loginRes.json().access_token;
  
  const searchRes = http.get(`${BASE_URL}/companies/search?query=test`, {
    headers: { 
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    },
  });
  
  check(searchRes, {
    'search status is 200': (r) => r.status === 200,
    'search returns companies': (r) => r.json().items !== undefined,
  });
  
  // Simulate realistic user behavior with delays
  sleep(0.5);
}
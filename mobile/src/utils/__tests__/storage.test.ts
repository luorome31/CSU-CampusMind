import { storage } from '../storage';

describe('storage', () => {
  const testToken = 'test_token_123';
  const testSessionId = 'test_session_456';

  beforeEach(async () => {
    // Clear stored values before each test
    await storage.removeToken();
    await storage.removeSessionId();
  });

  it('should set and get token', async () => {
    await storage.setToken(testToken);
    const token = await storage.getToken();
    expect(token).toBe(testToken);
  });

  it('should remove token', async () => {
    await storage.setToken(testToken);
    await storage.removeToken();
    const token = await storage.getToken();
    expect(token).toBeNull();
  });

  it('should set and get sessionId', async () => {
    await storage.setSessionId(testSessionId);
    const sessionId = await storage.getSessionId();
    expect(sessionId).toBe(testSessionId);
  });

  it('should remove sessionId', async () => {
    await storage.setSessionId(testSessionId);
    await storage.removeSessionId();
    const sessionId = await storage.getSessionId();
    expect(sessionId).toBeNull();
  });

  it('should clear all storage', async () => {
    await storage.setToken(testToken);
    await storage.setSessionId(testSessionId);
    await storage.clear();
    const token = await storage.getToken();
    const sessionId = await storage.getSessionId();
    expect(token).toBeNull();
    expect(sessionId).toBeNull();
  });
});
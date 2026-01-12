import { describe, expect, it, vi } from 'vitest';

import { registerRepo } from './apiClient';

describe('apiClient', () => {
  it('posts to the register endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'Demo', path: '/tmp' }),
    });
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    await registerRepo({ name: 'Demo', path: '/tmp' });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/v1/repos/register'),
      expect.objectContaining({ method: 'POST' }),
    );
  });
});

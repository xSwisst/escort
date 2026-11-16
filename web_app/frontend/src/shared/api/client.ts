import { env } from '@/shared/config/env';
import { interceptStubRequest } from '@/shared/api/stubInterceptor';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

type RequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  token?: string | null;
};

const ENABLE_STUBS = env.enableStubs;

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  if (ENABLE_STUBS) {
    return interceptStubRequest<T>(path, options);
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method: options.method ?? 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const fallbackMessage = `API request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      throw new Error(payload.detail || fallbackMessage);
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(fallbackMessage);
    }
  }

  return (await response.json()) as T;
}

const browserOrigin = typeof window !== 'undefined' ? window.location.origin : '';
const fallbackApiBaseUrl = import.meta.env.DEV ? 'http://localhost:8001' : browserOrigin;

function normalizeApiBaseUrl(rawValue?: string) {
  const value = String(rawValue ?? '').trim().replace(/\/+$/, '');
  if (!value) {
    return fallbackApiBaseUrl;
  }

  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && value.startsWith('http://')) {
    return `https://${value.slice('http://'.length)}`;
  }

  return value;
}

export const env = {
  apiBaseUrl: normalizeApiBaseUrl(import.meta.env.VITE_ESCORT_API_BASE_URL as string | undefined),
  enableStubs: ((import.meta.env.VITE_ENABLE_STUBS as string | undefined) ?? 'false') === 'true',
  mainBotUrl: (import.meta.env.VITE_ESCORT_MAIN_BOT_URL as string | undefined)?.trim() || '',
};

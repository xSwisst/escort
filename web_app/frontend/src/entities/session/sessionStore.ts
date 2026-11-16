import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import { createTelegramSession } from '@/shared/api/webAppApi';
import { getTelegramInitData, hasTelegramLaunchContext, waitForTelegramInitData } from '@/shared/lib/telegram';
import type { WebAppSessionResponse } from '@/shared/types/web-app';

type SessionStatus = 'idle' | 'loading' | 'ready' | 'error';

type SessionStore = {
  status: SessionStatus;
  session: WebAppSessionResponse | null;
  error: string | null;
  bootstrap: () => Promise<void>;
};

const SESSION_STORAGE_KEY = 'escort_v1_web_app.session.v1';

function isSessionExpired(session: WebAppSessionResponse | null) {
  const expiresAt = Date.parse(session?.expiresAt ?? '');
  return !Number.isFinite(expiresAt) || expiresAt <= Date.now();
}

export const useSessionStore = create<SessionStore>()(
  persist(
    (set, get) => ({
      status: 'idle',
      session: null,
      error: null,
      bootstrap: async () => {
        const cachedSession = get().session;
        if (cachedSession && !isSessionExpired(cachedSession)) {
          set({ status: 'ready', error: null, session: cachedSession });
          return;
        }

        set({ status: 'loading', error: null, session: null });
        try {
          if (!hasTelegramLaunchContext()) {
            throw new Error('WEB_APP_BROWSER_ONLY');
          }

          const initData = (await waitForTelegramInitData(2000)) || getTelegramInitData();
          if (!initData) {
            throw new Error('WEB_APP_TELEGRAM_INITDATA_MISSING');
          }

          const session = await createTelegramSession(initData);
          set({ session, status: 'ready', error: null });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to bootstrap session';
          set({ status: 'error', error: message, session: null });
        }
      },
    }),
    {
      name: SESSION_STORAGE_KEY,
      partialize: (state) => ({
        session: isSessionExpired(state.session) ? null : state.session,
      }),
    },
  ),
);

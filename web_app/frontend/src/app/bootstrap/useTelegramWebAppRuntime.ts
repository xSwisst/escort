import { useEffect } from 'react';

import { initTelegramWebApp } from '@/shared/lib/telegram';

export function useTelegramWebAppRuntime() {
  useEffect(() => {
    const cleanupTelegram = initTelegramWebApp();

    return () => {
      cleanupTelegram();
    };
  }, []);
}

import { useEffect } from 'react';

import { useSessionStore } from '@/entities/session/sessionStore';

export function useBootstrap() {
  const bootstrap = useSessionStore((state) => state.bootstrap);
  const status = useSessionStore((state) => state.status);

  useEffect(() => {
    if (status === 'idle') {
      void bootstrap();
    }
  }, [bootstrap, status]);
}

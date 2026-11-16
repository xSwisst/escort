import type { PropsWithChildren } from 'react';
import { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider, dehydrate, hydrate } from '@tanstack/react-query';

const QUERY_CACHE_STORAGE_KEY = 'escort_v1_web_app.query_cache.v1';
const PERSISTED_QUERY_ROOT_KEYS = new Set([
  'about',
  'favorites',
  'model-sheet',
  'models',
  'profile',
  'profile-orders',
  'support',
]);

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,
        gcTime: 30 * 60 * 1000,
        retry: 1,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
      },
    },
  });
}

function restoreQueryCache(queryClient: QueryClient) {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const raw = window.localStorage.getItem(QUERY_CACHE_STORAGE_KEY);
    if (!raw) {
      return;
    }

    hydrate(queryClient, JSON.parse(raw) as Parameters<typeof hydrate>[1]);
  } catch {
    window.localStorage.removeItem(QUERY_CACHE_STORAGE_KEY);
  }
}

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(() => {
    const client = createQueryClient();
    restoreQueryCache(client);
    return client;
  });

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    let persistTimeoutId: number | null = null;
    const unsubscribe = queryClient.getQueryCache().subscribe(() => {
      if (persistTimeoutId != null) {
        window.clearTimeout(persistTimeoutId);
      }

      persistTimeoutId = window.setTimeout(() => {
        try {
          const snapshot = dehydrate(queryClient, {
            shouldDehydrateQuery: (query) => {
              if (query.state.status !== 'success') {
                return false;
              }

              const rootKey = query.queryKey[0];
              return typeof rootKey === 'string' && PERSISTED_QUERY_ROOT_KEYS.has(rootKey);
            },
          });
          window.localStorage.setItem(QUERY_CACHE_STORAGE_KEY, JSON.stringify(snapshot));
        } catch {
          window.localStorage.removeItem(QUERY_CACHE_STORAGE_KEY);
        }
      }, 200);
    });

    return () => {
      if (persistTimeoutId != null) {
        window.clearTimeout(persistTimeoutId);
      }
      unsubscribe();
    };
  }, [queryClient]);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { initCorners } from '@spatio-labs/squircle/corners';

import { AppRouter } from '@/app/router/AppRouter';
import { AppProviders } from '@/app/providers/AppProviders';
import './index.css';

initCorners({
  selector: '.glass-block,.glass-block-soft,.glass-block-muted,.glass-avatar,.glass-sheet,.glass-nested,.profile,.switcher,[class*="corner-"],.squircle,[data-corner-shape]',
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppProviders>
      <AppRouter />
    </AppProviders>
  </StrictMode>,
)

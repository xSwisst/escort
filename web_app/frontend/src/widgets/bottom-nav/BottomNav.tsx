import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import aboutIcon from '@/assets/icons/about.svg';
import butterflyIcon from '@/assets/icons/butterfly.svg';
import questionIcon from '@/assets/icons/question.svg';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';

const tabs = [
  {
    label: 'О нас',
    path: '/about',
    icon: (
      <MaskedIcon src={aboutIcon} className="bottom-nav__icon bottom-nav__icon--about" />
    ),
  },
  {
    label: 'Модели',
    path: '/models',
    icon: (
      <MaskedIcon src={butterflyIcon} className="bottom-nav__icon bottom-nav__icon--models" />
    ),
  },
  {
    label: 'Поддержка',
    path: '/support',
    icon: (
      <MaskedIcon src={questionIcon} className="bottom-nav__icon bottom-nav__icon--support" />
    ),
  },
];

type BottomNavProps = {
  hidden?: boolean;
};

export function BottomNav({ hidden = false }: BottomNavProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const jelloTimeoutRef = useRef<number | null>(null);
  const activeTab = useMemo(() => {
    if (location.pathname.startsWith('/models')) {
      return 1;
    }

    if (location.pathname.startsWith('/support')) {
      return 2;
    }

    if (location.pathname.startsWith('/profile')) {
      return -1;
    }

    return 0;
  }, [location.pathname]);
  const [previousTab, setPreviousTab] = useState(0);
  const [jelloTarget, setJelloTarget] = useState<string | null>(null);
  const switcherTab = activeTab >= 0 ? activeTab : -1;

  useEffect(() => {
    if (activeTab >= 0) {
      setPreviousTab(activeTab);
    }
  }, [activeTab]);

  useEffect(() => () => {
    if (jelloTimeoutRef.current) {
      window.clearTimeout(jelloTimeoutRef.current);
    }
  }, []);

  const triggerJello = (target: string) => {
    if (jelloTimeoutRef.current) {
      window.clearTimeout(jelloTimeoutRef.current);
    }

    setJelloTarget(null);

    window.requestAnimationFrame(() => {
      setJelloTarget(target);
      jelloTimeoutRef.current = window.setTimeout(() => {
        setJelloTarget((current) => (current === target ? null : current));
        jelloTimeoutRef.current = null;
      }, 560);
    });
  };

  const handlePress = (nextTab: number) => {
    const tab = tabs[nextTab];
    if (!tab) {
      return;
    }

    const isFavoritesModelsTab =
      tab.path === '/models'
      && location.pathname === '/models'
      && new URLSearchParams(location.search).get('section') === 'favorites';

    if (isFavoritesModelsTab) {
      return;
    }

    if (activeTab >= 0) {
      setPreviousTab(activeTab);
    }

    triggerJello(`tab-${nextTab}`);
    navigate(tab.path);
  };

  return (
    <div className={`tabbar-wrapper tabbar-enter${hidden ? ' tabbar-wrapper--hidden' : ''}`} aria-label="Навигационная панель">
      <div className="tabbar-root">
        <svg className="filter" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
          <filter id="distortion" x="0%" y="0%" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.008 0.008" numOctaves="2" seed="92" result="noise" />
            <feGaussianBlur in="noise" stdDeviation="2" result="blurred" />
            <feDisplacementMap in="SourceGraphic" in2="blurred" scale="70" xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <filter id="glass-distortion" x="0%" y="0%" width="100%" height="100%" filterUnits="objectBoundingBox">
            <feTurbulence type="fractalNoise" baseFrequency="0.001 0.005" numOctaves="1" seed="17" result="turbulence" />
            <feComponentTransfer in="turbulence" result="mapped">
              <feFuncR type="gamma" amplitude="1" exponent="10" offset="0.5" />
              <feFuncG type="gamma" amplitude="0" exponent="1" offset="0" />
              <feFuncB type="gamma" amplitude="0" exponent="1" offset="0.5" />
            </feComponentTransfer>
            <feGaussianBlur in="turbulence" stdDeviation="3" result="softMap" />
            <feSpecularLighting in="softMap" surfaceScale="5" specularConstant="1" specularExponent="100" lightingColor="white" result="specLight">
              <fePointLight x="-200" y="-200" z="300" />
            </feSpecularLighting>
            <feComposite in="specLight" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="litImage" />
            <feDisplacementMap in="SourceGraphic" in2="softMap" scale="200" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </svg>

        <div className="container">
          <div className="switcher" data-active={switcherTab} data-previous={previousTab} data-tabs="3" role="tablist">
            {tabs.map((tab, index) => (
              <div className="optionWrap" role="presentation" key={tab.label}>
                <button
                  className={`option${activeTab === index ? ' optionActive' : ''}`}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === index}
                  data-option={index}
                  onClick={() => handlePress(index)}
                >
                  <div className={`icon${jelloTarget === `tab-${index}` ? ' nav-icon-jello' : ''}`} aria-hidden="true">
                    {tab.icon}
                  </div>
                  <div className="title">{tab.label}</div>
                </button>
              </div>
            ))}
          </div>

          <button
            className={`profile${location.pathname.startsWith('/profile') ? ' profileActive' : ''}`}
            type="button"
            aria-label="Профиль"
            aria-pressed={location.pathname.startsWith('/profile')}
            onClick={() => {
              triggerJello('profile');
              navigate('/profile');
            }}
          >
            <div className={`profileIcon${jelloTarget === 'profile' ? ' nav-icon-jello' : ''}`} style={{ width: 42, height: 42, overflow: 'hidden', borderRadius: '50%' }}>
              <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <circle cx="21" cy="21" r="21" fill="rgba(255,255,255,0.08)" />
                <circle cx="21" cy="17" r="7" fill="rgba(255,255,255,0.25)" />
                <ellipse cx="21" cy="34" rx="12" ry="8" fill="rgba(255,255,255,0.15)" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

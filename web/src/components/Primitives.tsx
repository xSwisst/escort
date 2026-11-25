import type { CSSProperties, ReactNode } from 'react';
import s from './Editorial.module.css';

export function Arrow({ down = false }: { down?: boolean }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      style={down ? { transform: 'rotate(135deg)' } : undefined}
    >
      <path
        d="M5 19 19 5M5 5h14v14"
        stroke="currentColor"
        strokeWidth="1.25"
      />
    </svg>
  );
}

export function Photo({
  index = 0,
  wide = false,
  priority = false,
  className = '',
  alt = '',
}: {
  index?: number;
  wide?: boolean;
  priority?: boolean;
  className?: string;
  alt?: string;
}) {
  return (
    <div
      className={[
        s.photo,
        wide ? s.widePhoto : '',
        className,
      ].join(' ')}
      style={{ '--portrait': index } as CSSProperties}
      role="img"
      aria-label={alt}
    >
      {wide ? (
        /* Wide Abstract Editorial Canvas (World Section) */
        <svg
          className={s.photoSvg}
          viewBox="0 0 1536 1024"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="wideGlow1" cx="20%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.4" />
              <stop offset="50%" stopColor="#7c0c1e" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="wideGlow2" cx="80%" cy="45%" r="70%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.45" />
              <stop offset="55%" stopColor="#380610" stopOpacity="0.22" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="wideLineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ece3de" stopOpacity="0.45" />
              <stop offset="50%" stopColor="#e51937" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#ece3de" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="beamGrad" x1="50%" y1="0%" x2="50%" y2="100%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0" />
              <stop offset="50%" stopColor="#e51937" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#e51937" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Deep atmospheric backdrop */}
          <rect width="1536" height="1024" fill="#0b0305" />
          <rect width="1536" height="1024" fill="url(#wideGlow1)" />
          <rect width="1536" height="1024" fill="url(#wideGlow2)" />

          {/* Architectural perspective lines */}
          <line x1="0" y1="200" x2="1536" y2="350" stroke="url(#wideLineGrad)" strokeWidth="0.75" strokeDasharray="4 8" />
          <line x1="0" y1="512" x2="1536" y2="512" stroke="#ece3de" strokeOpacity="0.08" strokeWidth="0.5" />
          <line x1="0" y1="820" x2="1536" y2="700" stroke="url(#wideLineGrad)" strokeWidth="0.75" strokeDasharray="3 9" />

          {/* Flowing abstract ribbons */}
          <path
            d="M-100,600 C300,200 650,900 1100,450 C1350,200 1550,500 1650,400"
            stroke="url(#wideLineGrad)"
            strokeWidth="1.5"
            fill="none"
          />
          <path
            d="M-50,750 C380,350 720,980 1180,550 C1400,320 1580,600 1680,520"
            stroke="#e51937"
            strokeOpacity="0.45"
            strokeWidth="1"
            fill="none"
          />

          {/* Architectural portal arches */}
          <ellipse cx="768" cy="512" rx="420" ry="320" stroke="#ece3de" strokeOpacity="0.14" strokeWidth="1" />
          <ellipse cx="768" cy="512" rx="300" ry="230" stroke="#e51937" strokeOpacity="0.28" strokeWidth="1" />
          <ellipse cx="768" cy="512" rx="160" ry="120" stroke="#ece3de" strokeOpacity="0.3" strokeWidth="0.75" />

          {/* Vertical light beam */}
          <rect x="740" y="0" width="56" height="1024" fill="url(#beamGrad)" />

          {/* Monogram / Watermark */}
          <text
            x="768"
            y="525"
            textAnchor="middle"
            fill="#ece3de"
            fillOpacity="0.18"
            fontSize="18"
            fontFamily="var(--font-bodoni), serif"
            letterSpacing="0.45em"
          >
            E L E G A N T   A G E N C Y
          </text>
          <text
            x="768"
            y="560"
            textAnchor="middle"
            fill="#e51937"
            fillOpacity="0.45"
            fontSize="9"
            fontFamily="var(--font-inter), sans-serif"
            letterSpacing="0.6em"
          >
            I · II · III
          </text>
        </svg>
      ) : index === 0 ? (
        /* Muse 01 — "Грация" (Poise) */
        <svg
          className={s.photoSvg}
          viewBox="0 0 600 900"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="poiseGlow" cx="65%" cy="38%" r="65%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.55" />
              <stop offset="45%" stopColor="#7c0c1e" stopOpacity="0.28" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="poiseLine" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ece3de" stopOpacity="0.65" />
              <stop offset="50%" stopColor="#e51937" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#ece3de" stopOpacity="0.15" />
            </linearGradient>
            <linearGradient id="poiseSilk" x1="30%" y1="0%" x2="70%" y2="100%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#180306" stopOpacity="0.85" />
            </linearGradient>
          </defs>

          {/* Dark luxury background */}
          <rect width="600" height="900" fill="#0c0306" />
          <rect width="600" height="900" fill="url(#poiseGlow)" />

          {/* Elegant geometric arcs & poise silhouette */}
          <path
            d="M120,850 Q280,450 350,220 T480,80"
            stroke="url(#poiseLine)"
            strokeWidth="1.5"
            fill="none"
          />
          <path
            d="M180,900 Q320,520 380,280 T520,120"
            stroke="#e51937"
            strokeOpacity="0.4"
            strokeWidth="1"
            fill="none"
          />
          <path
            d="M200,900 C300,600 420,380 400,220 C380,120 480,60 520,40"
            fill="url(#poiseSilk)"
          />

          {/* Graceful concentric rings */}
          <circle cx="360" cy="340" r="160" stroke="#ece3de" strokeOpacity="0.12" strokeWidth="1" />
          <circle cx="360" cy="340" r="110" stroke="#e51937" strokeOpacity="0.4" strokeWidth="1" />
          <circle cx="360" cy="340" r="50" stroke="#ece3de" strokeOpacity="0.25" strokeWidth="0.75" />

          {/* Editorial Watermark */}
          <text
            x="60"
            y="800"
            fill="#ece3de"
            fillOpacity="0.25"
            fontSize="10"
            fontFamily="var(--font-inter), sans-serif"
            letterSpacing="0.4em"
          >
            01 / GRAZIA
          </text>
          <text
            x="60"
            y="830"
            fill="#e51937"
            fillOpacity="0.65"
            fontSize="14"
            fontFamily="var(--font-bodoni), serif"
            fontStyle="italic"
            letterSpacing="0.1em"
          >
            The Poise
          </text>
        </svg>
      ) : index === 1 ? (
        /* Muse 02 — "Обаяние" (Presence) */
        <svg
          className={s.photoSvg}
          viewBox="0 0 600 900"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="allureGlow" cx="45%" cy="45%" r="65%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#380610" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="allureLine" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.85" />
              <stop offset="50%" stopColor="#ece3de" stopOpacity="0.55" />
              <stop offset="100%" stopColor="#e51937" stopOpacity="0.25" />
            </linearGradient>
            <radialGradient id="coreLight" cx="50%" cy="50%" r="40%">
              <stop offset="0%" stopColor="#ff2a4b" stopOpacity="0.5" />
              <stop offset="60%" stopColor="#e51937" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Deep velvet backdrop */}
          <rect width="600" height="900" fill="#0d0205" />
          <rect width="600" height="900" fill="url(#allureGlow)" />
          <circle cx="300" cy="420" r="220" fill="url(#coreLight)" />

          {/* Sensual magnetic concentric ellipses */}
          <ellipse cx="300" cy="430" rx="190" ry="260" stroke="url(#allureLine)" strokeWidth="1" />
          <ellipse cx="300" cy="430" rx="140" ry="190" stroke="#ece3de" strokeOpacity="0.18" strokeWidth="0.75" />
          <ellipse cx="300" cy="430" rx="80" ry="110" stroke="#e51937" strokeOpacity="0.55" strokeWidth="1.25" />

          {/* Subtle crossing rays */}
          <line x1="80" y1="200" x2="520" y2="660" stroke="#ece3de" strokeOpacity="0.14" strokeWidth="0.75" />
          <line x1="520" y1="200" x2="80" y2="660" stroke="#e51937" strokeOpacity="0.3" strokeWidth="0.75" />

          {/* Editorial Watermark */}
          <text
            x="60"
            y="800"
            fill="#ece3de"
            fillOpacity="0.25"
            fontSize="10"
            fontFamily="var(--font-inter), sans-serif"
            letterSpacing="0.4em"
          >
            02 / ALLURE
          </text>
          <text
            x="60"
            y="830"
            fill="#e51937"
            fillOpacity="0.65"
            fontSize="14"
            fontFamily="var(--font-bodoni), serif"
            fontStyle="italic"
            letterSpacing="0.1em"
          >
            The Presence
          </text>
        </svg>
      ) : (
        /* Muse 03 — "Интрига" (Intrigue) & Hero Visual */
        <svg
          className={s.photoSvg}
          viewBox="0 0 600 900"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="intrigueGlow" cx="72%" cy="30%" r="70%">
              <stop offset="0%" stopColor="#e51937" stopOpacity="0.65" />
              <stop offset="45%" stopColor="#7c0c1e" stopOpacity="0.35" />
              <stop offset="85%" stopColor="#180306" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="sharpEdge" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff2a4b" stopOpacity="0.95" />
              <stop offset="50%" stopColor="#e51937" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#ece3de" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="shadowFacet" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#380610" stopOpacity="0.65" />
              <stop offset="100%" stopColor="#080808" stopOpacity="0.9" />
            </linearGradient>
          </defs>

          {/* Deep architectural dark backdrop */}
          <rect width="600" height="900" fill="#090204" />
          <rect width="600" height="900" fill="url(#intrigueGlow)" />

          {/* Chiaroscuro high-fashion architectural facets */}
          <polygon points="180,0 600,0 600,520 320,380" fill="url(#shadowFacet)" />
          <polygon points="600,380 600,900 240,900 420,600" fill="#140307" fillOpacity="0.75" />

          {/* Sharp glowing light beam lines */}
          <line x1="180" y1="0" x2="600" y2="720" stroke="url(#sharpEdge)" strokeWidth="1.5" />
          <line x1="80" y1="120" x2="520" y2="880" stroke="#e51937" strokeOpacity="0.4" strokeWidth="0.75" />
          <line x1="320" y1="0" x2="160" y2="900" stroke="#ece3de" strokeOpacity="0.18" strokeWidth="0.75" />

          {/* Geometric diamond accent */}
          <polygon
            points="420,240 480,320 420,400 360,320"
            stroke="#e51937"
            strokeOpacity="0.65"
            strokeWidth="1.2"
            fill="#e51937"
            fillOpacity="0.12"
          />

          {/* Editorial Watermark */}
          <text
            x="60"
            y="800"
            fill="#ece3de"
            fillOpacity="0.25"
            fontSize="10"
            fontFamily="var(--font-inter), sans-serif"
            letterSpacing="0.4em"
          >
            03 / MYSTIQUE
          </text>
          <text
            x="60"
            y="830"
            fill="#e51937"
            fillOpacity="0.65"
            fontSize="14"
            fontFamily="var(--font-bodoni), serif"
            fontStyle="italic"
            letterSpacing="0.1em"
          >
            The Intrigue
          </text>
        </svg>
      )}
    </div>
  );
}

export function Mask({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <span className={s.mask + ' ' + className}>
      <span data-line>{children}</span>
    </span>
  );
}

export function Eyebrow({
  number,
  children,
}: {
  number: string;
  children: ReactNode;
}) {
  return (
    <p className={s.eyebrow}>
      <span>{number}</span>
      <span>{children}</span>
    </p>
  );
}

export function Characters({ text }: { text: string }) {
  return (
    <span aria-label={text}>
      {Array.from(text).map((char, i) => (
        <span className={s.charMask} aria-hidden="true" key={i}>
          <span data-char>{char === ' ' ? '\u00a0' : char}</span>
        </span>
      ))}
    </span>
  );
}

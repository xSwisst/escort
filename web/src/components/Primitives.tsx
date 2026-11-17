import type { CSSProperties, ReactNode } from 'react';
import { site } from '@/lib/config';
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
  const sizes = wide
    ? '100vw'
    : '(min-width: 960px) 180vw, 300vw';

  return (
    <div
      className={[
        s.photo,
        wide ? s.widePhoto : '',
        className,
      ].join(' ')}
      style={{ '--portrait': index } as CSSProperties}
    >
      <picture>
        <source
          type="image/avif"
          srcSet={site.assets.avif}
          sizes={sizes}
        />
        <source
          type="image/webp"
          srcSet={site.assets.webp}
          sizes={sizes}
        />
        <img
          src={site.assets.campaign}
          width="1536"
          height="1024"
          alt={alt}
          loading={priority ? 'eager' : 'lazy'}
          fetchPriority={priority ? 'high' : 'auto'}
          decoding="async"
        />
      </picture>
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

import type { CSSProperties } from 'react';

type MaskedIconProps = {
  src: string;
  className?: string;
  size?: number | string;
};

export function MaskedIcon({ src, className, size }: MaskedIconProps) {
  const style: CSSProperties = {
    WebkitMask: `url("${src}") center / contain no-repeat`,
    mask: `url("${src}") center / contain no-repeat`,
    ...(size != null ? { width: size, height: size } : {}),
  };

  return (
    <span
      aria-hidden="true"
      className={className ? `app-icon ${className}` : 'app-icon'}
      style={style}
    />
  );
}

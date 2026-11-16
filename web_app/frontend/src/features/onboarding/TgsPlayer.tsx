import { useEffect, useRef, useState } from 'react';
import lottie, { AnimationItem } from 'lottie-web';

const tgsCache = new Map<string, object>();

async function fetchAndDecompressTgs(url: string): Promise<object | null> {
  if (tgsCache.has(url)) {
    return tgsCache.get(url)!;
  }

  try {
    const response = await fetch(url);
    if (!response.ok) {
      return null;
    }

    const buffer = await response.arrayBuffer();
    let jsonString = '';

    try {
      if (typeof DecompressionStream !== 'undefined') {
        const decompressionStream = new DecompressionStream('gzip');
        const stream = new Response(buffer).body?.pipeThrough(decompressionStream);
        if (stream) {
          jsonString = await new Response(stream).text();
        }
      }
    } catch {
      jsonString = '';
    }

    if (!jsonString) {
      const decoder = new TextDecoder('utf-8');
      jsonString = decoder.decode(buffer);
    }

    const data = JSON.parse(jsonString);
    tgsCache.set(url, data);
    return data;
  } catch {
    return null;
  }
}

interface TgsPlayerProps {
  url: string;
  className?: string;
  size?: number;
}

export function TgsPlayer({ url, className, size = 220 }: TgsPlayerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const animRef = useRef<AnimationItem | null>(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    if (animRef.current) {
      animRef.current.destroy();
      animRef.current = null;
    }

    fetchAndDecompressTgs(url).then((animationData) => {
      if (isCancelled) {
        return;
      }

      if (!animationData || !containerRef.current) {
        setHasError(true);
        return;
      }

      setHasError(false);
      try {
        animRef.current = lottie.loadAnimation({
          container: containerRef.current,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          animationData,
        });
      } catch {
        setHasError(true);
      }
    });

    return () => {
      isCancelled = true;
      if (animRef.current) {
        animRef.current.destroy();
        animRef.current = null;
      }
    };
  }, [url]);

  return (
    <div
      className={`tgs-player-container${className ? ` ${className}` : ''}`}
      style={{ width: `${size}px`, height: `${size}px` }}
    >
      <div ref={containerRef} className="tgs-player-canvas" />
      {hasError ? (
        <div className="tgs-player-fallback">
          <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="tgs-fallback-whale">
            <ellipse cx="100" cy="115" rx="55" ry="38" fill="#1689ff" />
            <ellipse cx="90" cy="120" rx="42" ry="24" fill="#60a5fa" />
            <path d="M145 110 C165 95 175 110 170 125 C160 130 150 122 145 118 Z" fill="#1689ff" />
            <circle cx="75" cy="108" r="5" fill="#0b1b36" />
            <circle cx="76" cy="107" r="1.5" fill="#ffffff" />
            <path d="M100 80 C95 65 105 65 100 77" stroke="#38bdf8" strokeWidth="4" strokeLinecap="round" />
            <path d="M105 78 C115 63 125 68 110 79" stroke="#38bdf8" strokeWidth="4" strokeLinecap="round" />
            <path d="M95 79 C85 63 75 68 90 80" stroke="#38bdf8" strokeWidth="4" strokeLinecap="round" />
            <path d="M85 92 L115 62" stroke="#2563eb" strokeWidth="9" strokeLinecap="round" />
            <path d="M115 62 L100 62" stroke="#2563eb" strokeWidth="9" strokeLinecap="round" />
          </svg>
        </div>
      ) : null}
    </div>
  );
}

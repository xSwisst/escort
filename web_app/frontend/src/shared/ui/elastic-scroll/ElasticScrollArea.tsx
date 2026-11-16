import { forwardRef, useRef } from 'react';
import type { PropsWithChildren, UIEvent } from 'react';

type ScrollDirection = 'up' | 'down' | 'idle';

type ElasticScrollAreaProps = PropsWithChildren<{
  className?: string;
  innerClassName?: string;
  onScrollStateChange?: (state: { scrollTop: number; direction: ScrollDirection }) => void;
}>;

export const ElasticScrollArea = forwardRef<HTMLDivElement, ElasticScrollAreaProps>(function ElasticScrollArea({
  children,
  className,
  innerClassName,
  onScrollStateChange,
}, ref) {
  const previousScrollTopRef = useRef(0);
  const touchStartYRef = useRef(0);

  const handleTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    touchStartYRef.current = event.touches[0].clientY;
  };

  const handleTouchMove = (event: React.TouchEvent<HTMLDivElement>) => {
    const el = event.currentTarget;
    const touchY = event.touches[0].clientY;
    const isPullingDown = touchY > touchStartYRef.current;
    const isPullingUp = touchY < touchStartYRef.current;

    if (isPullingDown && el.scrollTop <= 0) {
      if (event.cancelable) {
        event.preventDefault();
      }
    } else if (isPullingUp && el.scrollTop + el.clientHeight >= el.scrollHeight - 1) {
      if (event.cancelable) {
        event.preventDefault();
      }
    }
  };

  const handleScroll = (event: UIEvent<HTMLDivElement>) => {
    const nextScrollTop = event.currentTarget.scrollTop;
    const delta = nextScrollTop - previousScrollTopRef.current;
    let direction: ScrollDirection = 'idle';

    if (Math.abs(delta) >= 6) {
      direction = delta > 0 ? 'down' : 'up';
      previousScrollTopRef.current = nextScrollTop;
    }

    onScrollStateChange?.({
      scrollTop: nextScrollTop,
      direction,
    });
  };

  return (
    <div
      ref={ref}
      className={`elastic-scroll-area${className ? ` ${className}` : ''}`}
      onScroll={handleScroll}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
    >
      <div className={`elastic-scroll-area__inner${innerClassName ? ` ${innerClassName}` : ''}`}>
        {children}
      </div>
    </div>
  );
});

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';

export type PromoCarouselCard = {
  id: string;
  eyebrow: string;
  title: string;
  value: string;
  valueSuffix?: string;
  description: string;
  detail: string;
};

const PROMO_CARD_GAP_PX = 14;
const PROMO_CYCLE_MS = 3000;

function getWrappedIndex(index: number, length: number) {
  if (length <= 0) {
    return 0;
  }

  return ((index % length) + length) % length;
}

type PromoCardsCarouselProps = {
  cards: PromoCarouselCard[];
};

export function PromoCardsCarousel({ cards }: PromoCardsCarouselProps) {
  const [activePromoIndex, setActivePromoIndex] = useState(0);
  const [promoCycleVersion, setPromoCycleVersion] = useState(0);
  const [isPromoPageVisible, setIsPromoPageVisible] = useState(
    typeof document === 'undefined' ? true : document.visibilityState === 'visible',
  );
  const [isPromoPointerActive, setIsPromoPointerActive] = useState(false);
  const [isPromoDragging, setIsPromoDragging] = useState(false);
  const [isPromoTransitionEnabled, setIsPromoTransitionEnabled] = useState(true);
  const [promoDragOffset, setPromoDragOffset] = useState(0);
  const [promoShiftDirection, setPromoShiftDirection] = useState<-1 | 0 | 1>(0);
  const [promoViewportWidth, setPromoViewportWidth] = useState(0);
  const promoViewportRef = useRef<HTMLDivElement | null>(null);
  const promoDragPointerIdRef = useRef<number | null>(null);
  const promoDragStartXRef = useRef(0);
  const promoDragOffsetRef = useRef(0);
  const promoIsTransitioningRef = useRef(false);
  const promoPendingShiftRef = useRef(0);

  const hasPromoControls = cards.length > 1;
  const promoCardWidth = Math.max(0, promoViewportWidth);
  const promoStepWidth = promoCardWidth + PROMO_CARD_GAP_PX;
  const visiblePromoCards = useMemo(() => {
    if (!cards.length) {
      return [];
    }

    if (!hasPromoControls) {
      return [cards[0]];
    }

    const currentIndex = getWrappedIndex(activePromoIndex, cards.length);

    return [
      cards[getWrappedIndex(currentIndex - 1, cards.length)],
      cards[currentIndex],
      cards[getWrappedIndex(currentIndex + 1, cards.length)],
    ];
  }, [activePromoIndex, cards, hasPromoControls]);
  const promoBaseTranslate = hasPromoControls ? -promoStepWidth : 0;
  const promoShiftTranslate = promoShiftDirection === 1 ? -promoStepWidth : promoShiftDirection === -1 ? promoStepWidth : 0;
  const promoTranslateStyle = `translateX(${promoBaseTranslate + promoShiftTranslate + promoDragOffset}px)`;

  const restartPromoCycle = () => {
    setPromoCycleVersion((current) => current + 1);
  };

  const shiftPromoTrack = (direction: -1 | 1) => {
    if (!hasPromoControls) {
      return;
    }

    if (promoIsTransitioningRef.current) {
      promoPendingShiftRef.current += direction;
      return;
    }

    promoIsTransitioningRef.current = true;
    setIsPromoTransitionEnabled(true);
    setPromoShiftDirection(direction);
  };

  useEffect(() => {
    if (cards.length <= 1 || isPromoPointerActive || !isPromoPageVisible) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      shiftPromoTrack(1);
    }, PROMO_CYCLE_MS);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [cards.length, isPromoPageVisible, isPromoPointerActive, promoCycleVersion]);

  useEffect(() => {
    const pausePromoPlayback = () => {
      setIsPromoPageVisible(false);

      if (promoShiftDirection !== 0) {
        setActivePromoIndex((current) => current + promoShiftDirection);
      }

      promoPendingShiftRef.current = 0;
      promoIsTransitioningRef.current = false;
      promoDragPointerIdRef.current = null;
      promoDragOffsetRef.current = 0;
      setPromoDragOffset(0);
      setPromoShiftDirection(0);
      setIsPromoDragging(false);
      setIsPromoPointerActive(false);
      setIsPromoTransitionEnabled(false);
    };

    const resumePromoPlayback = () => {
      setIsPromoPageVisible(true);
      promoPendingShiftRef.current = 0;
      promoIsTransitioningRef.current = false;
      promoDragPointerIdRef.current = null;
      promoDragOffsetRef.current = 0;
      setPromoDragOffset(0);
      setPromoShiftDirection(0);
      setIsPromoDragging(false);
      setIsPromoPointerActive(false);
      setIsPromoTransitionEnabled(true);
      restartPromoCycle();
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        resumePromoPlayback();
        return;
      }

      pausePromoPlayback();
    };

    const handleWindowBlur = () => {
      pausePromoPlayback();
    };

    const handleWindowFocus = () => {
      if (document.visibilityState === 'visible') {
        resumePromoPlayback();
      }
    };

    const handlePageHide = () => {
      pausePromoPlayback();
    };

    const handlePageShow = () => {
      if (document.visibilityState === 'visible') {
        resumePromoPlayback();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus);
    window.addEventListener('pagehide', handlePageHide);
    window.addEventListener('pageshow', handlePageShow);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('focus', handleWindowFocus);
      window.removeEventListener('pagehide', handlePageHide);
      window.removeEventListener('pageshow', handlePageShow);
    };
  }, [promoShiftDirection]);

  useLayoutEffect(() => {
    const syncPromoViewportWidth = () => {
      setPromoViewportWidth(promoViewportRef.current?.getBoundingClientRect().width ?? 0);
    };

    syncPromoViewportWidth();
    window.addEventListener('resize', syncPromoViewportWidth);

    return () => {
      window.removeEventListener('resize', syncPromoViewportWidth);
    };
  }, []);

  const handlePromoDragStart = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!hasPromoControls) {
      return;
    }

    if (promoShiftDirection !== 0) {
      setActivePromoIndex((current) => current + promoShiftDirection);
      promoPendingShiftRef.current = 0;
      promoIsTransitioningRef.current = false;
      setPromoShiftDirection(0);
      setIsPromoTransitionEnabled(false);
      setPromoDragOffset(0);
      promoDragOffsetRef.current = 0;
    }

    promoDragPointerIdRef.current = event.pointerId;
    promoDragStartXRef.current = event.clientX;
    promoDragOffsetRef.current = 0;
    setPromoDragOffset(0);
    setIsPromoPointerActive(true);
    restartPromoCycle();
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePromoDragMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (promoDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    const deltaX = event.clientX - promoDragStartXRef.current;
    const dragActivationDistance = 6;

    if (!isPromoDragging && Math.abs(deltaX) < dragActivationDistance) {
      return;
    }

    if (!isPromoDragging) {
      promoIsTransitioningRef.current = false;
      promoPendingShiftRef.current = 0;
      setIsPromoDragging(true);
      setIsPromoTransitionEnabled(false);
      setPromoShiftDirection(0);
    }

    promoDragOffsetRef.current = deltaX;
    setPromoDragOffset(deltaX);
  };

  const handlePromoDragEnd = (event: React.PointerEvent<HTMLDivElement>) => {
    if (promoDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    const viewportWidth = promoViewportRef.current?.getBoundingClientRect().width ?? 0;
    const threshold = Math.min(92, viewportWidth * 0.16);
    const dragDistance = promoDragOffsetRef.current;
    const wasDragging = isPromoDragging;

    promoDragPointerIdRef.current = null;
    promoDragOffsetRef.current = 0;
    setIsPromoPointerActive(false);
    setIsPromoDragging(false);

    if (!wasDragging) {
      setPromoDragOffset(0);
      setPromoShiftDirection(0);
      setIsPromoTransitionEnabled(true);
      restartPromoCycle();
      return;
    }

    if (Math.abs(dragDistance) < threshold) {
      setPromoDragOffset(0);
      setPromoShiftDirection(0);
      setIsPromoTransitionEnabled(true);
      restartPromoCycle();
      return;
    }

    setPromoDragOffset(0);
    if (dragDistance < 0) {
      shiftPromoTrack(1);
    } else {
      shiftPromoTrack(-1);
    }

    restartPromoCycle();
  };

  const handlePromoTrackTransitionEnd = (event: React.TransitionEvent<HTMLDivElement>) => {
    if (!hasPromoControls) {
      return;
    }

    if (event.target !== event.currentTarget || event.propertyName !== 'transform') {
      return;
    }

    const flushPendingShift = () => {
      if (promoPendingShiftRef.current !== 0) {
        const nextDirection = promoPendingShiftRef.current > 0 ? 1 : -1;
        promoPendingShiftRef.current -= nextDirection;
        promoIsTransitioningRef.current = false;
        shiftPromoTrack(nextDirection);
        return;
      }

      promoIsTransitioningRef.current = false;
      setIsPromoTransitionEnabled(true);
    };

    if (promoShiftDirection === 0) {
      flushPendingShift();
      return;
    }

    setActivePromoIndex((current) => current + promoShiftDirection);
    setIsPromoTransitionEnabled(false);
    setPromoShiftDirection(0);
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        flushPendingShift();
      });
    });
  };

  if (!cards.length) {
    return null;
  }

  return (
    <div className="promo-carousel">
      <div
        ref={promoViewportRef}
        className="promo-carousel__viewport"
        onPointerDown={handlePromoDragStart}
        onPointerMove={handlePromoDragMove}
        onPointerUp={handlePromoDragEnd}
        onPointerCancel={handlePromoDragEnd}
      >
        <div
          className="promo-carousel__track"
          style={{
            transform: promoTranslateStyle,
            transition:
              isPromoDragging || !isPromoTransitionEnabled || promoShiftDirection === 0
                ? 'none'
                : 'transform 0.64s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
          onTransitionEnd={handlePromoTrackTransitionEnd}
        >
          {visiblePromoCards.map((card, index) => (
            <article
              key={`${card.id}-${index}`}
              className={`promo-card promo-card--${card.id} glass-block-soft glass-accent-blue`}
            >
              <div className="promo-card__content">
                <p className="promo-card__eyebrow">{card.eyebrow}</p>
                {card.title ? <h2 className="promo-card__title">{card.title}</h2> : null}
                <p className="promo-card__value">
                  <span className="promo-card__value-primary">{card.value}</span>
                  {card.valueSuffix ? <span className="promo-card__value-suffix">{card.valueSuffix}</span> : null}
                </p>
                <p className="promo-card__description">{card.description}</p>
                <p className="promo-card__detail">{card.detail}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}

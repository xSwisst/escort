import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { ONBOARDING_SLIDES } from './types';
import { TgsPlayer } from './TgsPlayer';

const SLIDE_DURATION_MS = 10000;
const ONBOARDING_STORAGE_KEY = 'escort_onboarding_viewed_v1';

export function OnboardingModal() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(() => {
    try {
      return localStorage.getItem(ONBOARDING_STORAGE_KEY) !== 'true';
    } catch {
      return false;
    }
  });
  const [activeIndex, setActiveIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isClosing, setIsClosing] = useState(false);

  const startTimeRef = useRef<number>(Date.now());
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isOpen || isClosing) {
      return;
    }

    startTimeRef.current = Date.now();
    setProgress(0);

    const updateProgress = () => {
      const elapsed = Date.now() - startTimeRef.current;
      const pct = Math.min(100, (elapsed / SLIDE_DURATION_MS) * 100);
      setProgress(pct);

      if (elapsed >= SLIDE_DURATION_MS) {
        if (activeIndex < ONBOARDING_SLIDES.length - 1) {
          setActiveIndex((prev) => prev + 1);
        } else {
          handleFinish();
        }
      } else {
        animationFrameRef.current = requestAnimationFrame(updateProgress);
      }
    };

    animationFrameRef.current = requestAnimationFrame(updateProgress);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [activeIndex, isOpen, isClosing]);

  const handleFinish = () => {
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    } catch {}
    navigate('/models');
    setIsClosing(true);
    setTimeout(() => {
      setIsOpen(false);
    }, 450);
  };

  const handleNext = () => {
    if (activeIndex < ONBOARDING_SLIDES.length - 1) {
      setActiveIndex((prev) => prev + 1);
    } else {
      handleFinish();
    }
  };

  const handlePrev = () => {
    if (activeIndex > 0) {
      setActiveIndex((prev) => prev - 1);
    }
  };

  const handleCardClick = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    if (clickX < rect.width * 0.35) {
      handlePrev();
    } else {
      handleNext();
    }
  };

  if (!isOpen) {
    return null;
  }

  const currentSlide = ONBOARDING_SLIDES[activeIndex] || ONBOARDING_SLIDES[0];

  return createPortal(
    <div className={`onboarding-overlay${isClosing ? ' onboarding-overlay--closing' : ''}`}>
      <div className="onboarding-modal" onClick={handleCardClick}>
        <div className="onboarding-progress-bars" onClick={(e) => e.stopPropagation()}>
          {ONBOARDING_SLIDES.map((slide, index) => {
            let width = 0;
            if (index < activeIndex) {
              width = 100;
            } else if (index === activeIndex) {
              width = progress;
            }

            return (
              <div
                key={`progress-${slide.id}`}
                className="onboarding-progress-track"
                onClick={() => setActiveIndex(index)}
              >
                <div
                  className="onboarding-progress-fill"
                  style={{ width: `${width}%` }}
                />
              </div>
            );
          })}
        </div>

        <div className="onboarding-content-area">
          <div className="onboarding-media-wrapper" onClick={(e) => e.stopPropagation()}>
            <TgsPlayer url={currentSlide.tgsUrl} size={210} />
          </div>

          <div className="onboarding-text-block">
            <span className="onboarding-badge">{currentSlide.badge}</span>
            <h1 className="onboarding-title">{currentSlide.title}</h1>
            <p className="onboarding-description">{currentSlide.description}</p>
          </div>
        </div>

        <div className="onboarding-bottom-actions" onClick={(e) => e.stopPropagation()}>
          <button
            type="button"
            className="onboarding-cta-button"
            onClick={handleNext}
          >
            Продолжить
          </button>
          <p className="onboarding-terms-text">
            Продолжая, вы принимаете Пользовательское соглашение и Политику конфиденциальности.
          </p>
        </div>
      </div>
    </div>,
    document.body,
  );
}

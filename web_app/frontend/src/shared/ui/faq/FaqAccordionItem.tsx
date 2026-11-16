import { useId, useLayoutEffect, useRef } from 'react';
import type { ReactNode } from 'react';

type FaqAccordionItemProps = {
  title: string;
  isOpen: boolean;
  onToggle: () => void;
  children: ReactNode;
  className?: string;
  questionClassName?: string;
  answerClassName?: string;
};

export function FaqAccordionItem({
  title,
  isOpen,
  onToggle,
  children,
  className,
  questionClassName,
  answerClassName,
}: FaqAccordionItemProps) {
  const contentId = useId();
  const answerWrapRef = useRef<HTMLDivElement | null>(null);
  const contentInnerRef = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    const answerWrapElement = answerWrapRef.current;
    const contentElement = contentInnerRef.current;

    if (!answerWrapElement || !contentElement) {
      return undefined;
    }

    const syncHeight = () => {
      answerWrapElement.style.setProperty('--faq-answer-height', `${contentElement.scrollHeight}px`);
    };

    syncHeight();

    const resizeObserver = new ResizeObserver(() => {
      syncHeight();
    });

    resizeObserver.observe(contentElement);

    return () => {
      resizeObserver.disconnect();
    };
  }, [children, isOpen]);

  return (
    <div className={`about-faq__item${isOpen ? ' about-faq__item--open' : ''}${className ? ` ${className}` : ''}`}>
      <button
        type="button"
        className={`about-faq__question${questionClassName ? ` ${questionClassName}` : ''}`}
        aria-expanded={isOpen}
        aria-controls={contentId}
        onClick={onToggle}
      >
        <span>{title}</span>
        <span className={`about-faq__question-icon${isOpen ? ' about-faq__question-icon--open' : ''}`}>+</span>
      </button>
      <div
        ref={answerWrapRef}
        id={contentId}
        className="about-faq__answer-wrap"
        aria-hidden={!isOpen}
      >
        <div ref={contentInnerRef} className="about-faq__answer-inner">
          <div className={`about-faq__answer${answerClassName ? ` ${answerClassName}` : ''}`}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

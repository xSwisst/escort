import { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import messageIcon from '@/assets/icons/message.svg';
import { useSessionStore } from '@/entities/session/sessionStore';
import { getSupport } from '@/shared/api/webAppApi';
import { normalizeTelegramHref } from '@/shared/lib/telegram';
import { FaqAccordionItem } from '@/shared/ui/faq/FaqAccordionItem';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';
import { SearchIcon } from '@/shared/ui/SearchIcon';
import aboutPageContentRaw from './aboutPageContent.yaml?raw';

type FaqItem = {
  id: string;
  question: string;
  answer: string;
};

type FaqSection = {
  id: string;
  title: string;
  items: FaqItem[];
};

const aboutPageContent = JSON.parse(aboutPageContentRaw) as {
  pageTitle: string;
  faqLead: string;
  searchPlaceholder: string;
  linksTitle: string;
  linksChipLabel: string;
  linksSupport: string;
  emptyTitle: string;
  emptyDescription: string;
  sections: FaqSection[];
};

export function AboutPage() {
  const token = useSessionStore((state) => state.session?.sessionToken ?? '');
  const supportQuery = useQuery({
    queryKey: ['support', token],
    queryFn: () => getSupport(token),
    enabled: Boolean(token),
  });
  const [searchValue, setSearchValue] = useState('');
  const [activeSectionId, setActiveSectionId] = useState(aboutPageContent.sections[0]?.id ?? '');
  const [openQuestionIds, setOpenQuestionIds] = useState<string[]>([]);
  const tabsRef = useRef<HTMLDivElement | null>(null);

  const visibleSections = useMemo(() => {
    const normalizedQuery = searchValue.trim().toLowerCase();

    return aboutPageContent.sections
      .map((section) => {
        if (!normalizedQuery) {
          return section;
        }

        const filteredItems = section.items.filter((item) => (
          item.question.toLowerCase().includes(normalizedQuery) || item.answer.toLowerCase().includes(normalizedQuery)
        ));

        return {
          ...section,
          items: filteredItems,
        };
      })
      .filter((section) => section.items.length > 0);
  }, [searchValue]);

  useEffect(() => {
    if (!visibleSections.length) {
      return;
    }

    if (!visibleSections.some((section) => section.id === activeSectionId)) {
      setActiveSectionId(visibleSections[0].id);
    }
  }, [activeSectionId, visibleSections]);

  const activeSection = useMemo(
    () => visibleSections.find((section) => section.id === activeSectionId) ?? visibleSections[0] ?? null,
    [activeSectionId, visibleSections],
  );
  const loopedSections = useMemo(
    () => (visibleSections.length > 1
      ? [
          ...visibleSections,
          ...visibleSections,
          ...visibleSections,
          ...visibleSections,
          ...visibleSections,
        ]
      : visibleSections),
    [visibleSections],
  );

  const isAdjustingScrollRef = useRef(false);

  useEffect(() => {
    if (visibleSections.length <= 1) {
      return undefined;
    }

    const frameId = window.requestAnimationFrame(() => {
      const tabsElement = tabsRef.current;
      if (!tabsElement || !tabsElement.children.length) {
        return;
      }

      const M = visibleSections.length;
      const firstTab = tabsElement.children[0] as HTMLElement | undefined;
      const nextSetFirstTab = tabsElement.children[M] as HTMLElement | undefined;
      if (firstTab && nextSetFirstTab) {
        const oneSetWidth = nextSetFirstTab.offsetLeft - firstTab.offsetLeft;
        if (oneSetWidth > 0) {
          tabsElement.scrollLeft = oneSetWidth * 2;
        }
      }
    });

    return () => {
      window.cancelAnimationFrame(frameId);
    };
  }, [visibleSections]);

  const toggleQuestion = (questionId: string) => {
    setOpenQuestionIds((current) => (
      current.includes(questionId)
        ? current.filter((id) => id !== questionId)
        : [...current, questionId]
    ));
  };

  const handleTabsScroll = () => {
    const tabsElement = tabsRef.current;
    if (!tabsElement || visibleSections.length <= 1 || isAdjustingScrollRef.current) {
      return;
    }

    const M = visibleSections.length;
    const firstTab = tabsElement.children[0] as HTMLElement | undefined;
    const nextSetFirstTab = tabsElement.children[M] as HTMLElement | undefined;
    if (!firstTab || !nextSetFirstTab) {
      return;
    }

    const oneSetWidth = nextSetFirstTab.offsetLeft - firstTab.offsetLeft;
    if (oneSetWidth <= 0) {
      return;
    }

    if (tabsElement.scrollLeft < oneSetWidth * 0.8) {
      isAdjustingScrollRef.current = true;
      tabsElement.scrollLeft += oneSetWidth * 2;
      window.requestAnimationFrame(() => {
        isAdjustingScrollRef.current = false;
      });
      return;
    }

    if (tabsElement.scrollLeft > oneSetWidth * 3.2) {
      isAdjustingScrollRef.current = true;
      tabsElement.scrollLeft -= oneSetWidth * 2;
      window.requestAnimationFrame(() => {
        isAdjustingScrollRef.current = false;
      });
    }
  };

  const supportHref = normalizeTelegramHref(supportQuery.data?.supportBotUrl || '');

  return (
    <section className="space-y-4">
      <div className="about-faq space-y-4">
        <label className="about-faq__search">
          <SearchIcon />
          <input
            className="about-faq__search-input"
            type="text"
            inputMode="search"
            placeholder={aboutPageContent.searchPlaceholder}
            value={searchValue}
            onChange={(event) => setSearchValue(event.target.value)}
          />
        </label>

        {visibleSections.length ? (
          <div
            ref={tabsRef}
            className="about-faq__tabs"
            role="tablist"
            aria-label={aboutPageContent.pageTitle}
            onScroll={handleTabsScroll}
          >
            {loopedSections.map((section, index) => (
              <button
                key={`${section.id}-${index}`}
                type="button"
                role="tab"
                aria-selected={activeSection?.id === section.id}
                className={`about-faq__tab${activeSection?.id === section.id ? ' about-faq__tab--active' : ''}`}
                onClick={() => setActiveSectionId(section.id)}
              >
                {section.title}
              </button>
            ))}
          </div>
        ) : null}

        {visibleSections.length ? (
          activeSection ? (
            <section className="about-faq__section">
              <h2 className="about-faq__section-title">{activeSection.title}</h2>
              <div className="about-faq__items">
                {activeSection.items.map((item) => {
                  const isOpen = openQuestionIds.includes(item.id);

                  return (
                    <FaqAccordionItem
                      key={item.id}
                      title={item.question}
                      isOpen={isOpen}
                      onToggle={() => toggleQuestion(item.id)}
                    >
                      {item.answer}
                    </FaqAccordionItem>
                  );
                })}
              </div>
            </section>
          ) : null
        ) : (
          <div className="about-faq__empty">
            <h2 className="about-faq__empty-title">{aboutPageContent.emptyTitle}</h2>
            <p className="about-faq__empty-description">{aboutPageContent.emptyDescription}</p>
          </div>
        )}

        <div className="about-faq__links">
          <h2 className="about-faq__links-title">{aboutPageContent.linksTitle}</h2>
          <div className="about-faq__links-grid">
            {supportHref ? (
              <a
                href={supportHref}
                target="_blank"
                rel="noreferrer"
                className="about-faq__link"
              >
                <MaskedIcon src={messageIcon} className="about-faq__link-icon about-faq__link-icon--support" />
                <span>{aboutPageContent.linksSupport}</span>
              </a>
            ) : (
              <div className="about-faq__link about-faq__link--disabled">
                <MaskedIcon src={messageIcon} className="about-faq__link-icon about-faq__link-icon--support" />
                <span>{aboutPageContent.linksSupport}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

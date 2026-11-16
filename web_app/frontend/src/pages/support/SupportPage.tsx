import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import atIcon from '@/assets/icons/at.svg';
import clockIcon from '@/assets/icons/clock.svg';
import geoIcon from '@/assets/icons/geo.svg';
import telegramIcon from '@/assets/icons/telegram.svg';
import { useSessionStore } from '@/entities/session/sessionStore';
import { getSupport } from '@/shared/api/webAppApi';
import { extractTelegramHandle, normalizeTelegramHref } from '@/shared/lib/telegram';
import { FaqAccordionItem } from '@/shared/ui/faq/FaqAccordionItem';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';
import supportPageContentRaw from './supportPageContent.yaml?raw';

type SupportFaqItem = {
  id: string;
  question: string;
  answer: string;
};

const supportPageContent = JSON.parse(supportPageContentRaw) as {
  contactTitle: string;
  supportContactLabel: string;
  agencyAddressLabel: string;
  agencyAddressValue: string;
  workingHoursLabel: string;
  workingHoursValue: string;
  telegramActionLabel: string;
  telegramFallbackLabel: string;
  faqTitle: string;
  emptySupportLinkLabel: string;
  faqItems: SupportFaqItem[];
};

export function SupportPage() {
  const token = useSessionStore((state) => state.session?.sessionToken ?? '');
  const query = useQuery({
    queryKey: ['support', token],
    queryFn: () => getSupport(token),
    enabled: Boolean(token),
  });
  const [openQuestionIds, setOpenQuestionIds] = useState<string[]>([]);

  const supportHref = useMemo(
    () => normalizeTelegramHref(query.data?.supportBotUrl ?? ''),
    [query.data?.supportBotUrl],
  );
  const supportHandle = useMemo(
    () => extractTelegramHandle(query.data?.supportBotUrl ?? '', supportPageContent.telegramFallbackLabel),
    [query.data?.supportBotUrl],
  );

  const toggleQuestion = (questionId: string) => {
    setOpenQuestionIds((current) => (
      current.includes(questionId)
        ? current.filter((id) => id !== questionId)
        : [...current, questionId]
    ));
  };

  return (
    <section className="support-page">
      <section className="support-page__card">
        <h1 className="support-page__title">{supportPageContent.contactTitle}</h1>

        <div className="support-page__details">
          <div className="support-page__detail">
            <div className="support-page__detail-icon" aria-hidden="true">
              <MaskedIcon src={atIcon} className="support-page__detail-svg support-page__detail-svg--contact" />
            </div>
            <div className="support-page__detail-body">
              <span className="support-page__detail-label">{supportPageContent.supportContactLabel}</span>
              <span className="support-page__detail-value">{supportHandle}</span>
            </div>
          </div>

          <div className="support-page__detail">
            <div className="support-page__detail-icon" aria-hidden="true">
              <MaskedIcon src={geoIcon} className="support-page__detail-svg support-page__detail-svg--address" />
            </div>
            <div className="support-page__detail-body">
              <span className="support-page__detail-label">{supportPageContent.agencyAddressLabel}</span>
              <span className="support-page__detail-value">{supportPageContent.agencyAddressValue}</span>
            </div>
          </div>

          <div className="support-page__detail">
            <div className="support-page__detail-icon" aria-hidden="true">
              <MaskedIcon src={clockIcon} className="support-page__detail-svg support-page__detail-svg--hours" />
            </div>
            <div className="support-page__detail-body">
              <span className="support-page__detail-label">{supportPageContent.workingHoursLabel}</span>
              <span className="support-page__detail-value">{supportPageContent.workingHoursValue}</span>
            </div>
          </div>
        </div>

        {supportHref ? (
          <a
            href={supportHref}
            target="_blank"
            rel="noreferrer"
            className="support-page__cta"
          >
            <span className="support-page__cta-icon" aria-hidden="true">
              <MaskedIcon src={telegramIcon} className="support-page__cta-svg support-page__cta-svg--telegram" />
            </span>
            <span>{supportPageContent.telegramActionLabel}</span>
          </a>
        ) : (
          <div className="support-page__cta support-page__cta--disabled">
            <span className="support-page__cta-icon" aria-hidden="true">
              <MaskedIcon src={telegramIcon} className="support-page__cta-svg support-page__cta-svg--telegram" />
            </span>
            <span>{supportPageContent.emptySupportLinkLabel}</span>
          </div>
        )}
      </section>

      <section className="support-page__card">
        <h2 className="support-page__title">{supportPageContent.faqTitle}</h2>

        <div className="about-faq__items support-page__faq-items">
          {supportPageContent.faqItems.map((item) => {
            const isOpen = openQuestionIds.includes(item.id);

            return (
              <FaqAccordionItem
                key={item.id}
                title={item.question}
                isOpen={isOpen}
                onToggle={() => toggleQuestion(item.id)}
                questionClassName="support-page__question"
              >
                {item.answer}
              </FaqAccordionItem>
            );
          })}
        </div>
      </section>
    </section>
  );
}

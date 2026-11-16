import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { FAQ_ITEMS } from '../../data/faqData';
import styles from './FAQ.module.css';

export const FAQ: React.FC = () => {
  const [openId, setOpenId] = useState<string | null>(FAQ_ITEMS[0].id);

  const toggle = (id: string) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  return (
    <section id="faq" className={styles.section} aria-label="Информация">
      <div className={styles.headingBlock}>
        <h2 className={styles.title}>Частые вопросы (FAQ)</h2>
        <p className={styles.subtitle}>Ответы на популярные вопросы, правила сервиса и безопасность</p>
      </div>

      <div className={styles.list}>
        {FAQ_ITEMS.map((item) => {
          const isOpen = openId === item.id;
          return (
            <div key={item.id} className={styles.item}>
              <button
                type="button"
                className={styles.trigger}
                onClick={() => toggle(item.id)}
                aria-expanded={isOpen}
              >
                <span>{item.question}</span>
                <ChevronDown
                  size={18}
                  className={`${styles.icon} ${isOpen ? styles.iconRotated : ''}`}
                />
              </button>

              {isOpen && <div className={styles.answer}>{item.answer}</div>}
            </div>
          );
        })}
      </div>
    </section>
  );
};

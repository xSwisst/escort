'use client';

import {
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react';
import gsap from 'gsap';
import { muses, site, type Overlay } from '@/lib/config';
import { Arrow, Photo } from './Primitives';
import s from './Editorial.module.css';

type Value = NonNullable<Overlay>;

export default function Dialogs({
  value,
  onClose,
  open,
}: {
  value: Value;
  onClose: () => void;
  open: (value: Overlay) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const closing = useRef(false);
  const headingId = useId();

  useLayoutEffect(() => {
    const node = dialog.current!;
    const previous = document.activeElement as HTMLElement | null;

    node.showModal();

    const context = gsap.context(() => {
      if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
        gsap.from('[data-dialog-body]', {
          y: 26,
          opacity: 0,
          duration: .65,
          ease: 'power3.out',
        });

        if (value.type === 'menu') {
          gsap.from('[data-menu-link]', {
            yPercent: 110,
            stagger: .07,
            duration: .8,
            ease: 'power4.out',
          });
        }
      }
    }, node);

    return () => {
      context.revert();
      node.close();
      previous?.focus({ preventScroll: true });
    };
  }, [value.type]);

  function close(after?: () => void) {
    if (closing.current) return;
    closing.current = true;

    const finish = () => {
      onClose();
      after?.();
    };

    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      finish();
    } else {
      gsap.to(
        dialog.current!.querySelector('[data-dialog-body]'),
        {
          opacity: 0,
          y: -14,
          duration: .22,
          onComplete: finish,
        }
      );
    }
  }

  const title =
    value.type === 'menu' ? 'Приватный мир.' :
    value.type === 'enquiry' ? 'Давайте начнем.' :
    value.type === 'muse' ? muses[value.index].title :
    value.type === 'privacy' ? 'Конфиденциальность.' :
    'Информация о сайте.';

  return (
    <dialog
      ref={dialog}
      className={s.dialog}
      aria-labelledby={headingId}
      data-lenis-prevent
      onCancel={event => {
        event.preventDefault();
        close();
      }}
      onClick={event => {
        if (event.target === event.currentTarget) close();
      }}
    >
      <div className={s.modalBody} data-dialog-body>
        <div className={s.modalTop}>
          <span>ELEGANT AGENCY</span>
          <button
            type="button"
            className={s.closeButton}
            onClick={() => close()}
            aria-label="Закрыть окно"
          >
            <span>ЗАКРЫТЬ</span>
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                d="m4 4 12 12M16 4 4 16"
                stroke="currentColor"
                fill="none"
              />
            </svg>
          </button>
        </div>

        {value.type === 'menu' ? (
          <>
            <h2 id={headingId} className={s.menuHeading}>{title}</h2>

            <nav
              aria-label="Полная навигация"
              className={s.menuLinks}
            >
              {[
                ['philosophy', 'Философия'],
                ['muses', 'Наши музы'],
                ['experience', 'Наш подход'],
                ['contact', 'Личный запрос'],
              ].map(([id, label], i) => (
                <div className={s.mask} key={id}>
                  <a
                    data-menu-link
                    href={'#' + id}
                    onClick={event => {
                      event.preventDefault();

                      close(() => {
                        window.location.hash = id;
                        document.getElementById(id)?.focus({
                          preventScroll: true,
                        });
                      });
                    }}
                  >
                    <span>0{i + 1}</span>
                    <span>{label}</span>
                    <Arrow />
                  </a>
                </div>
              ))}
              {site.botUrl && (
                <div className={s.mask}>
                  <a
                    data-menu-link
                    href={site.botUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <span>05</span>
                    <span>Telegram-бот</span>
                    <Arrow />
                  </a>
                </div>
              )}
            </nav>

            <p className={s.menuFoot}>
              ПРИВАТНОСТЬ ПО ПРИРОДЕ. / СТРОГО 18+
            </p>
          </>
        ) : value.type === 'muse' ? (
          <div className={s.profile}>
            <Photo
              index={muses[value.index].index}
              alt={'Художественный образ: ' + title}
            />

            <div>
              <p className={s.micro}>
                ОБРАЗ / {muses[value.index].id}
              </p>

              <h2 id={headingId}>{title}</h2>
              <i>{muses[value.index].chapter}</i>
              <p>{muses[value.index].note}</p>

              <p className={s.profileNote}>
                Авторский образ из коллекции Elegant.
                Портрет передает настроение и атмосферу;
                не является публичным каталогом или списком доступности.
              </p>

              <button
                type="button"
                className={s.cta}
                onClick={() => open({
                  type: 'enquiry',
                  muse: title,
                })}
              >
                НАЧАТЬ ДИАЛОГ <Arrow />
              </button>
            </div>
          </div>
        ) : value.type === 'enquiry' ? (
          <div className={s.formLayout}>
            <div>
              <p className={s.micro}>ЛИЧНОЕ ЗНАКОМСТВО</p>
              <h2 id={headingId}>{title}</h2>
              <p>
                Несколько важных деталей.
                <br />
                Начало нашего диалога.
              </p>
            </div>
            <EnquiryForm muse={value.muse} />
          </div>
        ) : (
          <div className={s.legalCopy}>
            <p className={s.micro}>ELEGANT AGENCY / ИНФОРМАЦИЯ</p>
            <h2 id={headingId}>{title}</h2>

            {value.type === 'privacy' ? (
              <>
                <p>
                  Параметры вашего запроса сохраняются исключительно
                  в вашем браузере до тех пор, пока вы сами не решите
                  скопировать их, сохранить или отправить по почте.
                  Этот сайт не передает данные на сторонние серверы.
                </p>
                <p>
                  Сессионное хранилище запоминает только факт
                  просмотра вступительной заставки. Закрытие браузера
                  удаляет эти данные. На сайте отсутствуют сторонние
                  трекеры и рекламная аналитика.
                </p>
                <p>
                  При отправке письма ваш почтовый сервис обрабатывает
                  сообщение в соответствии со своими правилами
                  конфиденциальности. Сервис не заявляет об анонимной
                  или сквозной криптографической доставке писем.
                </p>
              </>
            ) : (
              <>
                <p>
                  Исключительно для лиц старше 18 лет.
                  Данный сайт представляет концепцию приватного
                  персонального сопровождения и знакомств.
                </p>
                <p>
                  Все портреты являются художественными образами.
                  Названия и титулы не являются подтвержденными анкетами
                  или гарантией доступности. Через этот сайт не производятся
                  бронирования или финансовые транзакции.
                </p>
                <p>
                  Любое знакомство требует взаимного согласия и четких
                  договоренностей. Контактные данные и информация оператора
                  предоставляются агентством при личном обращении.
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </dialog>
  );
}

function EnquiryForm({ muse }: { muse?: string }) {
  const [draft, setDraft] = useState('');
  const [message, setMessage] = useState('');
  const prefix = useId();

  function prepare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    setDraft([
      'ЛИЧНЫЙ ЗАПРОС — ELEGANT AGENCY',
      '',
      'Имя: ' + String(data.get('name')).trim(),
      'Контакт: ' + String(data.get('email')).trim(),
      muse ? 'Интересующий образ: ' + muse : '',
      '',
      String(data.get('note')).trim(),
    ].filter(Boolean).join('\n'));

    setMessage(
      'Ваш запрос подготовлен. Выберите удобный способ отправить его.'
    );
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(draft);
      setMessage('Запрос скопирован в буфер обмена.');
    } catch {
      setMessage(
        'Выделите и скопируйте текст запроса ниже.'
      );
    }
  }

  return (
    <form className={s.form} onSubmit={prepare}>
      <label htmlFor={prefix + '-name'}>
        ВАШЕ ИМЯ
        <input
          id={prefix + '-name'}
          name="name"
          autoComplete="name"
          maxLength={100}
          required
          placeholder="Как к вам обращаться?"
        />
      </label>

      <label htmlFor={prefix + '-email'}>
        EMAIL ДЛЯ СВЯЗИ
        <input
          id={prefix + '-email'}
          name="email"
          type="email"
          autoComplete="email"
          maxLength={200}
          required
          placeholder="Ваш контактный email"
        />
      </label>

      <label htmlFor={prefix + '-note'}>
        НЕСКОЛЬКО СЛОВ
        <textarea
          id={prefix + '-note'}
          name="note"
          maxLength={2000}
          rows={3}
          required
          placeholder="Повод встречи. Атмосфера. Что для вас особенно важно."
        />
      </label>

      <label className={s.consent}>
        <input type="checkbox" required />
        <span>
          Мне исполнилось 18 лет, и я понимаю, что это действие формирует черновик запроса.
        </span>
      </label>

      <button type="submit" className={s.cta}>
        СФОРМИРОВАТЬ ЗАПРОС <Arrow />
      </button>

      <p className={s.status} role="status" aria-live="polite">
        {message}
      </p>

      {draft && (
        <div className={s.draft}>
          <label htmlFor={prefix + '-draft'}>
            ВАШ ПРИВАТНЫЙ ЗАПРОС
          </label>

          <textarea
            id={prefix + '-draft'}
            value={draft}
            readOnly
            rows={7}
          />

          <div>
            <button type="button" onClick={copy}>
              СКОПИРОВАТЬ <Arrow />
            </button>

            <a
              href={
                'data:text/plain;charset=utf-8,' +
                encodeURIComponent(draft)
              }
              download="elegant-enquiry.txt"
            >
              СОХРАНИТЬ ФАЙЛ <Arrow />
            </a>

            {site.contactEmail && (
              <a
                href={
                  'mailto:' + site.contactEmail +
                  '?subject=' +
                  encodeURIComponent('Личный запрос — Elegant Agency') +
                  '&body=' +
                  encodeURIComponent(draft)
                }
              >
                ОТПРАВИТЬ EMAIL <Arrow />
              </a>
            )}

            {site.botUrl && (
              <a
                href={site.botUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                ОТКРЫТЬ TELEGRAM-БОТ <Arrow />
              </a>
            )}
          </div>
        </div>
      )}
    </form>
  );
}

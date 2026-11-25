import { Arrow, Characters, Eyebrow, Mask, Photo } from './Primitives';
import { muses, site, type Overlay } from '@/lib/config';
import s from './Editorial.module.css';

type Props = { open: (value: Overlay) => void };

export function Hero() {
  return (
    <section
      id="top"
      className={s.hero}
      data-scene="hero"
      aria-label="Elegant Agency"
    >
      <Photo
        index={2}
        priority
        className={s.heroPhoto}
        alt="Абстрактная архитектурная композиция Elegant Agency"
      />
      <div className={s.heroShade} />

      <div className={s.heroTopline} data-hero-detail>
        <span>ЛИЧНЫЙ СЕРВИС. ИСКЛЮЧИТЕЛЬНОЕ ВНИМАНИЕ.</span>
        <span>ЭЛЕГАНТНОСТЬ КАК ОБРАЗ МЫСЛЕЙ.</span>
      </div>

      <h1 className={s.heroTitle}>
        <Mask className={s.heroElegance}>ЭЛЕГАНТНОСТЬ</Mask>
        <Mask className={s.heroArt}><i>— это искусство.</i></Mask>
      </h1>

      <div className={s.heroBottom} data-hero-detail>
        <a href="#philosophy" className={s.scrollLink}>
          УЗНАТЬ БОЛЬШЕ <Arrow down />
        </a>
        <p>
          Самая редкая близость
          <br />
          не нуждается в зрителях.
        </p>
        <span className={s.heroEdition}>
          ПРИВАТНЫЙ МИР
          <br />
          18+ / ПО ПРИРОДЕ
        </span>
      </div>

      <div className={s.heroIndex} aria-hidden="true">01 — 08</div>
    </section>
  );
}

export function Philosophy() {
  const words = [
    'Некоторые', 'моменты', 'созданы', 'не',
    'для', 'всех.',
  ];

  return (
    <section
      id="philosophy"
      tabIndex={-1}
      className={s.philosophy}
      data-scene="philosophy"
    >
      <Eyebrow number="02">ФИЛОСОФИЯ</Eyebrow>

      <h2 className={s.statement} aria-label={words.join(' ')}>
        {words.map((word, i) => (
          <span
            key={word}
            data-word
            aria-hidden="true"
            className={i === words.length - 1 ? s.serif : ''}
          >
            {word}{' '}
          </span>
        ))}
      </h2>

      <div className={s.philosophyAside}>
        <span className={s.micro}>ИСКУССТВО ЛИЧНОГО ВНИМАНИЯ</span>
        <p>
          Особое удовольствие — быть понятым без лишних слов.
          Быть в компании, где всё естественно. В вечере, созданном
          вокруг вас, а не по чужому расписанию.
        </p>
        <p>
          Элегантность начинается с беседы. Вдумчивого
          знакомства. И пространства, где рождается нечто исключительное.
        </p>
      </div>
    </section>
  );
}

export function PrivateWorld() {
  return (
    <section
      id="private-world"
      className={s.world}
      data-scene="world"
    >
      <Eyebrow number="03">ОСОБЫЙ МИР</Eyebrow>

      <div className={s.worldCollage} aria-hidden="true">
        <Photo index={0} className={s.worldOne} />
        <Photo index={1} className={s.worldTwo} />
        <Photo index={2} className={s.worldThree} />
      </div>

      <Photo
        wide
        className={s.worldCampaign}
        alt="Абстрактное художественное панно Elegant Agency в глубоких винных и бордовых тонах"
      />

      <div className={s.worldVeil} />

      <h2 className={s.worldTitle}>
        <span data-world-word>ПРИВАТНО</span>
        <i data-world-word>по природе.</i>
      </h2>

      <p className={s.worldCaption}>
        Другой ритм.
        <br />
        Исключительно ваш личный мир.
      </p>

      <span className={s.worldSide}>
        БЕЗУПРЕЧНЫЙ СТИЛЬ / ЕСТЕСТВЕННАЯ БЛИЗОСТЬ
      </span>
    </section>
  );
}

export function SelectedMuses({ open }: Props) {
  return (
    <section
      id="muses"
      tabIndex={-1}
      className={s.gallery}
      data-scene="gallery"
    >
      <div className={s.galleryHead}>
        <Eyebrow number="04">НАШИ МУЗЫ</Eyebrow>

        <h2>
          Присутствие.
          <br />
          <i>Больше, чем внешность.</i>
        </h2>

        <p>
          Три грани индивидуальности.
          <br />
          <span>Галерея образов · авторские концепты.</span>
        </p>
      </div>

      <div className={s.galleryViewport}>
        <div className={s.galleryTrack}>
          {muses.map((muse, i) => (
            <button
              type="button"
              data-muse={i}
              data-cursor="СМОТРЕТЬ"
              className={s.museButton}
              onClick={() => open({ type: 'muse', index: i })}
              aria-label={
                'Познакомиться: ' + muse.title +
                ', образ ' + muse.id
              }
              key={muse.id}
            >
              <div className={s.museImage}>
                <Photo
                  index={muse.index}
                  alt={'Художественный образ: ' + muse.title}
                />
                <span className={s.imageRed} />
                <span className={s.museDiscover}>
                  ПОЗНАКОМИТЬСЯ <Arrow />
                </span>
              </div>

              <div className={s.museCaption}>
                <span>{muse.id}</span>
                <h3>{muse.title}</h3>
                <Arrow />
              </div>

              <p className={s.museNote}>{muse.note}</p>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export function TheExperience() {
  const entries = [
    [
      'Вдумчивое знакомство',
      'Беседа о компании, которую вы цените, о событии, которое предстоит, и о деталях, важных для вас. Личный подход начинается с умения слушать.',
    ],
    [
      'Событие, ставшее особенным',
      'Уединенный ужин. Культурный вечер. Значимое торжество. Обстановка — лишь начало; характер вечеру задает общение.',
    ],
    [
      'Пространство быть собой',
      'Истинное взаимопонимание оставляет место непринужденности. Взаимное уважение, прозрачность ожиданий и свобода наслаждаться моментом.',
    ],
  ];

  return (
    <section
      id="experience"
      tabIndex={-1}
      className={s.experience}
      data-scene="experience"
    >
      <Eyebrow number="05">НАШ ПОДХОД</Eyebrow>

      <h2 className={s.experienceTitle}>
        <span data-experience-line>ВАШЕ ВРЕМЯ.</span>
        <i data-experience-line>Ваши правила.</i>
      </h2>

      <div className={s.experienceBody}>
        <p className={s.experienceIntro}>
          Лучшие планы оставляют
          <br />
          место для вдохновения.
        </p>

        <div className={s.experienceList}>
          {entries.map(([title, body], i) => (
            <details key={title} open={i === 0}>
              <summary>
                <span>0{i + 1}</span>
                <h3>{title}</h3>
                <span className={s.plus} aria-hidden="true" />
              </summary>
              <div><p>{body}</p></div>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Discretion() {
  return (
    <section
      id="discretion"
      className={s.discretion}
      data-scene="discretion"
    >
      <Eyebrow number="06">НЕГЛАСНЫЙ СТАНДАРТ</Eyebrow>

      <div className={s.discretionStage}>
        <h2>
          <Characters text="КОНФИДЕНЦИАЛЬНОСТЬ" />
          <span className={s.discretionItalic}>
            <i>— наш главный принцип.</i>
          </span>
        </h2>
        <span className={s.discretionShutter} aria-hidden="true" />
      </div>

      <div className={s.discretionFoot}>
        <p>
          Некоторые вещи остаются
          <br />
          только между нами.
        </p>
        <p>
          Только те подробности, которыми вы решите поделиться.
          <br />
          Диалог, окруженный абсолютной заботой.
        </p>
        <span>ПРИВАТНОСТЬ ПО УБЕЖДЕНИЮ.</span>
      </div>
    </section>
  );
}

export function PrivateEnquiry({ open }: Props) {
  return (
    <section
      id="contact"
      tabIndex={-1}
      className={s.enquiry}
      data-scene="enquiry"
    >
      <div className={s.enquiryCurtain} aria-hidden="true" />
      <Eyebrow number="07">
        ПРИГЛАШЕНИЕ, А НЕ ЗАЯВЛЕНИЕ
      </Eyebrow>

      <h2>
        <Mask>ВОЙДИТЕ В</Mask>
        <Mask><i>приватный мир.</i></Mask>
      </h2>

      <div className={s.enquiryBottom}>
        <p>
          Каждая исключительная встреча
          <br />
          начинается с простого приветствия.
        </p>

        <button
          className={s.cta}
          type="button"
          data-magnetic
          onClick={() => open({ type: 'enquiry' })}
        >
          <span>ОСТАВИТЬ ЗАЯВКУ</span>
          <Arrow />
        </button>
      </div>
    </section>
  );
}

export function Footer({ open }: Props) {
  return (
    <footer className={s.footer} data-scene="footer">
      <div className={s.footerTop}>
        <span>08 / ЗАКЛЮЧИТЕЛЬНОЕ СЛОВО</span>
        <a href="#top">В НАЧАЛО <Arrow /></a>
      </div>

      <a
        href="#top"
        className={s.footerBrand}
        aria-label="Elegant Agency, наверх"
      >
        <span data-footer-brand>ELEGANT</span>
        <i data-footer-brand>Agency.</i>
      </a>

      <div className={s.footerBottom}>
        <span>© {site.copyrightYear} ELEGANT AGENCY</span>
        <div>
          <button
            type="button"
            onClick={() => open({ type: 'privacy' })}
          >
            КОНФИДЕНЦИАЛЬНОСТЬ
          </button>
          <button
            type="button"
            onClick={() => open({ type: 'legal' })}
          >
            ИНФОРМАЦИЯ О САЙТЕ
          </button>
        </div>
        <span>ИСКЛЮЧИТЕЛЬНО ДЛЯ СОВЕРШЕННОЛЕТНИХ. 18+</span>
      </div>
    </footer>
  );
}

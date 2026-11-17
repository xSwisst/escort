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
        alt="Fictional adult fashion model in a black evening dress, framed by burgundy architecture"
      />
      <div className={s.heroShade} />

      <div className={s.heroTopline} data-hero-detail>
        <span>PRIVATE COMPANY. EXCEPTIONALLY CONSIDERED.</span>
        <span>AN ELEGANT STATE OF MIND.</span>
      </div>

      <h1 className={s.heroTitle}>
        <Mask className={s.heroElegance}>ELEGANCE</Mask>
        <Mask className={s.heroArt}><i>is an art.</i></Mask>
      </h1>

      <div className={s.heroBottom} data-hero-detail>
        <a href="#philosophy" className={s.scrollLink}>
          SCROLL TO DISCOVER <Arrow down />
        </a>
        <p>
          The rarest kind of connection
          <br />
          never needs an audience.
        </p>
        <span className={s.heroEdition}>
          A PRIVATE WORLD
          <br />
          18+ / BY NATURE
        </span>
      </div>

      <div className={s.heroIndex} aria-hidden="true">01 — 08</div>
    </section>
  );
}

export function Philosophy() {
  const words = [
    'Some', 'moments', 'are', 'not',
    'meant', 'for', 'everyone.',
  ];

  return (
    <section
      id="philosophy"
      tabIndex={-1}
      className={s.philosophy}
      data-scene="philosophy"
    >
      <Eyebrow number="02">THE PHILOSOPHY</Eyebrow>

      <h2 className={s.statement} aria-label={words.join(' ')}>
        {words.map((word, i) => (
          <span
            key={word}
            data-word
            aria-hidden="true"
            className={i === 6 ? s.serif : ''}
          >
            {word}{' '}
          </span>
        ))}
      </h2>

      <div className={s.philosophyAside}>
        <span className={s.micro}>THE ART OF PERSONAL ATTENTION</span>
        <p>
          There is a particular pleasure in being understood.
          In company that feels natural. In an evening shaped
          around you, rather than an itinerary.
        </p>
        <p>
          Elegant begins with a conversation. A thoughtful
          introduction. The space to let something exceptional unfold.
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
      <Eyebrow number="03">A WORLD APART</Eyebrow>

      <div className={s.worldCollage} aria-hidden="true">
        <Photo index={0} className={s.worldOne} />
        <Photo index={1} className={s.worldTwo} />
        <Photo index={2} className={s.worldThree} />
      </div>

      <Photo
        wide
        className={s.worldCampaign}
        alt="Three fictional adult models photographed in one restrained black and burgundy fashion campaign"
      />

      <div className={s.worldVeil} />

      <h2 className={s.worldTitle}>
        <span data-world-word>PRIVATE</span>
        <i data-world-word>by nature.</i>
      </h2>

      <p className={s.worldCaption}>
        A different rhythm.
        <br />
        An entirely personal world.
      </p>

      <span className={s.worldSide}>
        CONTROLLED INTENSITY / UNFORCED CONNECTION
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
        <Eyebrow number="04">SELECTED MUSES</Eyebrow>

        <h2>
          Presence.
          <br />
          <i>Beyond appearance.</i>
        </h2>

        <p>
          Three expressions of individuality.
          <br />
          <span>Editorial portraits · fictional identities.</span>
        </p>
      </div>

      <div className={s.galleryViewport}>
        <div className={s.galleryTrack}>
          {muses.map((muse, i) => (
            <button
              type="button"
              data-muse={i}
              data-cursor="VIEW"
              className={s.museButton}
              onClick={() => open({ type: 'muse', index: i })}
              aria-label={
                'Discover ' + muse.title +
                ', editorial portrait ' + muse.id
              }
              key={muse.id}
            >
              <div className={s.museImage}>
                <Photo
                  index={muse.index}
                  alt={'Fictional adult fashion portrait: ' + muse.title}
                />
                <span className={s.imageRed} />
                <span className={s.museDiscover}>
                  DISCOVER <Arrow />
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
      'A considered introduction',
      'A conversation about the company you enjoy, the occasion you have in mind and the details that matter to you. Personal attention starts with listening.',
    ],
    [
      'An occasion, made personal',
      'An intimate dinner. A cultural evening. A meaningful celebration. The setting is only the beginning; the connection gives it character.',
    ],
    [
      'Room to be yourself',
      'Thoughtful companionship leaves space for the unscripted. Mutual respect, clear expectations and the freedom to enjoy the moment.',
    ],
  ];

  return (
    <section
      id="experience"
      tabIndex={-1}
      className={s.experience}
      data-scene="experience"
    >
      <Eyebrow number="05">THE EXPERIENCE</Eyebrow>

      <h2 className={s.experienceTitle}>
        <span data-experience-line>YOUR TIME.</span>
        <i data-experience-line>Your terms.</i>
      </h2>

      <div className={s.experienceBody}>
        <p className={s.experienceIntro}>
          The best plans leave
          <br />
          something to possibility.
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
      <Eyebrow number="06">THE UNSPOKEN STANDARD</Eyebrow>

      <div className={s.discretionStage}>
        <h2>
          <Characters text="DISCRETION" />
          <span className={s.discretionItalic}>
            <i>is our signature.</i>
          </span>
        </h2>
        <span className={s.discretionShutter} aria-hidden="true" />
      </div>

      <div className={s.discretionFoot}>
        <p>
          Some things are better
          <br />
          kept between us.
        </p>
        <p>
          Only the details you choose to share.
          <br />
          A conversation handled with care.
        </p>
        <span>PRIVATE, BY CHOICE.</span>
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
        AN INVITATION, NOT AN ANNOUNCEMENT
      </Eyebrow>

      <h2>
        <Mask>ENTER THE</Mask>
        <Mask><i>private world.</i></Mask>
      </h2>

      <div className={s.enquiryBottom}>
        <p>
          Every exceptional connection
          <br />
          begins with a simple hello.
        </p>

        <button
          className={s.cta}
          type="button"
          data-magnetic
          onClick={() => open({ type: 'enquiry' })}
        >
          <span>BEGIN A PRIVATE ENQUIRY</span>
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
        <span>08 / THE FINAL WORD</span>
        <a href="#top">BACK TO THE BEGINNING <Arrow /></a>
      </div>

      <a
        href="#top"
        className={s.footerBrand}
        aria-label="Elegant Agency, back to top"
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
            PRIVACY
          </button>
          <button
            type="button"
            onClick={() => open({ type: 'legal' })}
          >
            SITE INFORMATION
          </button>
        </div>
        <span>EXCLUSIVELY FOR ADULTS. 18+</span>
      </div>
    </footer>
  );
}

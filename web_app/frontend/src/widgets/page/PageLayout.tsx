import type { PropsWithChildren, ReactNode } from 'react';

type PageLayoutProps = PropsWithChildren<{
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}>;

export function PageLayout({ eyebrow, title, description, actions, children }: PageLayoutProps) {
  return (
    <section className="space-y-5">
      <header className="glass-block p-5">
        {eyebrow ? (
          <p className="text-[11px] uppercase tracking-[0.28em] text-[rgb(var(--accent-soft))]">{eyebrow}</p>
        ) : null}
        <h1 className={`${eyebrow ? 'mt-3' : ''} text-[28px] font-semibold tracking-[-0.03em] text-[rgb(var(--text-primary))]`}>
          {title}
        </h1>
        {description ? (
          <p className="mt-3 max-w-[32rem] text-sm leading-6 text-[rgb(var(--text-secondary))]">{description}</p>
        ) : null}
        {actions ? <div className="mt-4">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}

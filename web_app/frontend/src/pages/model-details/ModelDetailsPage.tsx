import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, BadgeCheck, Star } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import { useSessionStore } from '@/entities/session/sessionStore';
import { getModel } from '@/shared/api/webAppApi';
import { formatPrice } from '@/shared/lib/format';
import { PageLayout } from '@/widgets/page/PageLayout';

export function ModelDetailsPage() {
  const { code = '' } = useParams();
  const token = useSessionStore((state) => state.session?.sessionToken ?? '');
  const query = useQuery({
    queryKey: ['model', token, code],
    queryFn: () => getModel(token, code),
    enabled: Boolean(token && code),
  });

  const model = query.data;

  return (
    <PageLayout
      eyebrow="Карточка модели"
      title={model?.name || 'Загрузка анкеты'}
      description="Базовый детальный экран уже подключён к backend. Потом сюда спокойно натянем твой финальный визуал."
      actions={
        <Link to="/models" className="inline-flex items-center gap-2 text-sm text-[rgb(var(--accent-soft))]">
          <ArrowLeft size={16} />
          К списку
        </Link>
      }
    >
      {model ? (
        <div className="space-y-4">
          <div className="grid gap-3">
            {model.photoUrls.length ? (
                <div className="glass-block h-72 overflow-hidden">
                <img
                  src={model.photoUrls[0]}
                  alt={model.name}
                  className="h-full w-full object-cover"
                />
              </div>
            ) : (
                <div className="glass-block flex h-72 items-center justify-center text-[rgb(var(--text-secondary))]">
                Фото пока нет
              </div>
            )}
          </div>
          <div className="glass-block-soft p-5">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              {model.flags.verification ? (
                <span className="glass-chip glass-chip-success">
                  <BadgeCheck size={12} />
                  Проверена
                </span>
              ) : null}
              <span className="glass-chip text-[rgb(var(--text-secondary))]">
                <Star size={12} />
                Рейтинг {model.rating.toFixed(1)}
              </span>
            </div>
            <p className="mt-4 text-sm leading-6 text-[rgb(var(--text-secondary))]">
              {model.description || 'Описание для этой анкеты пока не добавлено.'}
            </p>
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="glass-block-muted p-3">1 час: {formatPrice(model.prices.oneHour)}</div>
              <div className="glass-block-muted p-3">2 часа: {formatPrice(model.prices.twoHours)}</div>
              <div className="glass-block-muted p-3">3 часа: {formatPrice(model.prices.threeHours)}</div>
              <div className="glass-block-muted p-3">Ночь: {formatPrice(model.prices.night)}</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-block-soft p-5 text-sm text-[rgb(var(--text-secondary))]">
          Загружаю данные анкеты...
        </div>
      )}
    </PageLayout>
  );
}

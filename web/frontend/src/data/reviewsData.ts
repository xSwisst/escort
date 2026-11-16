export interface ClientReview {
  id: string;
  clientName: string;
  clientBadge: string;
  city: string;
  rating: number;
  date: string;
  content: string;
  modelCode: string;
}

export const CLIENT_REVIEWS: ClientReview[] = [
  {
    id: 'rev-1',
    clientName: 'Игорь',
    clientBadge: 'Клиент сервиса',
    city: 'Москва',
    rating: 5,
    date: '7 дней назад',
    content: 'Комфортно и без суеты.',
    modelCode: 'ALISA-701',
  },
  {
    id: 'rev-2',
    clientName: 'Роман',
    clientBadge: 'Клиент сервиса',
    city: 'Москва',
    rating: 5,
    date: '2 дня назад',
    content: 'Очень сильная анкета. Сервис на высшем уровне.',
    modelCode: 'VICT-804',
  },
  {
    id: 'rev-3',
    clientName: 'Алексей',
    clientBadge: 'Клиент сервиса',
    city: 'Санкт-Петербург',
    rating: 5,
    date: '10 дней назад',
    content: 'Очень приятная и внимательная. Все договоренности соблюдены.',
    modelCode: 'DIAN-305',
  },
  {
    id: 'rev-4',
    clientName: 'Максим',
    clientBadge: 'Клиент сервиса',
    city: 'Сочи',
    rating: 5,
    date: '4 дня назад',
    content: 'Все как договаривались.',
    modelCode: 'CAM-912',
  },
];

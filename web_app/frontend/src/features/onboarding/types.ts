export interface OnboardingSlide {
  id: number;
  badge: string;
  title: string;
  description: string;
  tgsUrl: string;
}

export const ONBOARDING_SLIDES: OnboardingSlide[] = [
  {
    id: 1,
    badge: 'Velvet Allure',
    title: 'Добро пожаловать!',
    description:
      'Откройте для себя мир исключительных впечатлений и найдите идеальное сопровождение для вашего незабываемого вечера.',
    tgsUrl: '/assets/loading.tgs',
  },
  {
    id: 2,
    badge: 'Премиум каталог',
    title: 'Лучшие модели',
    description:
      'Тщательно отобранные анкеты с верификацией, реальными фотографиями и высокими стандартами качества.',
    tgsUrl: '/assets/models.tgs',
  },
  {
    id: 3,
    badge: 'Конфиденциальность',
    title: 'Безопасный сервис',
    description:
      'Полная анонимность, безопасность ваших данных и безупречный комфорт в каждой детали.',
    tgsUrl: '/assets/security.tgs',
  },
];

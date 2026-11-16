export interface AgencyServiceItem {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  iconName: 'Sparkles' | 'ShieldCheck' | 'Plane' | 'Wine' | 'Gem' | 'Clock';
  tag: string;
}

export const AGENCY_SERVICES: AgencyServiceItem[] = [
  {
    id: 's-1',
    title: 'Отдых у модели',
    subtitle: 'Формат встречи на территории модели',
    description:
      'Встреча в комфортных подготовленных апартаментах модели в престижном районе города без лишней суеты.',
    iconName: 'Gem',
    tag: 'У модели',
  },
  {
    id: 's-2',
    title: 'Выезд к клиенту',
    subtitle: 'Формат встречи на вашей локации',
    description:
      'Приезд модели к вам: апартаменты, загородный дом или номер в отеле с соблюдением всех договоренностей.',
    iconName: 'Plane',
    tag: 'У себя',
  },
  {
    id: 's-3',
    title: 'Ужин и сопровождение',
    subtitle: 'Для мероприятий и закрытых ужинов',
    description:
      'Сопровождение на светские события, рестораны и деловые встречи. Корректная коммуникация и высокий такт.',
    iconName: 'Wine',
    tag: 'Сопровождение',
  },
  {
    id: 's-4',
    title: 'Длинные встречи и ночь',
    subtitle: 'Длительный формат отдыха',
    description:
      'Продолжительные сценарии встреч с предварительным согласованием всех условий и времени через менеджера.',
    iconName: 'Clock',
    tag: 'Ночь',
  },
];

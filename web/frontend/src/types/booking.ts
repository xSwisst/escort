export type TariffType = 'oneHour' | 'twoHours' | 'threeHours' | 'night';

export type MeetingPlace = 'model' | 'client';

export interface BookingFormState {
  modelId: string;
  modelName: string;
  modelPhoto: string;
  city: string;
  date: string;
  time: string;
  place: MeetingPlace;
  address: string;
  tariff: TariffType;
  selectedAdditionals: number[];
  clientName: string;
  clientContact: string;
  contactMethod: 'telegram' | 'whatsapp' | 'call';
  specialRequests?: string;
}

export interface BookingSummary {
  tariffPrice: number;
  additionalsPrice: number;
  totalPrice: number;
}

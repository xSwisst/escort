import { useState, useMemo, useCallback } from 'react';
import { Model } from '../types/model';
import { BookingFormState, BookingSummary, TariffType } from '../types/booking';

export function useBooking(model: Model | null) {
  const [form, setForm] = useState<BookingFormState>({
    modelId: model?.id || '',
    modelName: model?.name || '',
    modelPhoto: model?.photos[0] || '',
    city: model?.cityName || 'Москва',
    date: new Date().toISOString().split('T')[0],
    time: '20:00',
    place: 'model',
    address: '',
    tariff: 'twoHours',
    selectedAdditionals: [],
    clientName: '',
    clientContact: '',
    contactMethod: 'telegram',
    specialRequests: '',
  });

  const [step, setStep] = useState<number>(1);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const setTariff = useCallback((tariff: TariffType) => {
    setForm((prev) => ({ ...prev, tariff }));
  }, []);

  const toggleAdditional = useCallback((id: number) => {
    setForm((prev) => {
      const exists = prev.selectedAdditionals.includes(id);
      return {
        ...prev,
        selectedAdditionals: exists
          ? prev.selectedAdditionals.filter((item) => item !== id)
          : [...prev.selectedAdditionals, id],
      };
    });
  }, []);

  const updateField = useCallback(
    <K extends keyof BookingFormState>(key: K, value: BookingFormState[K]) => {
      setForm((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const summary: BookingSummary = useMemo(() => {
    if (!model) return { tariffPrice: 0, additionalsPrice: 0, totalPrice: 0 };

    const tariffPrice = model.prices[form.tariff] || 0;
    const additionalsPrice = form.selectedAdditionals.reduce((sum, addId) => {
      const found = model.additionals.find((a) => a.id === addId);
      return sum + (found ? found.price : 0);
    }, 0);

    return {
      tariffPrice,
      additionalsPrice,
      totalPrice: tariffPrice + additionalsPrice,
    };
  }, [model, form.tariff, form.selectedAdditionals]);

  const submitBooking = useCallback(() => {
    setIsSuccess(true);
  }, []);

  const resetBooking = useCallback(() => {
    setStep(1);
    setIsSuccess(false);
  }, []);

  return {
    form,
    step,
    setStep,
    isSuccess,
    summary,
    setTariff,
    toggleAdditional,
    updateField,
    submitBooking,
    resetBooking,
  };
}

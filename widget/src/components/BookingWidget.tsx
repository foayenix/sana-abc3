import React, { useState, useEffect } from 'react';
import { Calendar } from './Calendar';
import { TimeSlots } from './TimeSlots';
import { BookingForm } from './BookingForm';
import { Confirmation } from './Confirmation';
import { PractitionerHeader } from './PractitionerHeader';

interface BookingWidgetProps {
  widgetKey: string;
  practitionerId?: string;
  theme: 'light' | 'dark';
  primaryColor: string;
  onBookingComplete?: (booking: any) => void;
  onError?: (error: any) => void;
}

type Step = 'service' | 'date' | 'time' | 'form' | 'confirmation';

interface Practitioner {
  id: string;
  name: string;
  title: string;
  avatar?: string;
  rating: number;
  outcomeScore: number;
}

interface Service {
  id: string;
  name: string;
  duration: number;
  price: number;
  description: string;
}

export const BookingWidget: React.FC<BookingWidgetProps> = ({
  widgetKey,
  theme,
  primaryColor,
  onBookingComplete,
  onError,
}) => {
  const [step, setStep] = useState<Step>('service');
  const [loading, setLoading] = useState(true);
  const [practitioner, setPractitioner] = useState<Practitioner | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [booking, setBooking] = useState<any>(null);

  useEffect(() => {
    fetchWidgetData();
  }, [widgetKey]);

  const fetchWidgetData = async () => {
    try {
      // Mock data - replace with actual API call
      setPractitioner({
        id: '1',
        name: 'Dr. Emily Chen',
        title: 'Licensed Acupuncturist',
        rating: 4.9,
        outcomeScore: 92,
      });

      setServices([
        { id: '1', name: 'Initial Consultation', duration: 90, price: 150, description: 'Comprehensive health assessment and first treatment' },
        { id: '2', name: 'Follow-up Session', duration: 60, price: 100, description: 'Regular acupuncture treatment' },
        { id: '3', name: 'Cupping Therapy', duration: 45, price: 80, description: 'Traditional cupping for muscle tension' },
      ]);

      setLoading(false);
    } catch (error) {
      onError?.(error);
      setLoading(false);
    }
  };

  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    setStep('date');
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setStep('time');
  };

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time);
    setStep('form');
  };

  const handleBookingSubmit = async (formData: any) => {
    try {
      // Mock booking - replace with actual API call
      const newBooking = {
        id: 'BK-' + Math.random().toString(36).substr(2, 9).toUpperCase(),
        practitioner,
        service: selectedService,
        date: selectedDate,
        time: selectedTime,
        client: formData,
        status: 'confirmed',
      };

      setBooking(newBooking);
      setStep('confirmation');
      onBookingComplete?.(newBooking);
    } catch (error) {
      onError?.(error);
    }
  };

  const handleBack = () => {
    switch (step) {
      case 'date': setStep('service'); break;
      case 'time': setStep('date'); break;
      case 'form': setStep('time'); break;
    }
  };

  const handleNewBooking = () => {
    setSelectedService(null);
    setSelectedDate(null);
    setSelectedTime(null);
    setBooking(null);
    setStep('service');
  };

  const cssVars = {
    '--sana-primary': primaryColor,
    '--sana-primary-light': `${primaryColor}20`,
  } as React.CSSProperties;

  if (loading) {
    return (
      <div className={`sana-widget sana-widget--${theme}`} style={cssVars}>
        <div className="sana-widget__loading">
          <div className="sana-widget__spinner" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`sana-widget sana-widget--${theme}`} style={cssVars}>
      {practitioner && <PractitionerHeader practitioner={practitioner} />}

      <div className="sana-widget__content">
        {step === 'service' && (
          <div className="sana-widget__step">
            <h3 className="sana-widget__title">Select a Service</h3>
            <div className="sana-widget__services">
              {services.map((service) => (
                <button
                  key={service.id}
                  className="sana-widget__service"
                  onClick={() => handleServiceSelect(service)}
                >
                  <div className="sana-widget__service-info">
                    <span className="sana-widget__service-name">{service.name}</span>
                    <span className="sana-widget__service-desc">{service.description}</span>
                    <span className="sana-widget__service-duration">{service.duration} min</span>
                  </div>
                  <span className="sana-widget__service-price">${service.price}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 'date' && (
          <div className="sana-widget__step">
            <button className="sana-widget__back" onClick={handleBack}>← Back</button>
            <h3 className="sana-widget__title">Select a Date</h3>
            <Calendar onSelect={handleDateSelect} selectedDate={selectedDate} />
          </div>
        )}

        {step === 'time' && (
          <div className="sana-widget__step">
            <button className="sana-widget__back" onClick={handleBack}>← Back</button>
            <h3 className="sana-widget__title">Select a Time</h3>
            <TimeSlots
              date={selectedDate!}
              duration={selectedService!.duration}
              onSelect={handleTimeSelect}
              selectedTime={selectedTime}
            />
          </div>
        )}

        {step === 'form' && (
          <div className="sana-widget__step">
            <button className="sana-widget__back" onClick={handleBack}>← Back</button>
            <h3 className="sana-widget__title">Your Information</h3>
            <BookingForm onSubmit={handleBookingSubmit} />
          </div>
        )}

        {step === 'confirmation' && booking && (
          <Confirmation booking={booking} onNewBooking={handleNewBooking} />
        )}
      </div>

      <div className="sana-widget__footer">
        <span>Powered by</span>
        <strong>SANA</strong>
      </div>
    </div>
  );
};

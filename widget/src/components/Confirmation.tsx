import React from 'react';
import { format } from 'date-fns';

interface ConfirmationProps {
  booking: any;
  onNewBooking: () => void;
}

export const Confirmation: React.FC<ConfirmationProps> = ({ booking, onNewBooking }) => {
  return (
    <div className="sana-confirmation">
      <div className="sana-confirmation__icon">✓</div>
      <h3>Booking Confirmed!</h3>
      <p className="sana-confirmation__id">Confirmation #{booking.id}</p>
      <div className="sana-confirmation__details">
        <div className="sana-confirmation__row">
          <span>Service</span>
          <strong>{booking.service.name}</strong>
        </div>
        <div className="sana-confirmation__row">
          <span>Date</span>
          <strong>{format(booking.date, 'EEEE, MMMM d, yyyy')}</strong>
        </div>
        <div className="sana-confirmation__row">
          <span>Time</span>
          <strong>{booking.time}</strong>
        </div>
        <div className="sana-confirmation__row">
          <span>Duration</span>
          <strong>{booking.service.duration} minutes</strong>
        </div>
      </div>
      <p className="sana-confirmation__email">A confirmation email has been sent to {booking.client.email}</p>
      <button className="sana-confirmation__new" onClick={onNewBooking}>Book Another Appointment</button>
    </div>
  );
};

import React from 'react';
import { format } from 'date-fns';

interface TimeSlotsProps {
  date: Date;
  duration: number;
  onSelect: (time: string) => void;
  selectedTime: string | null;
}

export const TimeSlots: React.FC<TimeSlotsProps> = ({ date, onSelect, selectedTime }) => {
  const slots = ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM'];

  return (
    <div className="sana-timeslots">
      <p className="sana-timeslots__date">{format(date, 'EEEE, MMMM d, yyyy')}</p>
      <div className="sana-timeslots__grid">
        {slots.map((time) => (
          <button
            key={time}
            className={`sana-timeslots__slot ${selectedTime === time ? 'selected' : ''}`}
            onClick={() => onSelect(time)}
          >
            {time}
          </button>
        ))}
      </div>
    </div>
  );
};

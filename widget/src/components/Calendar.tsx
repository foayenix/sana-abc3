import React, { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, addMonths, subMonths, isToday, isBefore } from 'date-fns';

interface CalendarProps {
  onSelect: (date: Date) => void;
  selectedDate: Date | null;
}

export const Calendar: React.FC<CalendarProps> = ({ onSelect, selectedDate }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const days = eachDayOfInterval({
    start: startOfMonth(currentMonth),
    end: endOfMonth(currentMonth),
  });

  const startDay = startOfMonth(currentMonth).getDay();

  return (
    <div className="sana-calendar">
      <div className="sana-calendar__header">
        <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}>‹</button>
        <span>{format(currentMonth, 'MMMM yyyy')}</span>
        <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}>›</button>
      </div>
      <div className="sana-calendar__weekdays">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      <div className="sana-calendar__days">
        {Array.from({ length: startDay }).map((_, i) => (
          <span key={`empty-${i}`} />
        ))}
        {days.map((day) => {
          const isPast = isBefore(day, new Date()) && !isToday(day);
          const isSelected = selectedDate && isSameDay(day, selectedDate);
          return (
            <button
              key={day.toISOString()}
              className={`sana-calendar__day ${isSelected ? 'selected' : ''} ${isToday(day) ? 'today' : ''}`}
              onClick={() => !isPast && onSelect(day)}
              disabled={isPast}
            >
              {format(day, 'd')}
            </button>
          );
        })}
      </div>
    </div>
  );
};

import React from 'react';

interface PractitionerHeaderProps {
  practitioner: {
    name: string;
    title: string;
    avatar?: string;
    rating: number;
    outcomeScore: number;
  };
}

export const PractitionerHeader: React.FC<PractitionerHeaderProps> = ({ practitioner }) => {
  return (
    <div className="sana-practitioner">
      <div className="sana-practitioner__avatar">
        {practitioner.avatar ? (
          <img src={practitioner.avatar} alt={practitioner.name} />
        ) : (
          <span>{practitioner.name.charAt(0)}</span>
        )}
      </div>
      <div className="sana-practitioner__info">
        <h2>{practitioner.name}</h2>
        <p>{practitioner.title}</p>
        <div className="sana-practitioner__stats">
          <span>★ {practitioner.rating}</span>
          <span>{practitioner.outcomeScore}% Outcomes</span>
        </div>
      </div>
    </div>
  );
};

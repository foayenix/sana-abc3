import React, { useState } from 'react';

interface BookingFormProps {
  onSubmit: (data: any) => void;
}

export const BookingForm: React.FC<BookingFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(formData);
    setLoading(false);
  };

  return (
    <form className="sana-form" onSubmit={handleSubmit}>
      <div className="sana-form__row">
        <div className="sana-form__field">
          <label>First Name *</label>
          <input type="text" required value={formData.firstName} onChange={(e) => setFormData({ ...formData, firstName: e.target.value })} />
        </div>
        <div className="sana-form__field">
          <label>Last Name *</label>
          <input type="text" required value={formData.lastName} onChange={(e) => setFormData({ ...formData, lastName: e.target.value })} />
        </div>
      </div>
      <div className="sana-form__field">
        <label>Email *</label>
        <input type="email" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
      </div>
      <div className="sana-form__field">
        <label>Phone</label>
        <input type="tel" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
      </div>
      <div className="sana-form__field">
        <label>Notes</label>
        <textarea value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} placeholder="Any additional information..." />
      </div>
      <button type="submit" className="sana-form__submit" disabled={loading}>
        {loading ? 'Booking...' : 'Confirm Booking'}
      </button>
    </form>
  );
};

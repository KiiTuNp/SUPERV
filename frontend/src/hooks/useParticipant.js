import { useState } from 'react';

export const useParticipant = () => {
  const [state, setState] = useState(null);
  // participant-specific logic placeholder
  return { state, setState };
};

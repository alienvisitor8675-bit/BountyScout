```python
import React from 'react';
import { useContext } from 'react'; 
import { CellContext } from '../Cell';

const ActionButton = ({ destination, ...props }: { destination?: string }) => {
  const cellContext = useContext(CellContext);
  const parentProps = cellContext?.parentProps;

  const useActionButtonDestinationValidation = () => {
    if (parentProps?.actionButtons) {
      const destinations = parentProps.actionButtons.map((btn: any) => btn.destination);
      const uniqueDestinations = new Set(destinations);
      if (destinations.length !== uniqueDestinations.size) {
        throw new Error('Duplicate actionButton destinations within the same cell');
      }
    }
  };

  useActionButtonDestinationValidation();

  return <ActionButtonComponent {...props} />;
};

useActionButtonDestinationValidation();

export default ActionButton;
```

```python
import React from 'react';
import { useContext } from 'react'; 
import { CellContext } from '../Cell';

const ActionButton = ({ destination, ...props }: { destination?: string }) => {
  const cellContext = useContext(CellContext);
  const parentProps = cellContext?.parentProps;

  const useActionButtonDestinationValidation = () => {
    if (parentProps?.actionButtons) {
      const destinations = parentProps.actionButtons.map((btn: any) => btn.destination);
      const uniqueDestinations = new Set(destinations);
      if (destinations.length !== uniqueDestinations.size) {
        throw new Error('Duplicate actionButton destinations within the same cell');
      }
    }
  };

  useActionButtonDestinationValidation();

  return <ActionButtonComponent {...props} />;
};

useActionButtonDestinationValidation();

export default ActionButton;
```
import React, { useState } from 'react';
import { Box, TextField, Button, Paper } from '@mui/material';

const RequirementForm = ({ onSubmit, loading }) => {
  const [requirement, setRequirement] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!requirement.trim()) return;
    onSubmit(requirement);
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          rows={6}
          variant="outlined"
          label="Requirement Description"
          placeholder="Enter the detailed software requirement..."
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button 
          type="submit" 
          variant="contained" 
          size="large" 
          disabled={loading || !requirement.trim()}
        >
          {loading ? 'Processing...' : 'Submit Requirement'}
        </Button>
      </Box>
    </Paper>
  );
};

export default RequirementForm;

import React from 'react';
import {
  Card, 
  CardContent, 
  Typography, 
  CircularProgress, 
  Box, 
  Chip 
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';

const StatusIcon = ({ status }) => {
  if (status === 'Complete') {
    return <CheckCircleIcon color="success" />;
  }
  if (status === 'Error') {
    return <ErrorIcon color="error" />;
  }
  if (status === 'In Progress') {
    return <CircularProgress size={20} />;
  }
  return <PendingIcon color="disabled" />;
};

const AgentCard = ({ agentName, agentData }) => {
  const status = agentData ? agentData.status : 'Pending';

  return (
    <Card sx={{ minWidth: 275, height: '100%' }} elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <StatusIcon status={status} />
          <Typography sx={{ ml: 1, fontSize: 18 }} variant="h5" component="div">
            {agentName}
          </Typography>
        </Box>
        {agentData && (
          <Paper variant="outlined" sx={{ p: 2, background: '#f5f5f5', maxHeight: 200, overflowY: 'auto' }}>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.8rem'}}>
              {JSON.stringify(agentData.data, null, 2)}
            </pre>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentCard;

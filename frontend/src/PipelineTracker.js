import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import AgentCard from './AgentCard';

const AGENT_NAMES = [
  'Ingestor',
  'Parser',
  'Regulatory Compliance',
  'Test Case Generator',
  'Data Synthesizer',
  'ALM Integrator',
  'Traceability'
];

const PipelineTracker = ({ pipelineState }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
      <Typography variant="h5" gutterBottom>Live Pipeline Status</Typography>
      <Grid container spacing={2}>
        {AGENT_NAMES.map(agentName => (
          <Grid item xs={12} sm={6} md={4} key={agentName}>
            <AgentCard 
              agentName={agentName} 
              agentData={pipelineState[agentName]} 
            />
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default PipelineTracker;
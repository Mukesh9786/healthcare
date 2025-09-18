import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Alert,
  Box
} from '@mui/material';
import RequirementForm from './RequirementForm';
import PipelineTracker from './PipelineTracker';
import ReconnectingWebSocket from 'reconnecting-websocket';

const AGENT_NAMES = [
  'Ingestor',
  'Parser',
  'Regulatory Compliance',
  'Test Case Generator',
  'Data Synthesizer',
  'ALM Integrator',
  'Traceability'
];

const App = () => {
  const [pipelineState, setPipelineState] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [socket, setSocket] = useState(null);

  const jobInProgress = useRef(false);

  useEffect(() => {
    const ws = new ReconnectingWebSocket('ws://127.0.0.1:8080/ws');

    ws.onopen = () => {
      console.log('WebSocket connection established');
      setError('');
    };

    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);
      console.log('Received result:', result);
      setPipelineState(prevState => ({
        ...prevState,
        [result.agent]: result
      }));

      // If this is the last agent, mark the job as complete
      if (result.agent === 'Traceability') {
        jobInProgress.current = false;
        setIsProcessing(false);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      if (jobInProgress.current) {
          setError('Connection lost during processing. Please try again.');
          setIsProcessing(false);
      }
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('Could not connect to the backend service. Please ensure all services are running.');
      setIsProcessing(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const handleProcessRequirement = (requirement) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      // Reset state for a new job
      const initialPipelineState = AGENT_NAMES.reduce((acc, name) => ({...acc, [name]: null}), {});
      setPipelineState(initialPipelineState);
      setError('');
      setIsProcessing(true);
      jobInProgress.current = true;

      socket.send(JSON.stringify({ requirement }));
    } else {
      setError('Not connected to the backend. Please wait for the connection to establish.');
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div">
            Healthcare Agent Pipeline
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Submit a New Requirement
        </Typography>
        <RequirementForm onSubmit={handleProcessRequirement} loading={isProcessing} />
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {(isProcessing || Object.values(pipelineState).some(s => s)) && (
            <PipelineTracker pipelineState={pipelineState} />
        )}
      </Container>
    </Box>
  );
};

export default App;

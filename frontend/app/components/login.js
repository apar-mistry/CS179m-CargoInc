"use client";
import React, { useState } from 'react';
import { TextField, Button, Container, Typography, Box } from '@mui/material';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const LoginComponent = () => {
  const [name, setName] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:5000/api/log_login', { username: name });
      sessionStorage.setItem('username', name);
      router.push('/main'); // Redirect to the main page after login
    } catch (error) {
      console.error('Error logging in:', error);
    }
  };

  return (
    <Container maxWidth="xs" style={{ marginTop: '100px' }}>
      <Box 
        display="flex" 
        flexDirection="column" 
        alignItems="center"
        p={3}
        borderRadius={1}
        boxShadow={3}
      >
        <Typography variant="h5" component="h1" gutterBottom>
          Welcome Operator!
        </Typography>
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <TextField
            label="Name"
            variant="outlined"
            fullWidth
            margin="normal"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            style={{ marginTop: '16px' }}
          >
            Log In
          </Button>
        </form>
      </Box>
    </Container>
  );
};

export default LoginComponent;
import axios from 'axios';

// Use environment variable or fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSimulation = async () => {
  const res = await api.get('/simulate');
  return res.data;
};

export const scoreCustomer = async (customerId: number) => {
  const res = await api.post('/score/customer', { customer_id: customerId });
  return res.data;
};

export const runCampaign = async (budget: number, cpa: number) => {
  const res = await api.post('/recommend', {
    budget,
    cost_per_action: cpa,
    margin: 0.3
  });
  return res.data;
};

export const triggerIngest = async () => {
  const res = await api.post('/admin/ingest');
  return res.data;
};

export const triggerTrain = async () => {
  const res = await api.post('/admin/train');
  return res.data;
};

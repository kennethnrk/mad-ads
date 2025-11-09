import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import companyReducer from './companySlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    company: companyReducer,
  },
});


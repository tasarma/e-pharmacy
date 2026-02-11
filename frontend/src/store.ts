import { configureStore } from "@reduxjs/toolkit";
import productsReducer from "./features/product/productsSlice";
import authReducer from "./features/auth/authSlice";
import { authApi } from "./utils/ApiService";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [authApi.reducerPath]: authApi.reducer,
    products: productsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(authApi.middleware),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

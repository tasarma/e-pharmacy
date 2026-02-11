import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { HttpMethods, OrderItemType } from "../../types";
import { fetchFromSubdomain } from "../../utils/Api";

interface OrderItemsState {
    loading: boolean;
    orderInfo: any;
    error: string | null;
    success: boolean;
  }

const initialState: OrderItemsState = {
  orderInfo: null,
  loading: false,
  error: null,
  success: false,
};

export const createOrderItems = createAsyncThunk(
  "orders/createItem",
  async (orderItemData: OrderItemType, { rejectWithValue }) => {
    try {
      const response = await fetchFromSubdomain(
        "api/orders/createItem",
        HttpMethods.POST,
        {
          product: orderItemData.productId,
          qty: orderItemData.qty
        }
      );

      return response;
    } catch (error: any) {
      if (error.response && error.response.data.error) {
        return rejectWithValue(error.response.data.error);
      } else {
        return rejectWithValue(error.message);
      }
    }
  }
);

const ordersSlice = createSlice({
  name: "orderitems",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(createOrderItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOrderItems.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
      })
      .addCase(createOrderItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to create order items";
      });
  },
});

export default ordersSlice.reducer;

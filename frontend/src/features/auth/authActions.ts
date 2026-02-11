import { createAsyncThunk } from "@reduxjs/toolkit";
import { fetchFromSubdomain } from "../../utils/Api";
import { HttpMethods, TokenType } from "../../types";

interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  gln?: string | null;
  phoneNumber?: string | null;
  address?: string | null;
}

type LoginData = Pick<UserData, "email" | "password">;

export const userLogin = createAsyncThunk(
  "auth/login",
  async (loginData: LoginData, { rejectWithValue }) => {
    try {
      const response: TokenType = await fetchFromSubdomain<TokenType>(
        "users/login/",
        HttpMethods.POST,
        {
          email: loginData.email.trim(),
          password: loginData.password.trim(),
        }
      );

      localStorage.setItem("userTokens", JSON.stringify(response));
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response.data.detail);
    }
  }
);

export const userRegister = createAsyncThunk(
  "auth/register",
  async (registerData: UserData, { rejectWithValue }) => {
    try {
      const response = await fetchFromSubdomain(
        "users/register/",
        HttpMethods.POST,
        {
          first_name: registerData.firstName.trim(),
          last_name: registerData.lastName.trim(),
          email: registerData.email.trim(),
          password: registerData.password.trim(),
          gln: registerData.gln?.trim(),
          phone_number: registerData.phoneNumber?.trim(),
          address: registerData.address?.trim(),
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

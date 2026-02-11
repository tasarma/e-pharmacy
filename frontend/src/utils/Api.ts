import axios, { AxiosRequestConfig } from "axios";
import { HttpMethods } from "../types";

interface ApiResponse {
  response?: any;
}

export const fetchFromSubdomain = async <T>(
  endpoint: string,
  method: HttpMethods = HttpMethods.GET,
  data?: any,
  config: AxiosRequestConfig = {
    headers: {
      "Content-Type": "application/json",
    },
  }
): Promise<T> => {
  const hostname = window.location.hostname;
  const subdomain = hostname.split(".")[0]; // assuming your site is at tenantone.example.com
  const url = `http://${subdomain}.example.com:8000/${endpoint}`;

  // Get the token from storage
  const userTokens = localStorage.getItem("userTokens");
  if (userTokens) {
    const tokenData = JSON.parse(userTokens);
    
   // Check if the access token exists within tokenData
   if (tokenData.access) {
    // Set the Authorization header with the access token
    axios.defaults.headers.post['Authorization'] = `Bearer ${tokenData.access}`;
  } 
}

  const requestConfig: AxiosRequestConfig = {
    url,
    method,
    headers: {
      ...config.headers,
    },
    ...config,
  };

  if (data) {
    requestConfig.data = data;
  }

  try {
    const response = await axios.request<T>(requestConfig);
    return response.data;
  } catch (error: any) {
    let errorResponse: ApiResponse = {};

    if (error.response) {
      errorResponse = {
        response: error.response,
      };
    } else if (error.request) {
      errorResponse = { response: "No response received" };
    } else {
      errorResponse = { response: "Error: " + error.message };
    }

    return Promise.reject(errorResponse);
  }
};

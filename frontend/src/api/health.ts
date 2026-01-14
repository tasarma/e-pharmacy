import apiClient from './client';
import HealthCheckResponse from '../types/api';

export const getHealthStatus = async (): Promise<HealthCheckResponse> => {
    const { data } = await apiClient.get<HealthCheckResponse>('/health/');
    return data;
};

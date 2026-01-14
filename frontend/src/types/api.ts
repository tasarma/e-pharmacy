export interface HealthCheckResponse {
    status: 'ok' | 'error';
    version: string;
    timestamp: string;
}

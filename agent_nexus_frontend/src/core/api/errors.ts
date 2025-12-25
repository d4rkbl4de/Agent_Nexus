import { ApiError } from '../../contracts/shared/meta';

export class AgentNexusError extends Error {
  public readonly name: string = 'AgentNexusError';
  public readonly code: string;
  public readonly details: Record<string, any> | undefined;
  public readonly timestamp: string;

  constructor(apiError: ApiError) {
    super(apiError.message);
    this.code = apiError.error_code;
    this.details = apiError.details;
    this.timestamp = apiError.timestamp;
    
    // Set the prototype explicitly to ensure instanceof works correctly
    Object.setPrototypeOf(this, AgentNexusError.prototype);
  }

  public toApiError(): ApiError {
    return {
      error_code: this.code,
      message: this.message,
      details: this.details,
      timestamp: this.timestamp,
    };
  }
}

export class AuthenticationError extends AgentNexusError {
    public readonly name: string = 'AuthenticationError';
    constructor(apiError: ApiError) {
        super(apiError);
        Object.setPrototypeOf(this, AuthenticationError.prototype);
    }
}

export class AuthorizationError extends AgentNexusError {
    public readonly name: string = 'AuthorizationError';
    constructor(apiError: ApiError) {
        super(apiError);
        Object.setPrototypeOf(this, AuthorizationError.prototype);
    }
}

export class NotFoundError extends AgentNexusError {
    public readonly name: string = 'NotFoundError';
    constructor(apiError: ApiError) {
        super(apiError);
        Object.setPrototypeOf(this, NotFoundError.prototype);
    }
}

export class ValidationError extends AgentNexusError {
    public readonly name: string = 'ValidationError';
    
    /** Specific details about field validation failures. */
    public readonly fieldErrors: Record<string, string> | undefined;

    constructor(apiError: ApiError) {
        super(apiError);
        this.fieldErrors = apiError.details?.field_errors;
        Object.setPrototypeOf(this, ValidationError.prototype);
    }
}

export class NetworkError extends AgentNexusError {
    public readonly name: string = 'NetworkError';
    constructor(message: string, originalCode: string = 'NETWORK_FAILURE') {
        const apiError: ApiError = {
            error_code: originalCode,
            message: message,
            timestamp: new Date().toISOString(),
        };
        super(apiError);
        Object.setPrototypeOf(this, NetworkError.prototype);
    }
}

export const isAgentNexusError = (error: any): error is AgentNexusError => {
    return error instanceof AgentNexusError;
};

/**
 * Utility to map HTTP status codes or custom error codes to specific error classes.
 * @param httpStatus The HTTP status code from the response.
 * @param apiError The structured ApiError object from the response body.
 * @returns An instance of the specific AgentNexusError class.
 */
export const mapApiError = (httpStatus: number, apiError: ApiError): AgentNexusError => {
    switch (httpStatus) {
        case 401:
            return new AuthenticationError(apiError);
        case 403:
            return new AuthorizationError(apiError);
        case 404:
            return new NotFoundError(apiError);
        case 400:
        case 422: // Often used for validation errors
            return new ValidationError(apiError);
        default:
            return new AgentNexusError(apiError);
    }
};
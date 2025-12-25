export type UserRole = 'admin' | 'developer' | 'analyst' | 'viewer';

export type AccountStatus = 'active' | 'suspended' | 'pending_verification' | 'disabled';

export interface PlatformUser {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  status: AccountStatus;
  created_at: string;
  last_login_at?: string;
  
  managed_agent_ids: string[]; 
}

export interface AuthSession {
  token: string;
  expires_at: string;
  user_id: string;
  is_valid: boolean;
  
  refresh_token: string; 
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: PlatformUser;
  session: AuthSession;
}

export interface RegistrationRequest {
  email: string;
  password: string;
  username: string;
  first_name: string;
  last_name: string;
}

export interface RolePermissions {
  role: UserRole;
  
  can_create_agent: boolean;
  can_deploy_agent: boolean;
  can_view_telemetry: boolean;
  can_run_studies: boolean;
  can_manage_users: boolean;
}
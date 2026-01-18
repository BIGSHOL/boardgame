/**
 * Authentication API Contract
 * 인증 관련 API 계약 정의
 */

// ============================================
// Request Types
// ============================================

/** 회원가입 요청 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

/** 로그인 요청 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 토큰 갱신 요청 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

// ============================================
// Response Types
// ============================================

/** 사용자 정보 */
export interface UserResponse {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

/** 토큰 응답 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
}

/** 로그인 응답 */
export interface LoginResponse {
  user: UserResponse;
  tokens: TokenResponse;
}

// ============================================
// API Endpoints
// ============================================

/**
 * POST /api/v1/auth/register
 * - Request: RegisterRequest
 * - Response: UserResponse (201 Created)
 * - Errors: 400 (email/username exists)
 */

/**
 * POST /api/v1/auth/login
 * - Request: LoginRequest
 * - Response: LoginResponse
 * - Errors: 401 (invalid credentials), 403 (disabled account)
 */

/**
 * POST /api/v1/auth/refresh
 * - Request: RefreshTokenRequest
 * - Response: TokenResponse
 * - Errors: 401 (invalid/expired refresh token)
 */

/**
 * GET /api/v1/auth/me
 * - Headers: Authorization: Bearer {access_token}
 * - Response: UserResponse
 * - Errors: 401 (invalid/expired token)
 */

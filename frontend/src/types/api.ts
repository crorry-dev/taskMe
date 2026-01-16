/**
 * API Types for CommitQuest
 * 
 * These types mirror the backend serializers for type-safe API communication.
 */

// User types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  bio: string;
  avatar: string | null;
  total_points: number;
  level: number;
  is_verified: boolean;
  date_joined: string;
}

export interface UserProfile extends User {
  streak_count: number;
  challenges_completed: number;
  challenges_active: number;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// Challenge types
export type ChallengeType = 
  | 'todo'
  | 'streak'
  | 'program'
  | 'quantified'
  | 'team'
  | 'duel'
  | 'team_vs_team'
  | 'community'
  | 'global';

export type ChallengeStatus = 
  | 'draft'
  | 'upcoming'
  | 'active'
  | 'completed'
  | 'cancelled';

export type ChallengeVisibility = 
  | 'private'
  | 'team'
  | 'invite'
  | 'public';

export type ProofType = 
  | 'SELF'
  | 'PHOTO'
  | 'VIDEO'
  | 'DOCUMENT'
  | 'PEER'
  | 'SENSOR';

export interface Challenge {
  id: number;
  title: string;
  description: string;
  challenge_type: ChallengeType;
  status: ChallengeStatus;
  visibility: ChallengeVisibility;
  goal: string;
  target_value: number;
  unit: string;
  required_proof_types: ProofType[];
  min_peer_approvals: number;
  proof_deadline_hours: number;
  team: number | null;
  creator: number;
  creator_name: string;
  max_participants: number | null;
  reward_points: number;
  winner_reward_multiplier: number;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
  participant_count?: number;
  is_participating?: boolean;
  is_creator?: boolean;
  my_participation?: ChallengeParticipant | null;
  participants?: ChallengeParticipant[];
}

export interface ChallengeCreateData {
  title: string;
  description: string;
  challenge_type: ChallengeType;
  visibility?: ChallengeVisibility;
  goal: string;
  target_value: number;
  unit?: string;
  required_proof_types?: ProofType[];
  min_peer_approvals?: number;
  proof_deadline_hours?: number;
  team?: number;
  max_participants?: number;
  reward_points?: number;
  winner_reward_multiplier?: number;
  start_date: string;
  end_date: string;
}

// Participation types
export type ParticipationStatus = 
  | 'invited'
  | 'active'
  | 'completed'
  | 'failed'
  | 'withdrawn';

export interface ChallengeParticipant {
  id: number;
  user: number;
  username: string;
  avatar: string | null;
  status: ParticipationStatus;
  current_progress: number;
  streak_current: number;
  streak_best: number;
  completed: boolean;
  rank: number | null;
  points_earned: number;
  joined_at: string;
  last_contribution_at: string | null;
  completed_at: string | null;
}

// Contribution types
export type ContributionStatus = 
  | 'pending'
  | 'awaiting_review'
  | 'approved'
  | 'rejected';

export interface Contribution {
  id: number;
  participation: number;
  user_name: string;
  value: number;
  note: string;
  status: ContributionStatus;
  logged_at: string;
  created_at: string;
  proofs: Proof[];
}

export interface ContributionCreateData {
  challenge_id: number;
  value: number;
  note?: string;
  logged_at: string;
}

// Proof types
export type ProofStatus = 
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'flagged';

export interface Proof {
  id: number;
  proof_type: ProofType;
  status: ProofStatus;
  image: string | null;
  video: string | null;
  document: string | null;
  sensor_data: Record<string, unknown> | null;
  original_filename: string;
  file_size: number | null;
  mime_type: string;
  reviewed_by: number | null;
  reviewer_name: string | null;
  reviewed_at: string | null;
  rejection_reason: string;
  submitted_at: string;
}

export interface ProofReview {
  id: number;
  proof: number;
  reviewer: number;
  reviewer_name: string;
  verdict: 'approved' | 'rejected';
  comment: string;
  created_at: string;
}

// Team types
export type TeamRole = 'owner' | 'admin' | 'member';

export interface Team {
  id: number;
  name: string;
  description: string;
  avatar: string | null;
  is_public: boolean;
  max_members: number | null;
  total_points: number;
  level: number;
  creator: number;
  member_count?: number;
  created_at: string;
}

export interface TeamMember {
  id: number;
  team: number;
  user: number;
  username: string;
  avatar: string | null;
  role: TeamRole;
  points_contributed: number;
  is_active: boolean;
  joined_at: string;
}

// Reward types
export type RewardType = 'badge' | 'title' | 'item' | 'privilege';

export interface Reward {
  id: number;
  name: string;
  description: string;
  reward_type: RewardType;
  icon: string | null;
  points_cost: number;
  is_available: boolean;
  is_redeemable: boolean;
}

export interface RewardEvent {
  id: number;
  xp_amount: number;
  coins_amount: number;
  badge: Reward | null;
  reason: string;
  reason_detail: string;
  created_at: string;
}

// Duel types
export type DuelStatus = 
  | 'pending'
  | 'active'
  | 'completed'
  | 'cancelled';

export interface Duel {
  id: number;
  challenge: number;
  challenge_title: string;
  challenger: number;
  challenger_name: string;
  opponent: number;
  opponent_name: string;
  status: DuelStatus;
  winner: number | null;
  winner_name: string | null;
  stake_points: number;
  created_at: string;
  accepted_at: string | null;
  completed_at: string | null;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  error?: string;
  [key: string]: unknown;
}

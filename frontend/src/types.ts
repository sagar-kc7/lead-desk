export interface Lead {
  id: number
  name: string
  email: string
  company: string
  website: string | null
  status: string
  owner_id: number
  owner_name?: string
  created_at: string
}

export interface UserInfo {
  id: number
  name: string
  email: string
  role: string
  created_at: string
}

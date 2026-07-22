export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export interface AssessmentResponse {
  tax_year: number
  land_value?: number
  improvement_value?: number
  market_value?: number
  assessed_value?: number
  remarks?: string
}

export interface ParcelResponse {
  parcel_number: string
  gpin?: string
  address?: string
  city?: string
  state?: string
  zoning?: string
  property_type?: string
  neighborhood?: string
  lot_size?: number
  years_owned?: number | null
  sia_flag?: boolean | null
  developer_owned?: boolean | null
  adjacent_developer_owned?: boolean | null
  tax_delinquent?: boolean | null
  tax_lien_amount?: number | null
  delinquency_remarks?: string | null
  owner_name?: string
  owner_address?: string
  owner_city_state?: string
  owner_zip_code?: string
  latest_assessment?: AssessmentResponse | null
  estimated_units?: number | null
  seller_probability?: number | null
  offer_low?: number | null
  offer_high?: number | null
  suggested_offer?: number | null
}

export interface OpportunityResponse {
  parcel_number: string
  owner?: string
  owner_address?: string
  owner_city_state?: string
  owner_zip_code?: string
  address?: string
  zoning?: string
  property_type?: string
  neighborhood?: string
  acres?: number
  years_owned?: number | null
  sia_flag?: boolean | null
  adjacent_developer_owned?: boolean | null
  estimated_units?: number | null
  seller_probability?: number | null
  offer_low?: number | null
  offer_high?: number | null
  suggested_offer?: number | null
  tax_delinquent?: boolean | null
  tax_lien_amount?: number | null
  absentee_owner: boolean
  vk_score: number
}

export async function fetchParcel(parcelNumber: string) {
  const response = await fetch(`${API_BASE_URL}/parcels/${encodeURIComponent(parcelNumber)}`)

  if (!response.ok) {
    throw new Error(`Parcel ${parcelNumber} not found or API unavailable.`)
  }

  return (await response.json()) as ParcelResponse
}

export async function fetchOpportunities(params: URLSearchParams) {
  const response = await fetch(`${API_BASE_URL}/opportunities?${params.toString()}`)

  if (!response.ok) {
    throw new Error('Search request failed.')
  }

  return (await response.json()) as OpportunityResponse[]
}

export type Role = 'admin' | 'physician' | 'nurse' | 'staff' | 'lab_technician' | 'patient';

export interface AuthUser {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: number;
  patient_id?: number | null;
  username: string;
  role: Role;
}

export interface SystemUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: Role;
  patient_id?: number | null;
  is_active: boolean;
}

export interface FhirPatient {
  resourceType: 'Patient';
  id: string;
  identifier: Array<{ value: string }>;
  name: Array<{ given: string[]; family: string }>;
  birthDate: string;
  gender: string;
}

export interface Medication {
  id: number;
  patient_id: number;
  practitioner_id: number;
  drug_name: string;
  dosage: string;
  frequency: string;
  route: string;
  end_date?: string | null;
  indication?: string | null;
  status: string;
  start_date: string;
  created_at: string;
}

export interface LabTest {
  id: number;
  patient_id: number;
  practitioner_id: number;
  assigned_to?: number | null;
  collected_by?: number | null;
  received_by?: number | null;
  resulted_by?: number | null;
  verified_by?: number | null;
  test_name: string;
  test_code?: string;
  status: string;
  order_date: string;
  result_date?: string | null;
  sample_collected_at?: string | null;
  received_at?: string | null;
  verified_at?: string | null;
  released_at?: string | null;
  created_at: string;
}

export interface LabResult {
  id: number;
  lab_test_id: number;
  result_name: string;
  result_value: string;
  unit: string;
  reference_range: string;
  status: string;
}

export interface ClinicalDocument {
  id: number;
  patient_id: number;
  practitioner_id?: number;
  document_type: string;
  title: string;
  version: number;
  is_signed: boolean;
  created_at: string;
  updated_at: string;
}

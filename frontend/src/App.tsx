import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import AdminDashboard from './pages/admin/Dashboard';
import Reports from './pages/admin/Reports';
import Statistics from './pages/admin/Statistics';
import AdminUsers from './pages/admin/Users';
import Login from './pages/Login';
import Register from './pages/Register';
import UploadFile from './pages/UploadFile';
import Appointments from './pages/patient/Appointments';
import PatientDashboard from './pages/patient/Dashboard';
import PatientLabResults from './pages/patient/LabResults';
import PatientRecords from './pages/patient/MedicalRecords';
import PatientMedications from './pages/patient/Medications';
import PrescriptionInvoice from './pages/patient/PrescriptionInvoice';
import AddDocument from './pages/provider/AddDocument';
import ProviderDashboard from './pages/provider/Dashboard';
import ManageResults from './pages/provider/ManageResults';
import OrderTest from './pages/provider/OrderTest';
import PatientDetails from './pages/provider/PatientDetails';
import ProviderPatients from './pages/provider/PatientsList';
import PrescribeMedication from './pages/provider/PrescribeMedication';

const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<ProtectedRoute roles={['patient']} />}>
          <Route path="/patient/dashboard" element={<PatientDashboard />} />
          <Route path="/patient/records" element={<PatientRecords />} />
          <Route path="/patient/medications" element={<PatientMedications />} />
          <Route path="/patient/medications/:medicationId/invoice" element={<PrescriptionInvoice />} />
          <Route path="/patient/lab-results" element={<PatientLabResults />} />
          <Route path="/patient/appointments" element={<Appointments />} />
        </Route>

        <Route element={<ProtectedRoute roles={['admin', 'physician', 'nurse', 'staff', 'lab_technician', 'patient']} />}>
          <Route path="/upload" element={<UploadFile />} />
          <Route path="/appointments" element={<Appointments />} />
        </Route>

        <Route element={<ProtectedRoute roles={['physician', 'nurse', 'staff', 'admin']} />}>
          <Route path="/provider/dashboard" element={<ProviderDashboard />} />
          <Route path="/provider/patients" element={<ProviderPatients />} />
          <Route path="/provider/patient/:patientId" element={<PatientDetails />} />
          <Route path="/provider/patient/:patientId/add-document" element={<AddDocument />} />
          <Route path="/provider/patient/:patientId/prescribe" element={<PrescribeMedication />} />
          <Route path="/provider/patient/:patientId/order-test" element={<OrderTest />} />
        </Route>

        <Route element={<ProtectedRoute roles={['physician', 'nurse', 'staff', 'admin', 'lab_technician']} />}>
          <Route path="/provider/results" element={<ManageResults />} />
        </Route>

        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/users" element={<AdminUsers />} />
          <Route path="/admin/statistics" element={<Statistics />} />
          <Route path="/admin/reports" element={<Reports />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  </AuthProvider>
);

export default App;

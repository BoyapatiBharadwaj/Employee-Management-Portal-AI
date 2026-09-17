<Route path="*" element={<NotFound />} />
import { BrowserRouter, Routes, Route } from "react-router-dom";
import EmployeeSettings from "./pages/EmployeeSettings";
import Login from "./pages/Login";
import EmployeeDetails from "./pages/EmployeeDetails";
// Admin Pages
import Home from "./pages/Home";
import Performance from "./pages/Performance";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import Departments from "./pages/Departments";
import Attendance from "./pages/Attendance";
import Leave from "./pages/Leave";
import Payroll from "./pages/Payroll";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import AdminDocuments from "./pages/AdminDocuments";
// Employee Pages
import EmployeeDashboard from "./pages/EmployeeDashboard";
import EmployeeProfile from "./pages/EmployeeProfile";
import EmployeeAttendance from "./pages/EmployeeAttendance";
import EmployeePerformance from "./pages/EmployeePerformance";
import EmployeeLeave from "./pages/EmployeeLeave";
import EmployeePayroll from "./pages/EmployeePayroll";
import AIAssistant from "./pages/AIAssistant";
import ChangePassword from "./pages/ChangePassword";
import Onboarding from "./pages/Onboarding";
// Components
import AdminRoute from "./components/AdminRoute";
import EmployeeRoute from "./components/EmployeeRoute";
import ManagerRoute from "./components/ManagerRoute";
import Offboarding from "./pages/Offboarding";
// Others
import NotFound from "./pages/NotFound";
import EditProfile from "./pages/EditProfile";
import ResumeAnalyzer from "./pages/hr/ResumeAnalyzer";
import Analytics from "./pages/Analytics";
import Notifications from "./pages/Notifications";
import HRAssistant from "./pages/HRAssistant";
import SentimentAnalysis from "./pages/SentimentAnalysis";
import SemanticSearch from "./pages/SemanticSearch";
import HierarchyManagement from "./pages/HierarchyManagement";
import EmployeeMonthlyPerformance from "./pages/EmployeeMonthlyPerformance";
import ManagerPerformance from "./pages/ManagerPerformance";
import PerformanceInsights from "./pages/PerformanceInsights";
function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Login */}
     <Route path="/" element={<Home />} />
<Route path="/login" element={<Login />} />

        {/* ================= ADMIN ROUTES ================= */}

        <Route
          path="/dashboard"
          element={
            <AdminRoute>
              <Dashboard />
            </AdminRoute>
          }
        />

        <Route
          path="/employees"
          element={
            <AdminRoute>
              <Employees />
            </AdminRoute>
          }
        />

        <Route
          path="/departments"
          element={
            <AdminRoute>
              <Departments />
            </AdminRoute>
          }
        />

        <Route
          path="/attendance"
          element={
            <AdminRoute>
              <Attendance />
            </AdminRoute>
          }
        />

        <Route
          path="/leave"
          element={
            <AdminRoute>
              <Leave />
            </AdminRoute>
          }
        />

        <Route
          path="/payroll"
          element={
            <AdminRoute>
              <Payroll />
            </AdminRoute>
          }
        />
        <Route
  path="/performance"
  element={
    <AdminRoute>
      <Performance />
    </AdminRoute>
  }
/>
        <Route path="/hierarchy-management" element={<AdminRoute><HierarchyManagement /></AdminRoute>} />
        <Route path="/performance-insights" element={<AdminRoute><PerformanceInsights /></AdminRoute>} />
        <Route
  path="/documents"
  element={
    <AdminRoute>
      <AdminDocuments />
    </AdminRoute>
  }
/>
        <Route
          path="/reports"
          element={
            <AdminRoute>
              <Reports />
            </AdminRoute>
          }
        />

        <Route
    path="/analytics"
    element={
        <AdminRoute>
            <Analytics />
        </AdminRoute>
    }
/>

<Route
    path="/notifications"
    element={
        <AdminRoute>
            <Notifications />
        </AdminRoute>
    }
/>
        <Route
  path="/resume-analyzer"
  element={
    <AdminRoute>
      <ResumeAnalyzer />
    </AdminRoute>
  }
/>

<Route
  path="/hr-ai"
  element={
    <AdminRoute>
      <HRAssistant />
    </AdminRoute>
  }
/>

        <Route
          path="/profile"
          element={
            <AdminRoute>
              <Profile />
            </AdminRoute>
          }
        />
        <Route
    path="/change-password"
    element={
        <AdminRoute>
            <ChangePassword />
        </AdminRoute>
    }
/>
<Route
    path="/edit-profile"
    element={
        <AdminRoute>
            <EditProfile />
        </AdminRoute>
    }
/>
        <Route
          path="/settings"
          element={
            <AdminRoute>
              <Settings />
            </AdminRoute>
          }
        />

        {/* ================= EMPLOYEE ROUTES ================= */}

        <Route
          path="/employee/dashboard"
          element={
            <EmployeeRoute>
              <EmployeeDashboard />
            </EmployeeRoute>
          }
        />

        <Route
          path="/employee/profile"
          element={
            <EmployeeRoute>
              <EmployeeProfile />
            </EmployeeRoute>
          }
        />

        <Route
          path="/employee/attendance"
          element={
            <EmployeeRoute>
              <EmployeeAttendance />
            </EmployeeRoute>
          }
        />

        <Route
          path="/employee/performance"
          element={
            <EmployeeRoute>
              <EmployeePerformance />
            </EmployeeRoute>
          }
        />
        <Route path="/manager/performance" element={<ManagerRoute><ManagerPerformance /></ManagerRoute>} />
        <Route path="/employee/monthly-performance" element={<EmployeeRoute><EmployeeMonthlyPerformance /></EmployeeRoute>} />

        <Route
          path="/employee/leave"
          element={
            <EmployeeRoute>
              <EmployeeLeave />
            </EmployeeRoute>
          }
        />

        <Route
          path="/employee/payroll"
          element={
            <EmployeeRoute>
              <EmployeePayroll />
            </EmployeeRoute>
          }
        />
        <Route
    path="/employee/ai"
    element={
        <EmployeeRoute>
            <AIAssistant />
        </EmployeeRoute>
    }
/>
<Route
    path="/onboarding"
    element={
        <AdminRoute>
            <Onboarding />
        </AdminRoute>
    }
/>
<Route
    path="/offboarding"
    element={
        <AdminRoute>
            <Offboarding />
        </AdminRoute>
    }
/>
<Route
    path="/sentiment"
    element={
        <AdminRoute>
            <SentimentAnalysis />
        </AdminRoute>
    }
/>

<Route
    path="/semantic-search"
    element={
        <AdminRoute>
            <SemanticSearch />
        </AdminRoute>
    }
/>
<Route
    path="/employee/settings"
    element={
        <EmployeeRoute>
            <EmployeeSettings />
        </EmployeeRoute>
    }
/>
<Route
    path="/employee/details"
    element={
        <EmployeeRoute>
            <EmployeeDetails />
        </EmployeeRoute>
    }
/>

        {/* 404 */}
        <Route path="*" element={<NotFound />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
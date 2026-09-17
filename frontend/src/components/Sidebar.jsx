import { Link, useLocation, useNavigate } from "react-router-dom";

import {
  FaTachometerAlt,
  FaUsers,
  FaBuilding,
  FaCalendarCheck,
  FaPlaneDeparture,
  FaMoneyCheckAlt,
  FaChartBar,
  FaSignOutAlt,
  FaUserCircle,
  FaCog,
  FaUserPlus,
  FaStar,
  FaFileAlt,
  FaRobot,
  FaBell,
  FaChartPie,
  FaSmile,
  FaSearch,
} from "react-icons/fa";

import { FaUserMinus } from "react-icons/fa";

function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    navigate("/");
  };

  const menuItems = [
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: <FaTachometerAlt />,
    },
    {
      name: "Employees",
      path: "/employees",
      icon: <FaUsers />,
    },
    {
      name: "Departments",
      path: "/departments",
      icon: <FaBuilding />,
    },
    {
      name: "Attendance",
      path: "/attendance",
      icon: <FaCalendarCheck />,
    },
    {
      name: "Leave",
      path: "/leave",
      icon: <FaPlaneDeparture />,
    },
    {
      name: "Payroll",
      path: "/payroll",
      icon: <FaMoneyCheckAlt />,
    },
    {
      name: "Documents",
      path: "/documents",
      icon: <FaFileAlt />,
    },
    {
      name: "Performance",
      path: "/performance",
      icon: <FaStar />,
    },
    {
      name: "Hierarchy Management",
      path: "/hierarchy-management",
      icon: <FaUsers />,
    },
    {
      name: "Performance Insights",
      path: "/performance-insights",
      icon: <FaChartBar />,
    },
    {
      name: "Onboarding",
      path: "/onboarding",
      icon: <FaUserPlus />,
    },
    {
      name: "Offboarding",
      path: "/offboarding",
      icon: <FaUserMinus />,
    },
    {
      name: "Reports",
      path: "/reports",
      icon: <FaChartBar />,
    },
    {
      name: "Resume AI",
      path: "/resume-analyzer",
      icon: <FaRobot />,
    },
    {
      name: "Sentiment Analysis",
      path: "/sentiment",
      icon: <FaSmile />,
    },
    {
      name: "AI HR Assistant",
      path: "/hr-ai",
      icon: <FaRobot />,
    },
    {
      name: "Analytics",
      path: "/analytics",
      icon: <FaChartPie />,
    },
    {
      name: "Notifications",
      path: "/notifications",
      icon: <FaBell />,
    },
    {
      name: "Profile",
      path: "/profile",
      icon: <FaUserCircle />,
    },

    {
    name: "Semantic Search",
    path: "/semantic-search",
    icon: <FaSearch />,
    },

    {
      name: "Settings",
      path: "/settings",
      icon: <FaCog />,
    },
  ];

  return (
    <div
      className="bg-dark text-white d-flex flex-column"
      style={{
        width: "260px",
        minHeight: "100vh",
      }}
    >
      <div className="text-center py-4 border-bottom">
        <h3 className="fw-bold">
          EMP Portal
        </h3>

        <small className="text-secondary">
          Employee Management
        </small>
      </div>

      <ul className="nav flex-column mt-3">
        {menuItems.map((item) => (
          <li key={item.path} className="nav-item">
            <Link
              to={item.path}
              className={`nav-link d-flex align-items-center px-4 py-3 ${
                location.pathname === item.path
                  ? "bg-primary text-white"
                  : "text-light"
              }`}
            >
              <span className="me-3 fs-5">
                {item.icon}
              </span>

              {item.name}
            </Link>
          </li>
        ))}
      </ul>

      <div className="mt-auto p-3">
        <button
          className="btn btn-danger w-100"
          onClick={logout}
        >
          <FaSignOutAlt className="me-2" />
          Logout
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
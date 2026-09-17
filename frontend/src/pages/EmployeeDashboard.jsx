import { useEffect, useState } from "react";

import EmployeeLayout from "../components/EmployeeLayout";

import WelcomeBanner from "../components/dashboard/WelcomeBanner";
import StatCards from "../components/dashboard/StatCards";
import AttendanceCard from "../components/dashboard/AttendanceCard";
import PerformanceCard from "../components/dashboard/PerformanceCard";
import AnnouncementCard from "../components/dashboard/AnnouncementCard";

import {
    getEmployeeDashboard
} from "../services/employeeDashboardService";

function EmployeeDashboard() {

    const [dashboard, setDashboard] = useState(null);

    useEffect(() => {

        loadDashboard();

    }, []);

    async function loadDashboard() {

        try {

            const data = await getEmployeeDashboard();

            setDashboard(data);

        }

        catch (error) {

            console.log(error);

        }

    }

    if (!dashboard) {

        return (

            <EmployeeLayout>

                <div className="text-center mt-5">

                    <div
                        className="spinner-border text-primary"
                    ></div>

                    <h5 className="mt-3">

                        Loading Dashboard...

                    </h5>

                </div>

            </EmployeeLayout>

        );

    }

    return (

        <EmployeeLayout>

            {/* Welcome Banner */}

            <WelcomeBanner

                employee={dashboard.employee}

            />

            {/* Summary Cards */}

            <StatCards

                dashboard={dashboard}

            />

            <div className="card border-0 shadow-sm mt-4">
                <div className="card-body">
                    <div className="text-muted small">Current Superior / Reporting Manager</div>
                    <div className="fw-bold fs-5 mt-1">
                        {dashboard.employee?.superior?.name || "No Superior Assigned"}
                    </div>
                    {dashboard.employee?.superior?.email && (
                        <div className="text-muted">{dashboard.employee.superior.email}</div>
                    )}
                </div>
            </div>

            {/* Today's Attendance */}

            <div className="mt-4">

                <AttendanceCard

                    attendance={dashboard.today_attendance}

                />

            </div>

            {/* Performance */}

            <div className="mt-4">

                <PerformanceCard />

            </div>

            {/* Company Announcements */}

            <div className="mt-4">

                <AnnouncementCard />

            </div>

        </EmployeeLayout>

    );

}

export default EmployeeDashboard;
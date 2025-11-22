<!-- Copilot: Generate a detailed README for this project including installation, usage, and examples -->
Robot Architecture Documentation
1. Introduction
    This document provides a comprehensive overview of the robot's modular architecture,
    detailing its core components, inter-module communication, and the specific APIs for both
    the web and mobile applications. The goal is to create a clear and maintainable reference for
    all development teams.
2. Overall Architecture
    The robot's architecture is built on a modular design principle, allowing for independent
    development, testing, and scaling of each component. The core logic is separated from the
    user interfaces (web and app) through distinct API layers.
    ●​ Figma Design: The user interface and flow for both the web and mobile applications are
    visually represented in Figma. This document serves as the technical blueprint behind
    those designs.
    ●​ Communication Protocol: A key architectural decision is the extensive use of
    webhooks and WebSockets. This design choice makes continuous API polling
    unnecessary, which is crucial for reducing system load and improving real-time
    performance. Events from the robot are pushed to the relevant clients, ensuring efficient
    and timely data transfer.
3. Module Breakdown
3.1. Website Modules
    ●​ Login:
        ○​ Description: This module handles user authentication and session management. It is
        the entry point for all users, including administrators and nurses. It uses a username
        and password combination for credential verification.
        ○​ Responsibilities:
        ■​ User credential validation against the database.
        ■​ Generation of a JSON Web Token (JWT) upon successful login.
        ■​ Session management and token refreshing to maintain user sessions.
        ■​ User role assignment (Admin or Nurse) based on the authenticated user's profile.
        ○​ Inputs/Outputs:
        ■​ Inputs: Username (string), Password (string).
        ■​ Outputs: A JSON object containing a JWT token and user details (name, email,
        role, etc.).
    Privilege Management:
        ○​ Description: This module is responsible for defining, storing, and enforcing access
        control policies based on user roles. It ensures that users can only access the
        functionalities and data appropriate for their assigned roles (Admin or Nurse), and it
        applies these privileges to all users within a given role, not on a per-user basis.
        ○​ Responsibilities:
        ■​ Defining granular permissions that apply to the entire Admin role.
        ■​ Defining granular permissions that apply to the entire Nurse role.
        ■​ Checking a user's role and applying the corresponding permissions before
        granting access.
        ■​ Privilege Data Model: Privileges are stored in a database using a model similar
        to the PrivilegeModel class. Each record defines a specific privilege via a code
        and uses boolean flags (allow_admin, allow_nurse) to determine access for each
        user role. This ensures a clear and extensible system for managing permissions.
        ○​ Inputs/Outputs: [Describe the data or signals.]
        Video Management:
        ○​ Description: This module serves as a demonstration and management tool for
        displaying multimedia content. It can host both videos and images, and the content
        can be reordered by users via a drag-and-drop interface on the website.
        ○​ Responsibilities:
        ■​ Storing and managing metadata for video and image files.
        ■​ Handling uploads of both videos and images, either via a direct file upload or a
        URL.
        ■​ Maintaining the order of the media items, allowing for reordering by a privileged
        user.
        ■​ Tracking the active status of each media item.
        ■​ Associating each media item with the user who created or last updated it.
        ○​ Inputs/Outputs:
        ■​ Inputs: Media file (.mp4, .jpeg, etc.) or URL, video_name (string), is_image
        (boolean), is_active (boolean).
        ■​ Outputs: A list of media objects (images/videos) with their respective URLs and
        metadata, presented in a user-defined order.
        ○​ Data Model: The module uses a data model similar to the VideoManagementModel
        class, which handles fields for video_name, video_image_url, video_image_file,
        is_image, and timestamps for creation and updates.
        Room and Bed Management:○​ Description: This module is responsible for the digital mapping and management of
        physical spaces within the hospital. It creates a virtual representation of rooms, beds,
        and key navigation points that the robot uses for localization and task execution. The
        room and bed lists can only be incremented and not decremented.
    ○​ Responsibilities:
        ■​ Defining and storing a static, incremental list of rooms.
        ■​ Defining and storing a static, incremental list of beds.
        ■​ Creating and managing "slots," which represent a specific bed within a room.
        ■​ Storing physical coordinates (x, y, yaw) for each slot.
        ■​ Storing entry and exit points for each room for robot navigation.
        ■​ Handling real-time location updates from the robot to populate coordinate data.
    ○​ Workflow:
        ■​ A web interface allows for the manual creation of rooms and beds.
        ■​ A tablet on the robot, running a web browser, accesses this interface.
        ■​ The tablet communicates with a webhook on the Jetson. When a user marks a
        location, the robot's onboard SLAM system determines its coordinates.
        ■​ The Jetson forwards this location data to the database, populating the x, y, and
        yaw fields for a slot or room position.
    ○​ Data Models:
        ■​ RoomDataModel: Manages the list of rooms. It includes a unique room_name and
        tracks its active status, creation, and last update. Rooms can only be added, not
        removed.
        ■​ BedDataModel: Manages the list of beds. It includes a unique bed_name and also
        only allows for new entries to be added, not removed.
        ■​ SlotDataModel: This model represents the core association of a bed to a room. It
        contains foreign keys to RoomDataModel and BedDataModel, and stores the
        physical coordinates (x, y, yaw) for a specific bed within a room. A unique
        constraint ensures that a single bed cannot be assigned to multiple rooms.
        ■​ RoomPositionModel: Stores the entry and exit coordinates (x, y, yaw) for each
        room, serving as navigational points for the robot. A unique constraint ensures
        that each room has only one defined set of entry and exit points.
    ●​ Schedulers:
        ○​ Description: This module handles the creation and management of recurring
        schedules for the robot's tasks, such as patient rounds. It allows for the definition of
        "batches" that are assigned to specific days and times. Furthermore, it enables the
        assignment of individual patients to these batches, with the ability to reorder them to
        dictate the robot's sequence of visits.
    ○​ Responsibilities:
        ■​ Creating and managing scheduled "batches" with specific time slots and days of
        the week.
        ■​ Assigning patients to defined batches.
        ■​ Maintaining and allowing for reordering of the patient list within a batch to set
        the robot's visitation order.■​ Tracking the status of a batch, including its scheduled time and completion
        status.
    ○​ Data Models:
        ■​ BatchScheduleModel: This model defines a reusable schedule or "batch." It
        specifies a time_slot (e.g., morning, afternoon) and includes boolean flags for
        each day of the week to create a recurring schedule. It also stores a trigger_time
        and various status flags to manage the batch's execution.
        ■​ ScheduledSlots: This model links a specific patient to a BatchScheduleModel. It is
        used to assign a patient to a particular batch. The order in which these slots are
        managed can be manually rearranged by the user via the website's interface,
        which is crucial for determining the robot's visitation sequence.
        ●​ Patients and Apparatus Value:
        ○​ Description: This module is designed to collect and store patient vital sign data from
        a connected apparatus. It links this data to specific patients and provides a way to
        store visual information, such as screenshots from a tablet or images from a camera.
    ○​ Responsibilities:
        ■​ Storing blood pressure readings (sys, dia, map) and pulse rate.
        ■​ Associating the readings with a specific patient using a foreign key.
        ■​ Handling the upload and storage of two distinct types of images: screenshots
        from the web tablet and images from an onboard camera.
        ■​ Linking all collected data to the user who created the record and logging
    timestamps.
        ○​ Data Model: The Bp2CheckMeModel is the primary data model for this module. It
        includes fields for the various vital signs and two separate fields for image storage,
        using URLField and FileField pairs to handle both remote and local files. The model's
        design allows for flexible data capture from various sources.
    ●​ IP management:
        ○​ Description: This module manages the local IP and port for the robot's internal
        network. It is crucial for enabling local communication between the robot's onboard
        tablet and the Jetson, which is necessary for tasks like marking and sending
        coordinates from the tablet's web interface.
        ○​ Responsibilities: Storing the local IP address and port.Providing this information to
        the web interface on the tablet for communication with the Jetson via webhooks.
        ○​ Data Model: The LocalIpModel is used to store a unique local_ip_add and
        port for the robot's local network.
    ○​ Inputs/Outputs:
        ■​ Inputs: Local IP address (string), port number (integer).
        ■​ Outputs: The stored IP and port information, used by the tablet for local
        communication.
    ●​ Alerts:
    ○​ Description: This module manages all patient-initiated alerts. It provides a real-time
        log of help requests from the robot's tablet, allowing nurses to respond promptly. The
        system also handles the popup timeout for alerts, which is defined in this module.○​ Data Model: AlertHistory: This model stores a history of all patient-triggered
        alerts. It includes fields for the room and bed from which the alert originated, a
        reason, and various boolean flags to track the status of the alert (is_help,
        is_timed_out, is_cancelled, not_me, is_patient_pop).
    ○​ Responsibilities:
        ■​ Logging and tracking alerts sent by patients (e.g., when a patient clicks a "help"
        button).
        ■​ Monitoring and recording the status of these alerts (e.g., responded, timed out,
        etc.).
        ■​ Providing a clear, filterable history of all alerts.
    3.2. Robot Arm Telemetry System
        Thefunctionality and purpose of the provided models (ArmEndpose, JointVelocity,
        JointEffort, JointPosition, ArmStatus, and JointStatus) which are designed for
        monitoring and managing a robotic arm. These models provide a comprehensive set of data
        points, from the arm's physical location to the detailed status of each individual joint.
        Purpose for Web-Based Monitoring and Visualization
        The models are essential for creating a rich, web-based dashboard that allows operators to
        visualize and understand the state of the robotic arm in real time. The data from ArmEndpose
        (x, y, z, rx, ry, rz) can be used to generate a 3D graphical representation of the arm's position
        and orientation on the screen. This provides an intuitive and immediate understanding of
        where the arm is located in its workspace.
        The ArmStatus and JointStatus models are crucial for providing real-time operational
        health. Operators can view high-level status indicators (arm_status, motion_status) and
        quickly identify potential issues such as motor_overheating or a driver_error_status.
        The timestamps associated with each status field are particularly important, allowing for a
        historical log of when specific events occurred, which is vital for diagnostics and
        troubleshooting.
        Data Display and Interactive Interface
        The data from these models is intended for presentation in a variety of formats on a web
    interface:
        ●​ 3D Visualization: The ArmEndpose data is used to render the arm's position and
        orientation in a 3D viewer. This allows for live, interactive manipulation and observation
        of the arm's state.
        ●​ Tabular Data: A dashboard can display JointVelocity, JointEffort, andJointPosition in a tabular format, providing a quick way to view the numerical
        values for all six joints.
        ●​ Graphs and Charts: The time-series nature of the data (due to the updated_at
        field) lends itself well to graphing. Historical data for joint velocities or motor
        temperatures can be plotted over time to analyze performance trends or diagnose
        intermittent issues.
        Data Exchange with a Jetson Device
        All of the provided models are designed for a system where a Jetson-based device on the
        robot arm is the primary data source. The Jetson, equipped with sensors and control
        software, continuously streams telemetry data to a central server. The model fields are
        updated in real-time with information coming directly from the robot.
        The save method logic in ArmStatus and JointStatus is particularly relevant to this data
        exchange. By checking for changes in a field's value before updating its timestamp, the
        system only records a new timestamp when an actual state change has occurred. This
        provides a clean, event-driven log of the arm's status history, making it easy to see the
        sequence of events that led to a particular state (e.g., an overcurrent event followed by an
        arm status change). This architectural pattern ensures that the web interface is not just
        showing the arm's current state, but also a detailed history of its recent behavior.
    3.3. FastAPI Webhook System
        This report provides an in-depth analysis of the provided FastAPI application, which is
        designed to act as a webhook receiver and a data forwarding service for a mobile medical
        robot system. The application serves as a critical intermediary, handling incoming requests
        from a tablet and processing them before communicating with a core API.
        Core Functionality
        The primary function of this application is to serve as a set of webhook endpoints that listen
        for specific events triggered by a tablet or a similar client device. Upon receiving a request,
        the application validates the payload, generates or forwards necessary data, and then sends
        a new request to a separate, internal API. This architecture offloads processing from the
        tablet and ensures a standardized communication flow within the robotic ecosystem.
    The application is built with:
        ●​ FastAPI: A modern, high-performance web framework for building APIs.
        ●​ Uvicorn: An ASGI server for running the FastAPI application.
        ●​ Starlette's CORS Middleware: To allow cross-origin requests, ensuring the tablet'sfront-end can communicate with the server without security issues.
        ●​ httpx: An asynchronous HTTP client used to forward requests to the main API,
        preventing the application from blocking while waiting for a response.
        Endpoint Breakdown
    The system is composed of several distinct webhook endpoints, each serving a specific
    purpose:
    1. POST /webhook/trigger-slot-position/
        This endpoint receives a webhook when a new "slot" position needs to be created. It expects
        a JSON payload containing slot_id. Upon successful reception, it generates random x, y,
        and yaw coordinates and forwards this complete payload to the
        create_slot_position_api.
    2. POST /webhook/create-room-entry-position/ and POST
        /webhook/create-room-exit-position/
        These endpoints are designed to register entry and exit points for a room. They both expect a
        room_pos_id in the JSON payload. Similar to the slot position endpoint, they generate mock
        x, y, and yaw coordinates before forwarding the request to their respective APIs:
        create_room_entry_position_api and create_room_exit_position_api. This
        process is essential for mapping and navigation within the robot's environment.
    3. POST /webhook/scheduled-data/
        This endpoint is intended to receive scheduled task data from the tablet. It expects a
        scheduled_data field in the payload. The application's current function is to receive this
        data, print it to the console, and return a success response, indicating it has successfully
        received the schedule.
    4. POST /webhook/skip-slot/
        This is a critical operational endpoint for managing the robot's tasks. It receives a reason
        from the tablet, which can be one of several predefined values (timeout, help, not_me,
        confirm, patient-completed). Based on the reason, the system can trigger different
        actions, such as skipping a task slot, confirming a patient, or starting camera detection for
        OCR.
    5. POST /webhook/demo-shown-completed/
        This endpoint is triggered when a patient has completed a demonstration or tutorial on the
        tablet. It expects a patient_id and, as indicated by the code's comments, is designed to
        initiate camera detection to verify the patient's actions or start a new process. The endpointreturns a success message confirming the action has been triggered.
        System Integration and Data Flow
        The architecture suggests a three-part system:
        1.​ Tablet/Client: The user-facing interface that triggers the webhooks.
        2.​ FastAPI Webhook Server: This intermediary application that receives, processes, and
        forwards data.
        3.​ Core API (192.168.1.33:8000): The central brain of the system, responsible for
        handling core logic, database operations, and robot control.
        Data flows from the tablet to the FastAPI server via a webhook, and from there it is
        asynchronously forwarded to the core API. This separation of concerns ensures that the
        webhook server remains lightweight and responsive, while the main API can focus on complex
        tasks without being burdened by direct client communication.

Medical Bot API Documentation
Overview
This API provides comprehensive management capabilities for a medical robot system, including bed
management, patient scheduling, robot control, video management, and vital signs monitoring.
Base URL: Not specified in schema
Authentication: JWT Bearer Token
API Version: 0.0.0
Authentication
Most endpoints require JWT authentication using the Bearer token scheme:
Authorization: Bearer <your-jwt-token>
Some endpoints allow anonymous access (marked as {} in security schemes).
API Endpoints by Category

🏥 Bed Management
    Get All Beds
        Endpoint: GET /api/medicalbot/bed/data/bed/all/
        Authentication: Required
        Description: Retrieves all bed information
        Response: 200 - Success
    Create Bed
        Endpoint: POST /api/medicalbot/bed/data/bed/create/
        Authentication: Required
        Description: Creates a new bed entry
        Response: 200 - Success
    Get All Rooms
        Endpoint: GET /api/medicalbot/bed/data/room/all/
        Authentication: Required
        Description: Retrieves all room information
        Response: 200 - Success
    Create Room
        Endpoint: POST /api/medicalbot/bed/data/room/create/
        Authentication: Required
        Description: Creates a new room entry
        Response: 200 - Success
    Create Room Entry Point Position
        Endpoint: POST /api/medicalbot/bed/data/room/entry-point/position/create/
        Authentication: Optional
        Description: Sets the entry point position for a room
        Response: 200 - Success
    Create Room Exit Point Position
        Endpoint: POST /api/medicalbot/bed/data/room/exit-point/position/create/
        Authentication: Optional
        Description: Sets the exit point position for a room
        Response: 200 - Success
    Activate Room Position
        Endpoint: DELETE /api/medicalbot/bed/data/room/position/activate/{id}/
        Authentication: Required
        Parameters: id (integer, path) - Position ID
        Response: 204 - No Content
    View Room Position
        Endpoint: GET /api/medicalbot/bed/data/room/position/view/
        Authentication: Required
        Description: Retrieves room position informationResponse: 200 - Success

🛏️ Slot Management
    Get Active Slots
        Endpoint: GET /api/medicalbot/bed/data/slot/active/
        Authentication: Required
        Description: Retrieves all active time slots
        Response: 200 - Success
    Get All Slots
        Endpoint: GET /api/medicalbot/bed/data/slot/all/
        Authentication: Required
        Description: Retrieves all time slots
        Response: 200 - Success
    Create Slot
        Endpoint: POST /api/medicalbot/bed/data/slot/create/
        Authentication: Required
        Description: Creates a new time slot
        Response: 200 - Success
    Delete Slot
        Endpoint: DELETE /api/medicalbot/bed/data/slot/delete/{slot_id}/
        Authentication: Required
        Parameters: slot_id (integer, path) - Slot ID to delete
        Response: 204 - No Content
    Create Slot Position
        Endpoint: POST /api/medicalbot/bed/data/slot/position/create/
        Authentication: None
        Description: Creates position data for a slot
        Response: 200 - Success User Management

    Login
        Endpoint: POST /api/medicalbot/main/login/
        Authentication: None
        Description: User authentication endpoint
        Response: 200 - Success
    Create Admin
        Endpoint: POST /api/medicalbot/main/create-admin/
        Authentication: Required
        Description: Creates a new admin user
        Response: 200 - Success
    Create Patient
        Endpoint: POST /api/medicalbot/main/create-patient/
        Authentication: Required
        Description: Creates a new patient record
        Response: 200 - Success
    Delete Admin
        Endpoint: DELETE /api/medicalbot/main/delete-admin/{user_id}/
        Authentication: Required
        Parameters: user_id (integer, path) - Admin user ID
        Response: 204 - No Content
    Delete Patient
        Endpoint: DELETE /api/medicalbot/main/delete-patient/{patient_id}/
        Authentication: Required
        Parameters: patient_id (integer, path) - Patient ID
        Response: 204 - No ContentDelete All Patients
        Endpoint: GET /api/medicalbot/main/delete-all-patient/
        Authentication: Required
        Description: Removes all patient records
        Response: 200 - Success
    View All Admins
        Endpoint: GET /api/medicalbot/main/view-all-admin/{role}/
        Authentication: Required
        Parameters: role (string, path) - Admin role filter
        Response: 200 - Success
    View All Patients
        Endpoint: GET /api/medicalbot/main/view-all-patient/
        Authentication: Required
        Description: Retrieves all patient records
        Response: 200 - Success
    Assign Bed to Room
        Endpoint: POST /api/medicalbot/main/assign-bed-room/
        Authentication: Required
        Description: Assigns a bed to a specific room
        Response: 200 - Success

📊 Data Import/Export
    Export Patients to Excel
        Endpoint: GET /api/medicalbot/main/export_patients_excel/
        Authentication: Optional
        Description: Exports patient data to Excel format
        Response: 200 - Success
    Import Patients from Excel
        Endpoint: POST /api/medicalbot/main/import_patients_excel/
        Authentication: Optional
        Description: Imports patient data from Excel file
        Response: 200 - Success

🔐 Privilege Management
    Create Privilege
        Endpoint: POST /api/medicalbot/privilege/create-privilege/
        Authentication: Required
        Description: Creates new user privileges
        Response: 200 - Success
    View All Privileges
        Endpoint: GET /api/medicalbot/privilege/view-all-privilege/
        Authentication: Required
        Description: Retrieves all system privileges
        Response: 200 - Success

🤖 Robot Management
    Get Robot Telemetry
        Endpoint: GET /api/medicalbot/robot_management/all-robot-telemetry/
        Authentication: Optional
        Description: Retrieves comprehensive robot telemetry data
        Response: 200 - Success
    Save Map Telemetry
        Endpoint: POST /api/medicalbot/robot_management/save-map-telemetry/
        Authentication: Optional
        Description: Upload STCM file, convert to PNG, and save into RobotTelemetry.robot_image_file.
        Falls back to auto-detected grid size if header and payload mismatch.Response: 200 - Success
    Get Patient Data
        Endpoint: GET /api/medicalbot/robot_management/get-patient-data/{patient_id}/
        Authentication: Optional
        Parameters: patient_id (integer, path) - Patient ID
        Response: 200 - Success
    Get Room Entry Coordinates
        Endpoint: GET /api/medicalbot/robot_management/get-room_entry_cord/{room}/
        Authentication: Optional
        Parameters: room (string, path) - Room identifier
        Response: 200 - Success
    Get Room Exit Coordinates
        Endpoint: GET /api/medicalbot/robot_management/get-room_exit_cord/{room}/
        Authentication: Optional
        Parameters: room (string, path) - Room identifier
        Response: 200 - Success
    Get Slot Coordinates
        Endpoint: GET /api/medicalbot/robot_management/get-slot_cord/{room}/{bed}/
        Authentication: Optional
        Parameters:
        room (string, path) - Room identifier
        bed (string, path) - Bed identifier
        Response: 200 - Success
    Fetch Latest Slot
        Endpoint: GET /api/medicalbot/robot_management/fetch-latest-slot/
        Authentication: Optional
        Description: Retrieves the most recent slot information
        Response: 200 - Success🦾 Robot Arm Control
    Get Arm End Pose
        Endpoint: GET /api/medicalbot/robot_management/arm-endpose/
        Authentication: Optional
        Description: Retrieves current arm end effector position
        Response: 200 - Success
    Update Arm End Pose
        Endpoint: PUT /api/medicalbot/robot_management/arm-endpose/
        Authentication: Optional
        Description: Updates arm end effector position
        Response: 200 - Success
    Get Arm Status
        Endpoint: GET /api/medicalbot/robot_management/get-arm-status/
        Authentication: Optional
        Description: Retrieves current arm status
        Response: 200 - Success
    Create/Update Arm Status
        Endpoint: POST /api/medicalbot/robot_management/create-update-arm-status/
        Authentication: Optional
        Description: Creates or updates arm status information
        Response: 200 - Success

⚙️ Joint Control
    Get Joint Position
        Endpoint: GET /api/medicalbot/robot_management/joint-position/
        Authentication: Optional
        Description: Retrieves current joint positionsResponse: 200 - Success
    Update Joint Position
        Endpoint: PUT /api/medicalbot/robot_management/joint-position/
        Authentication: Optional
        Description: Updates joint positions
        Response: 200 - Success
    Get Joint Velocity
        Endpoint: GET /api/medicalbot/robot_management/joint-velocity/
        Authentication: Optional
        Description: Retrieves current joint velocities
        Response: 200 - Success
    Update Joint Velocity
        Endpoint: PUT /api/medicalbot/robot_management/joint-velocity/
        Authentication: Optional
        Description: Updates joint velocities
        Response: 200 - Success
    Get Joint Effort
        Endpoint: GET /api/medicalbot/robot_management/joint-effort/
        Authentication: Optional
        Description: Retrieves current joint efforts/torques
        Response: 200 - Success
    Update Joint Effort
        Endpoint: PUT /api/medicalbot/robot_management/joint-effort/
        Authentication: Optional
        Description: Updates joint efforts/torques
        Response: 200 - Success
    Get Joint Status
        Endpoint: GET /api/medicalbot/robot_management/get-joint-status/
        Authentication: Optional
        Description: Retrieves overall joint status
        Response: 200 - Success
    Create/Update Joint Status
        Endpoint: POST /api/medicalbot/robot_management/create-update-joint-status/
        Authentication: Optional
        Description: Creates or updates joint status information
        Response: 200 - Success

🚨 Alert Management
    Get All Alerts
        Endpoint: GET /api/medicalbot/robot_management/alerts/
        Authentication: Optional
        Description: Retrieves all system alerts
        Response: 200 - Success
    Get Active Alerts
        Endpoint: GET /api/medicalbot/robot_management/active/alerts/
        Authentication: Optional
        Description: Retrieves only active alerts
        Response: 200 - Success
    Update Alert Reason
        Endpoint: PATCH /api/medicalbot/robot_management/alerts/{id}/update-reason/
        Authentication: Optional
        Parameters: id (integer, path) - Alert ID
        Response: 200 - Success
    Respond to Help Request
        Endpoint: GET /api/medicalbot/robot_management/respond-help/{alert_id}/{rsp}/Authentication: Optional
        Parameters:
        alert_id (integer, path) - Alert ID
        rsp (integer, path) - Response code
        Response: 200 - Success
    Save Help Data
        Endpoint: POST /api/medicalbot/robot_management/save-help-data/
        Authentication: Optional
        Description: Saves help request information
        Response: 200 - Success

📅 Schedule Management
    Add Batch Schedule
        Endpoint: POST /api/medicalbot/schedule/add-batch-schedule/
        Authentication: Required
        Description: Creates multiple schedules in batch
        Response: 200 - Success
    Update Batch Schedule
        Endpoint: PUT /api/medicalbot/schedule/add-batch-schedule/
        Authentication: Required
        Description: Updates existing batch schedules
        Response: 200 - Success
    Check Scheduled Slot
        Endpoint: POST /api/medicalbot/schedule/check-scheduled-slot/
        Authentication: Required
        Description: Verifies slot availability
        Response: 200 - Success
    Schedule Slots
        Endpoint: PUT /api/medicalbot/schedule/schedule-slots/
        Authentication: Required
        Description: Assigns schedules to time slots
        Response: 200 - Success
    Swap Scheduled Slots
        Endpoint: POST /api/medicalbot/schedule/swap/scheduled/slots/
        Authentication: Required
        Description: Exchanges two scheduled slots
        Response: 200 - Success
    View All Active Batch Schedules
        Endpoint: GET /api/medicalbot/schedule/view-all-active-batch-schedule/
        Authentication: Required
        Description: Retrieves all currently active batch schedules
        Response: 200 - Success
    View All Batch Schedules
        Endpoint: GET /api/medicalbot/schedule/view-all-batch-schedule/
        Authentication: Required
        Description: Retrieves all batch schedules
        Response: 200 - Success
    View All Scheduled Slots
        Endpoint: GET /api/medicalbot/schedule/view-all-scheduled-slots/
        Authentication: Required
        Description: Retrieves all scheduled time slots
        Response: 200 - Success
    Export Batch Schedules to Excel
        Endpoint: GET /api/medicalbot/schedule/export_batch_schedules_excel/
        Authentication: Optional
        Description: Exports schedule data to Excel format
        Response: 200 - Success
    Import Batch Schedules from Excel
        Endpoint: POST /api/medicalbot/schedule/import_batch_schedules_excel/
        Authentication: Optional
        Description: Imports schedule data from Excel file
        Response: 200 - Success

🎥 Video Management
    Add Video
        Endpoint: POST /api/medicalbot/video_management/add-video/
        Authentication: Required
        Description: Uploads a new video file
        Response: 200 - Success
    Update Video
        Endpoint: PUT /api/medicalbot/video_management/add-video/
        Authentication: Required
        Description: Updates existing video information
        Response: 200 - Success
    Delete Video
        Endpoint: DELETE /api/medicalbot/video_management/delete-video/
        Authentication: Required
        Description: Removes a video file
        Response: 204 - No Content
    Swap Video
        Endpoint: POST /api/medicalbot/video_management/swap-video/
        Authentication: Required
        Description: Exchanges video positions or assignments
        Response: 200 - Success
    View Active Video
        Endpoint: GET /api/medicalbot/video_management/view-active-video/
        Authentication: Optional
        Description: Retrieves currently active video
        Response: 200 - Success
    View All Videos
        Endpoint: GET /api/medicalbot/video_management/view-all-video/
        Authentication: Required
        Description: Retrieves all video files and metadata
        Response: 200 - Success

💓 Vitals Management
    Get All BP2CheckMe Data
        Endpoint: GET /api/medicalbot/vitals_management/bp2checkme/all/
        Authentication: Required
        Description: Retrieves all blood pressure monitoring data
        Response: 200 - Success
    Toggle BP2CheckMe Active Status
        Endpoint: PATCH /api/medicalbot/vitals_management/bp2checkme/toggle-active/
        Authentication: Required
        Description: Activates or deactivates BP monitoring
        Response: 200 - Success
    Upsert BP2CheckMe Data
        Endpoint: POST /api/medicalbot/vitals_management/bp2checkme/upsert/
        Authentication: Required
        Description: Creates or updates BP monitoring data
        Response: 200 - Success
    Update BP2CheckMe Data
        Endpoint: PUT /api/medicalbot/vitals_management/bp2checkme/upsert/
        Authentication: Required
        Description: Updates existing BP monitoring data
        Response: 200 - Success
    Robot BP2CheckMe Upsert
        Endpoint: POST /api/medicalbot/vitals_management/robot/bp2checkme/upsert/
        Authentication: Optional
        Description: Robot-initiated BP data creation/update
        Response: 200 - Success

🔧 System Utilities
        Create/Update Local IP
        Endpoint: POST /api/medicalbot/main/create-update-local-ip/
        Authentication: Optional
        Description: Configures local network IP address
        Response: 200 - Success
    Get Local IP
        Endpoint: GET /api/medicalbot/main/get-local-ip/
        Authentication: Optional
        Description: Retrieves current local IP configuration
        Response: 200 - Success
    Drop BP2CheckMe Table
        Endpoint: GET /api/medicalbot/main/drop_bp2checkme_table/
        Authentication: Optional
        Description: Removes BP2CheckMe database table (administrative function)
        Response: 200 - Success
    Get API Schema
    Endpoint: GET /schema/
    Authentication: Optional
    Description: Retrieves OpenAPI schema in JSON or YAML format
    Parameters:
    format (query) - Response format: json or yaml
    lang (query) - Language code for localization
    Response: 200 - OpenAPI schema document
    Response Codes
    200 OK - Request successful
    204 No Content - Request successful, no response body
    401 Unauthorized - Authentication required or invalid
    403 Forbidden - Insufficient permissions
    404 Not Found - Resource not found
    422 Unprocessable Entity - Validation error
    500 Internal Server Error - Server error
    Notes
    1. Authentication: Most endpoints require JWT authentication. Ensure your requests include the
    proper Authorization header.
    2. Data Formats: The API likely accepts and returns JSON data, though this is not explicitly specified
    in the schema.
    3. Error Handling: Implement proper error handling for all response codes, especially authentication
    failures.
    4. Rate Limiting: Consider implementing rate limiting on the client side to avoid overwhelming the
    server.
    5. Security: Always use HTTPS in production environments when transmitting authentication tokens.
    6. File Uploads: Video and Excel import endpoints likely require multipart/form-data content type.This documentation is generated from the OpenAPI 3.0.3 schema. For the most up-to-date information,
    consult the /schema/ endpoint directly.
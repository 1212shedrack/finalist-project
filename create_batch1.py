import os

base_dir = r"C:\Users\SHEDRACK\OneDrive\Desktop\project\amaranthus_project"
os.makedirs(os.path.join(base_dir, "templates", "accounts", "farmer"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "templates", "accounts", "admin_panel"), exist_ok=True)

files = {}

files["templates/accounts/_dashboard_base.html"] = """{% load i18n %}
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% trans "AmaranthusAI Dashboard" %}{% endblock %}</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Bootstrap 5.3.2 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons 1.11.3 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --primary: #1a4d2e;
            --primary-light: #2d7a4f;
            --accent: #4CAF50;
            --bg-color: #f8faf8;
            --text-color: #333;
            --sidebar-width: 250px;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            overflow-x: hidden;
        }
        #sidebar {
            width: var(--sidebar-width);
            height: 100vh;
            background-color: var(--primary);
            color: white;
            position: fixed;
            left: 0;
            top: 0;
            transition: all 0.3s;
            z-index: 1000;
            display: flex;
            flex-direction: column;
        }
        #sidebar .logo-area {
            padding: 20px;
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        #sidebar .nav-links {
            flex-grow: 1;
            padding: 20px 0;
            overflow-y: auto;
        }
        #sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s;
            border-left: 4px solid transparent;
        }
        #sidebar .nav-link:hover, #sidebar .nav-link.active {
            color: white;
            background: rgba(255,255,255,0.1);
        }
        #sidebar .nav-link.active {
            border-left-color: var(--accent);
        }
        #sidebar .user-area {
            padding: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        #main-content {
            margin-left: var(--sidebar-width);
            min-height: 100vh;
            transition: all 0.3s;
        }
        .top-header {
            background: white;
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        }
        .btn-primary {
            background-color: var(--primary);
            border-color: var(--primary);
        }
        .btn-primary:hover {
            background-color: var(--primary-light);
            border-color: var(--primary-light);
        }
        .btn-accent {
            background-color: var(--accent);
            color: white;
            border: none;
        }
        .btn-accent:hover {
            background-color: #45a049;
            color: white;
        }
        @media (max-width: 768px) {
            #sidebar {
                left: calc(var(--sidebar-width) * -1);
            }
            #sidebar.show {
                left: 0;
            }
            #main-content {
                margin-left: 0;
            }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>

    <div id="sidebar">
        <div class="logo-area">
            <i class="bi bi-env-fill"></i>
            <span>AmaranthusAI</span>
        </div>
        <div class="nav-links">
            {% block sidebar_nav %}
            {% if request.user.profile.is_farmer %}
                <a href="{% url 'accounts:farmer_dashboard' %}" class="nav-link"><i class="bi bi-grid-1x2-fill"></i> {% trans "Dashboard" %}</a>
                <a href="{% url 'accounts:farmer_history' %}" class="nav-link"><i class="bi bi-clock-history"></i> {% trans "Scan History" %}</a>
                <a href="{% url 'accounts:farmer_favorites' %}" class="nav-link"><i class="bi bi-heart-fill"></i> {% trans "Favorites" %}</a>
                <a href="{% url 'accounts:farmer_notifications' %}" class="nav-link"><i class="bi bi-bell-fill"></i> {% trans "Notifications" %}</a>
                <a href="{% url 'accounts:farmer_feedback' %}" class="nav-link"><i class="bi bi-chat-left-text-fill"></i> {% trans "Send Feedback" %}</a>
                <a href="{% url 'accounts:farmer_profile' %}" class="nav-link"><i class="bi bi-person-fill"></i> {% trans "Profile" %}</a>
            {% elif request.user.profile.is_admin %}
                <a href="{% url 'accounts:admin_dashboard' %}" class="nav-link"><i class="bi bi-speedometer2"></i> {% trans "Dashboard" %}</a>
                <a href="{% url 'accounts:admin_farmers' %}" class="nav-link"><i class="bi bi-people-fill"></i> {% trans "Farmers" %}</a>
                <a href="{% url 'accounts:admin_scans' %}" class="nav-link"><i class="bi bi-images"></i> {% trans "All Scans" %}</a>
                <a href="{% url 'accounts:admin_reports' %}" class="nav-link"><i class="bi bi-file-earmark-bar-graph-fill"></i> {% trans "Reports" %}</a>
                <a href="{% url 'accounts:admin_feedback' %}" class="nav-link"><i class="bi bi-chat-dots-fill"></i> {% trans "Feedback" %}</a>
                <a href="{% url 'accounts:admin_logs' %}" class="nav-link"><i class="bi bi-journal-text"></i> {% trans "Logs" %}</a>
                <a href="{% url 'disease_app:home' %}" class="nav-link"><i class="bi bi-box-arrow-up-right"></i> {% trans "Go to Site" %}</a>
            {% endif %}
            {% endblock %}
        </div>
        <div class="user-area">
            <div class="d-flex align-items-center gap-2">
                {% if request.user.profile.avatar %}
                    <img src="{{ request.user.profile.avatar.url }}" alt="Avatar" class="rounded-circle" width="40" height="40" style="object-fit: cover;">
                {% else %}
                    <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white" style="width: 40px; height: 40px;"><i class="bi bi-person"></i></div>
                {% endif %}
                <div class="overflow-hidden">
                    <div class="fw-bold text-truncate">{{ request.user.profile.full_name|default:request.user.username }}</div>
                    <div class="small text-muted">{{ request.user.profile.role }}</div>
                </div>
            </div>
            <a href="{% url 'accounts:logout' %}" class="btn btn-sm btn-outline-light w-100 mt-3"><i class="bi bi-box-arrow-right"></i> {% trans "Logout" %}</a>
        </div>
    </div>

    <div id="main-content">
        <div class="top-header">
            <div class="d-flex align-items-center gap-3">
                <button class="btn btn-light d-md-none" id="sidebarToggle"><i class="bi bi-list"></i></button>
                <h4 class="mb-0 fw-bold">{% block page_title %}{% trans "Dashboard" %}{% endblock %}</h4>
            </div>
            <div class="d-flex align-items-center gap-3">
                <a href="{% url 'accounts:farmer_notifications' %}" class="position-relative text-dark fs-5">
                    <i class="bi bi-bell"></i>
                    {% if unread_count > 0 %}
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem;">
                        {{ unread_count }}
                    </span>
                    {% endif %}
                </a>
            </div>
        </div>

        <div class="p-4 p-md-5">
            {% block dashboard_content %}{% endblock %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('sidebarToggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('show');
        });
        
        // Highlight active nav link
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

files["templates/accounts/farmer/dashboard.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Farmer Dashboard" %}{% endblock %}

{% block dashboard_content %}
{% if unread_count > 0 %}
<div class="alert alert-info alert-dismissible fade show" role="alert">
    <i class="bi bi-info-circle-fill me-2"></i> {% trans "You have" %} <strong>{{ unread_count }}</strong> {% trans "unread notifications." %}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>
{% endif %}

<div class="card mb-4 bg-primary text-white" style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);">
    <div class="card-body p-4 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
            <h3 class="fw-bold mb-1">{% trans "Good day" %}, {{ request.user.profile.full_name|default:request.user.username }}! 🌿</h3>
            <p class="mb-0 opacity-75">{% trans "Welcome back to your AmaranthusAI dashboard." %}</p>
        </div>
        <div style="min-width: 200px;">
            <div class="d-flex justify-content-between small mb-1">
                <span>{% trans "Profile Completion" %}</span>
                <span>80%</span>
            </div>
            <div class="progress" style="height: 8px; background: rgba(255,255,255,0.2);">
                <div class="progress-bar bg-accent" role="progressbar" style="width: 80%;" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-sm-6 col-lg-3">
        <div class="card h-100">
            <div class="card-body d-flex align-items-center">
                <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3 text-primary fs-3">
                    <i class="bi bi-camera"></i>
                </div>
                <div>
                    <h6 class="text-muted mb-1">{% trans "Total Scans" %}</h6>
                    <h3 class="mb-0 fw-bold">{{ total_scans }}</h3>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card h-100">
            <div class="card-body d-flex align-items-center">
                <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3 text-success fs-3">
                    <i class="bi bi-check-circle"></i>
                </div>
                <div>
                    <h6 class="text-muted mb-1">{% trans "Healthy Leaves" %}</h6>
                    <h3 class="mb-0 fw-bold">{{ stats.healthy|default:0 }}</h3>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card h-100">
            <div class="card-body d-flex align-items-center">
                <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3 text-warning fs-3">
                    <i class="bi bi-exclamation-circle"></i>
                </div>
                <div>
                    <h6 class="text-muted mb-1">{% trans "Diseased" %}</h6>
                    <h3 class="mb-0 fw-bold">{{ stats.diseased|default:0 }}</h3>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card h-100">
            <div class="card-body d-flex align-items-center">
                <div class="rounded-circle bg-danger bg-opacity-10 p-3 me-3 text-danger fs-3">
                    <i class="bi bi-heart"></i>
                </div>
                <div>
                    <h6 class="text-muted mb-1">{% trans "Favorites" %}</h6>
                    <h3 class="mb-0 fw-bold">{{ favorites.count|default:0 }}</h3>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h5 class="fw-bold mb-0">{% trans "Recent Scans" %}</h5>
    <a href="{% url 'disease_app:predict' %}" class="btn btn-accent"><i class="bi bi-camera-fill me-1"></i> {% trans "Scan New Leaf" %}</a>
</div>

<div class="row g-4">
    {% for scan in predictions|slice:":6" %}
    <div class="col-sm-6 col-md-4 col-xl-2">
        <div class="card h-100">
            {% if scan.image %}
            <img src="{{ scan.image.url }}" class="card-img-top" alt="Scan" style="height: 150px; object-fit: cover;">
            {% endif %}
            <div class="card-body p-3">
                <span class="badge {% if scan.disease_class == 'Healthy' %}bg-success{% else %}bg-warning text-dark{% endif %} mb-2">{{ scan.disease_class }}</span>
                <p class="mb-1 small text-muted"><i class="bi bi-calendar3"></i> {{ scan.created_at|date:"M d, Y" }}</p>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="fw-bold small">{{ scan.confidence|floatformat:1 }}% {% trans "Conf." %}</span>
                    <a href="{% url 'disease_app:result' scan.pk %}" class="btn btn-sm btn-outline-primary">{% trans "View" %}</a>
                </div>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12 text-center py-5 text-muted">
        <i class="bi bi-camera fs-1"></i>
        <p class="mt-2">{% trans "No scans yet. Start by scanning a new leaf." %}</p>
    </div>
    {% endfor %}
</div>

<div class="mt-5">
    <h5 class="fw-bold mb-3">{% trans "Quick Actions" %}</h5>
    <div class="d-flex flex-wrap gap-2">
        <a href="{% url 'disease_app:predict' %}" class="btn btn-primary"><i class="bi bi-upc-scan"></i> {% trans "Scan Now" %}</a>
        <a href="{% url 'accounts:farmer_history' %}" class="btn btn-light"><i class="bi bi-clock-history"></i> {% trans "View History" %}</a>
        <button class="btn btn-light"><i class="bi bi-download"></i> {% trans "Download Report" %}</button>
        <a href="{% url 'accounts:farmer_profile' %}" class="btn btn-light"><i class="bi bi-person-lines-fill"></i> {% trans "Edit Profile" %}</a>
    </div>
</div>
{% endblock %}
"""

files["templates/accounts/farmer/profile.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "My Profile" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white border-bottom-0 pt-4 pb-0 px-4">
        <ul class="nav nav-tabs border-bottom" id="profileTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active fw-bold text-dark" id="info-tab" data-bs-toggle="tab" data-bs-target="#info" type="button" role="tab">{% trans "Personal Info" %}</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link fw-bold text-dark" id="password-tab" data-bs-toggle="tab" data-bs-target="#password" type="button" role="tab">{% trans "Change Password" %}</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link fw-bold text-dark" id="settings-tab" data-bs-toggle="tab" data-bs-target="#settings" type="button" role="tab">{% trans "Account Settings" %}</button>
            </li>
        </ul>
    </div>
    <div class="card-body p-4">
        <div class="tab-content" id="profileTabsContent">
            <!-- Info Tab -->
            <div class="tab-pane fade show active" id="info" role="tabpanel">
                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="d-flex align-items-center gap-4 mb-4">
                        <div class="position-relative">
                            {% if request.user.profile.avatar %}
                                <img src="{{ request.user.profile.avatar.url }}" id="avatarPreview" class="rounded-circle border" width="120" height="120" style="object-fit: cover;">
                            {% else %}
                                <div id="avatarPreview" class="rounded-circle bg-light border d-flex align-items-center justify-content-center text-muted fs-1" style="width: 120px; height: 120px;">
                                    <i class="bi bi-person"></i>
                                </div>
                            {% endif %}
                            <label for="id_avatar" class="position-absolute bottom-0 end-0 bg-primary text-white rounded-circle p-2" style="cursor:pointer; transform: translate(25%, 25%);">
                                <i class="bi bi-camera"></i>
                            </label>
                            <input type="file" name="avatar" id="id_avatar" class="d-none" accept="image/*" onchange="previewImage(event)">
                        </div>
                        <div>
                            <h4 class="mb-1 fw-bold">{{ request.user.username }}</h4>
                            <p class="text-muted mb-0">{{ request.user.profile.role }}</p>
                        </div>
                    </div>

                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">{% trans "Full Name" %}</label>
                            <input type="text" name="full_name" class="form-control" value="{{ request.user.profile.full_name|default:'' }}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">{% trans "Email" %}</label>
                            <input type="email" name="email" class="form-control" value="{{ request.user.email }}" readonly disabled>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">{% trans "Phone Number" %}</label>
                            <input type="text" name="phone" class="form-control" value="{{ request.user.profile.phone|default:'' }}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">{% trans "Gender" %}</label>
                            <select name="gender" class="form-select">
                                <option value="">{% trans "Select Gender" %}</option>
                                <option value="M" {% if request.user.profile.gender == 'M' %}selected{% endif %}>{% trans "Male" %}</option>
                                <option value="F" {% if request.user.profile.gender == 'F' %}selected{% endif %}>{% trans "Female" %}</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">{% trans "Location" %}</label>
                            <input type="text" name="location" class="form-control" value="{{ request.user.profile.location|default:'' }}">
                        </div>
                        <div class="col-12">
                            <label class="form-label">{% trans "Bio" %}</label>
                            <textarea name="bio" class="form-control" rows="3">{{ request.user.profile.bio|default:'' }}</textarea>
                        </div>
                        <div class="col-12 mt-4">
                            <button type="submit" class="btn btn-primary px-4 py-2">{% trans "Save Changes" %}</button>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Password Tab -->
            <div class="tab-pane fade" id="password" role="tabpanel">
                <form method="post" action="{% url 'accounts:farmer_password' %}" style="max-width: 500px;">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">{% trans "Current Password" %}</label>
                        <input type="password" name="old_password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">{% trans "New Password" %}</label>
                        <input type="password" name="new_password" class="form-control" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label">{% trans "Confirm New Password" %}</label>
                        <input type="password" name="confirm_password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary">{% trans "Update Password" %}</button>
                </form>
            </div>

            <!-- Settings Tab -->
            <div class="tab-pane fade" id="settings" role="tabpanel">
                <div class="mb-5">
                    <h5 class="fw-bold">{% trans "Preferences" %}</h5>
                    <div class="mb-3">
                        <label class="form-label">{% trans "Language" %}</label>
                        <select class="form-select" style="max-width: 250px;">
                            <option value="en">English</option>
                        </select>
                    </div>
                    <p class="text-muted small">{% trans "Account created on" %} {{ request.user.date_joined|date:"M d, Y" }}</p>
                </div>
                
                <hr>
                
                <div class="mt-4">
                    <h5 class="fw-bold text-danger">{% trans "Danger Zone" %}</h5>
                    <p class="text-muted">{% trans "Once you delete your account, there is no going back. Please be certain." %}</p>
                    <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteAccountModal">
                        {% trans "Delete Account" %}
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Delete Account Modal -->
<div class="modal fade" id="deleteAccountModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content border-danger">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">{% trans "Delete Account" %}</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>{% trans "Are you sure you want to delete your account? This action cannot be undone." %}</p>
                <form method="post" action="{% url 'accounts:farmer_delete_account' %}" id="deleteForm">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">{% trans "Type your username" %} (<strong>{{ request.user.username }}</strong>) {% trans "to confirm:" %}</label>
                        <input type="text" class="form-control" id="confirmUsername" oninput="checkUsername()">
                    </div>
                    <button type="submit" class="btn btn-danger w-100" id="deleteBtn" disabled>{% trans "Permanently Delete My Account" %}</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    function previewImage(event) {
        const reader = new FileReader();
        reader.onload = function() {
            const output = document.getElementById('avatarPreview');
            if(output.tagName === 'IMG') {
                output.src = reader.result;
            } else {
                output.outerHTML = '<img src="' + reader.result + '" id="avatarPreview" class="rounded-circle border" width="120" height="120" style="object-fit: cover;">';
            }
        }
        reader.readAsDataURL(event.target.files[0]);
    }

    function checkUsername() {
        const input = document.getElementById('confirmUsername').value;
        const btn = document.getElementById('deleteBtn');
        if (input === '{{ request.user.username }}') {
            btn.disabled = false;
        } else {
            btn.disabled = true;
        }
    }
</script>
{% endblock %}
"""

files["templates/accounts/farmer/scan_history.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Scan History" %}{% endblock %}

{% block dashboard_content %}
<div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
    <div class="d-flex gap-2 flex-wrap">
        <button class="btn btn-primary rounded-pill px-3 active">{% trans "All" %}</button>
        <button class="btn btn-outline-secondary rounded-pill px-3">{% trans "Healthy" %}</button>
        <button class="btn btn-outline-secondary rounded-pill px-3">{% trans "Leaf Spot" %}</button>
        <button class="btn btn-outline-secondary rounded-pill px-3">{% trans "White Rust" %}</button>
        <button class="btn btn-outline-secondary rounded-pill px-3">{% trans "Non-Amaranthus" %}</button>
    </div>
    <div class="d-flex gap-2">
        <div class="input-group">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control border-start-0 ps-0" placeholder="{% trans 'Search...' %}">
        </div>
        <button class="btn btn-outline-primary"><i class="bi bi-download"></i> {% trans "Export" %}</button>
    </div>
</div>

<div class="row g-4">
    {% for scan in predictions %}
    <div class="col-sm-6 col-md-4 col-xl-3">
        <div class="card h-100 overflow-hidden">
            <div class="position-relative">
                {% if scan.image %}
                <img src="{{ scan.image.url }}" class="card-img-top" alt="Scan" style="height: 200px; object-fit: cover;">
                {% endif %}
                <form method="post" action="{% url 'accounts:favorite_add' scan.pk %}" class="position-absolute top-0 end-0 p-2">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-light rounded-circle shadow-sm p-2 text-danger" style="width: 40px; height: 40px;">
                        <i class="bi bi-heart"></i>
                    </button>
                </form>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge {% if scan.disease_class == 'Healthy' %}bg-success{% else %}bg-warning text-dark{% endif %} fs-6">{{ scan.disease_class }}</span>
                    <span class="fw-bold">{{ scan.confidence|floatformat:1 }}%</span>
                </div>
                <p class="text-muted small mb-3"><i class="bi bi-clock"></i> {{ scan.created_at|date:"M d, Y H:i" }}</p>
                <a href="{% url 'disease_app:result' scan.pk %}" class="btn btn-outline-primary w-100">{% trans "View Details" %}</a>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12 text-center py-5">
        <div class="text-muted mb-3">
            <i class="bi bi-images fs-1"></i>
        </div>
        <h4 class="fw-bold">{% trans "No scans found" %}</h4>
        <p class="text-muted">{% trans "You haven't scanned any leaves yet. Start your first scan!" %}</p>
        <a href="{% url 'disease_app:predict' %}" class="btn btn-accent mt-2"><i class="bi bi-camera-fill me-1"></i> {% trans "Scan New Leaf" %}</a>
    </div>
    {% endfor %}
</div>

{% if page_obj.has_other_pages %}
<nav class="mt-5">
    <ul class="pagination justify-content-center">
        {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">{% trans "Previous" %}</a></li>
        {% endif %}
        <li class="page-item active"><span class="page-link">{{ page_obj.number }}</span></li>
        {% if page_obj.has_next %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">{% trans "Next" %}</a></li>
        {% endif %}
    </ul>
</nav>
{% endif %}
{% endblock %}
"""

files["templates/accounts/farmer/favorites.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "My Favorites" %}{% endblock %}

{% block dashboard_content %}
<div class="row g-4">
    {% for fav in favorites %}
    <div class="col-sm-6 col-md-4 col-xl-3">
        <div class="card h-100 overflow-hidden">
            <div class="position-relative">
                {% if fav.prediction.image %}
                <img src="{{ fav.prediction.image.url }}" class="card-img-top" alt="Scan" style="height: 200px; object-fit: cover;">
                {% endif %}
                <form method="post" action="{% url 'accounts:favorite_remove' fav.prediction.pk %}" class="position-absolute top-0 end-0 p-2">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-light rounded-circle shadow-sm p-2 text-danger" style="width: 40px; height: 40px;" title="{% trans 'Remove' %}">
                        <i class="bi bi-heart-fill"></i>
                    </button>
                </form>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge {% if fav.prediction.disease_class == 'Healthy' %}bg-success{% else %}bg-warning text-dark{% endif %} fs-6">{{ fav.prediction.disease_class }}</span>
                    <span class="fw-bold">{{ fav.prediction.confidence|floatformat:1 }}%</span>
                </div>
                <p class="text-muted small mb-3"><i class="bi bi-clock"></i> {{ fav.prediction.created_at|date:"M d, Y" }}</p>
                <a href="{% url 'disease_app:result' fav.prediction.pk %}" class="btn btn-outline-primary w-100">{% trans "View Result" %}</a>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12 text-center py-5">
        <div class="text-muted mb-3 text-danger opacity-50">
            <i class="bi bi-heart-fill" style="font-size: 4rem;"></i>
        </div>
        <h4 class="fw-bold">{% trans "No favorites yet" %}</h4>
        <p class="text-muted">{% trans "You can save important scans to your favorites by clicking the heart icon on any scan result." %}</p>
        <a href="{% url 'accounts:farmer_history' %}" class="btn btn-outline-primary mt-2">{% trans "Browse History" %}</a>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

files["templates/accounts/farmer/notifications.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Notifications" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-bold">{% trans "Recent Alerts" %}</h5>
        <button class="btn btn-sm btn-outline-secondary">{% trans "Mark all as read" %}</button>
    </div>
    <div class="list-group list-group-flush">
        {% for notif in notifications %}
        <div class="list-group-item p-4 {% if not notif.is_read %}bg-light{% endif %}">
            <div class="d-flex gap-3">
                <div class="flex-shrink-0">
                    {% if notif.notif_type == 'success' %}
                        <div class="rounded-circle bg-success text-white p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="bi bi-check-lg"></i></div>
                    {% elif notif.notif_type == 'warning' %}
                        <div class="rounded-circle bg-warning text-dark p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="bi bi-exclamation-triangle"></i></div>
                    {% elif notif.notif_type == 'danger' %}
                        <div class="rounded-circle bg-danger text-white p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="bi bi-shield-x"></i></div>
                    {% else %}
                        <div class="rounded-circle bg-primary text-white p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="bi bi-info-circle"></i></div>
                    {% endif %}
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <h6 class="mb-0 fw-bold">{{ notif.title }}</h6>
                        <small class="text-muted">{{ notif.created_at|timesince }} {% trans "ago" %}</small>
                    </div>
                    <p class="mb-0 text-secondary">{{ notif.message }}</p>
                </div>
                {% if not notif.is_read %}
                <div class="align-self-center">
                    <span class="badge bg-primary rounded-circle p-1"><span class="visually-hidden">unread</span></span>
                </div>
                {% endif %}
            </div>
        </div>
        {% empty %}
        <div class="text-center py-5 text-muted">
            <i class="bi bi-bell-slash fs-1"></i>
            <p class="mt-3">{% trans "You have no notifications." %}</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

files["templates/accounts/farmer/feedback.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Send Feedback" %}{% endblock %}

{% block extra_css %}
<style>
    .star-rating {
        direction: rtl;
        display: inline-flex;
    }
    .star-rating input[type="radio"] {
        display: none;
    }
    .star-rating label {
        font-size: 2rem;
        color: #ddd;
        cursor: pointer;
        transition: color 0.2s;
    }
    .star-rating input[type="radio"]:checked ~ label,
    .star-rating label:hover,
    .star-rating label:hover ~ label {
        color: #ffc107;
    }
</style>
{% endblock %}

{% block dashboard_content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-body p-4 p-md-5">
                <div class="text-center mb-4">
                    <i class="bi bi-chat-heart-fill text-primary" style="font-size: 3rem;"></i>
                    <h4 class="fw-bold mt-2">{% trans "We value your feedback!" %}</h4>
                    <p class="text-muted">{% trans "Help us improve AmaranthusAI by sharing your experience." %}</p>
                </div>
                
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label fw-bold">{% trans "Category" %}</label>
                        <select name="category" class="form-select" required>
                            <option value="">{% trans "Select a category" %}</option>
                            <option value="Bug">{% trans "Bug Report" %}</option>
                            <option value="Feature">{% trans "Feature Request" %}</option>
                            <option value="General">{% trans "General Feedback" %}</option>
                            <option value="Complaint">{% trans "Complaint" %}</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold">{% trans "Subject" %}</label>
                        <input type="text" name="subject" class="form-control" required placeholder="{% trans 'Brief summary' %}">
                    </div>
                    
                    <div class="mb-4">
                        <label class="form-label fw-bold">{% trans "Message" %}</label>
                        <textarea name="message" class="form-control" rows="5" required placeholder="{% trans 'Please provide details...' %}"></textarea>
                    </div>
                    
                    <div class="mb-4 text-center">
                        <label class="form-label fw-bold d-block">{% trans "Rate your experience" %}</label>
                        <div class="star-rating">
                            <input type="radio" id="star5" name="rating" value="5"><label for="star5" class="bi bi-star-fill"></label>
                            <input type="radio" id="star4" name="rating" value="4"><label for="star4" class="bi bi-star-fill"></label>
                            <input type="radio" id="star3" name="rating" value="3"><label for="star3" class="bi bi-star-fill"></label>
                            <input type="radio" id="star2" name="rating" value="2"><label for="star2" class="bi bi-star-fill"></label>
                            <input type="radio" id="star1" name="rating" value="1" required><label for="star1" class="bi bi-star-fill"></label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100 py-2 fw-bold fs-5">{% trans "Submit Feedback" %}</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

files["templates/accounts/admin_panel/dashboard.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Admin Dashboard" %}{% endblock %}

{% block dashboard_content %}
<div class="row g-4 mb-4">
    <div class="col-sm-6 col-lg-3">
        <div class="card bg-success text-white h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="text-white-50">{% trans "Total Farmers" %}</h6>
                        <h2 class="fw-bold mb-0">{{ total_farmers|default:0 }}</h2>
                    </div>
                    <i class="bi bi-people fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card bg-primary text-white h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="text-white-50">{% trans "Total Scans" %}</h6>
                        <h2 class="fw-bold mb-0">{{ total_scans|default:0 }}</h2>
                    </div>
                    <i class="bi bi-images fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card bg-warning text-dark h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="text-dark-50 opacity-75">{% trans "Scans Today" %}</h6>
                        <h2 class="fw-bold mb-0">{{ scans_today|default:0 }}</h2>
                    </div>
                    <i class="bi bi-graph-up fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-lg-3">
        <div class="card" style="background-color: #6f42c1; color: white;">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="text-white-50">{% trans "Top Disease" %}</h6>
                        <h4 class="fw-bold mb-0 text-truncate">{% trans "Leaf Spot" %}</h4>
                    </div>
                    <i class="bi bi-bug fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header bg-white py-3 fw-bold">{% trans "Disease Distribution" %}</div>
            <div class="card-body p-4 d-flex justify-content-center">
                <canvas id="diseaseChart" style="max-height: 300px;"></canvas>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header bg-white py-3 fw-bold">{% trans "Scans Overview (Last 7 Days)" %}</div>
            <div class="card-body p-4">
                <canvas id="scansChart" style="max-height: 300px;"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row g-4">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                <span class="fw-bold">{% trans "Recent Scans" %}</span>
                <a href="{% url 'accounts:admin_scans' %}" class="btn btn-sm btn-outline-primary">{% trans "View All" %}</a>
            </div>
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>{% trans "User" %}</th>
                            <th>{% trans "Result" %}</th>
                            <th>{% trans "Risk" %}</th>
                            <th>{% trans "Date" %}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for scan in recent_predictions|slice:":5" %}
                        <tr>
                            <td>#{{ scan.id }}</td>
                            <td>{{ scan.user.username }}</td>
                            <td>{{ scan.disease_class }} <small class="text-muted">({{ scan.confidence|floatformat:1 }}%)</small></td>
                            <td>
                                <span class="badge {% if scan.disease_class == 'Healthy' %}bg-success{% else %}bg-danger{% endif %}">
                                    {% if scan.disease_class == 'Healthy' %}{% trans "Low" %}{% else %}{% trans "High" %}{% endif %}
                                </span>
                            </td>
                            <td>{{ scan.created_at|date:"M d, H:i" }}</td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="5" class="text-center py-3">{% trans "No recent scans." %}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header bg-white py-3 fw-bold">{% trans "Newest Farmers" %}</div>
            <div class="list-group list-group-flush">
                {% for farmer in recent_farmers|slice:":5" %}
                <div class="list-group-item d-flex align-items-center gap-3 p-3">
                    {% if farmer.avatar %}
                        <img src="{{ farmer.avatar.url }}" class="rounded-circle" width="40" height="40" style="object-fit: cover;">
                    {% else %}
                        <div class="rounded-circle bg-light d-flex align-items-center justify-content-center text-muted" style="width: 40px; height: 40px;"><i class="bi bi-person"></i></div>
                    {% endif %}
                    <div class="flex-grow-1 overflow-hidden">
                        <div class="fw-bold text-truncate">{{ farmer.full_name|default:farmer.user.username }}</div>
                        <small class="text-muted">{{ farmer.user.date_joined|date:"M d, Y" }}</small>
                    </div>
                    <a href="{% url 'accounts:admin_farmer_detail' farmer.user.id %}" class="btn btn-sm btn-light"><i class="bi bi-chevron-right"></i></a>
                </div>
                {% empty %}
                <div class="p-4 text-center text-muted">{% trans "No farmers registered yet." %}</div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Dummy data for charts - ideally fetch via AJAX to admin_chart_data
    const ctxDoughnut = document.getElementById('diseaseChart').getContext('2d');
    new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
            labels: ['Healthy', 'Leaf Spot', 'White Rust', 'Non-Amaranthus'],
            datasets: [{
                data: [45, 25, 20, 10],
                backgroundColor: ['#198754', '#fd7e14', '#0dcaf0', '#6c757d']
            }]
        },
        options: { plugins: { legend: { position: 'right' } } }
    });

    const ctxBar = document.getElementById('scansChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Scans',
                data: [12, 19, 15, 25, 22, 30, 28],
                backgroundColor: '#4CAF50'
            }]
        },
        options: { scales: { y: { beginAtZero: true } } }
    });
});
</script>
{% endblock %}
"""

for filepath, content in files.items():
    with open(os.path.join(base_dir, filepath), 'w', encoding='utf-8') as f:
        f.write(content)

print("Batch 1 created")

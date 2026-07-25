import os

base_dir = r"C:\Users\SHEDRACK\OneDrive\Desktop\project\amaranthus_project"
os.makedirs(os.path.join(base_dir, "templates", "accounts", "admin_panel"), exist_ok=True)

files = {}

files["templates/accounts/admin_panel/farmers.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Manage Farmers" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div class="input-group" style="max-width: 300px;">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control border-start-0 ps-0" placeholder="{% trans 'Search farmers...' %}">
        </div>
        <div>
            <button class="btn btn-outline-primary"><i class="bi bi-download"></i> {% trans "Export CSV" %}</button>
        </div>
    </div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th>{% trans "Farmer" %}</th>
                    <th>{% trans "Contact" %}</th>
                    <th>{% trans "Scans" %}</th>
                    <th>{% trans "Status" %}</th>
                    <th>{% trans "Joined" %}</th>
                    <th class="text-end">{% trans "Actions" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for profile in farmers %}
                <tr>
                    <td>
                        <div class="d-flex align-items-center gap-3">
                            {% if profile.avatar %}
                                <img src="{{ profile.avatar.url }}" class="rounded-circle" width="40" height="40" style="object-fit: cover;">
                            {% else %}
                                <div class="rounded-circle bg-light d-flex align-items-center justify-content-center text-muted" style="width: 40px; height: 40px;"><i class="bi bi-person"></i></div>
                            {% endif %}
                            <div>
                                <div class="fw-bold">{{ profile.full_name|default:profile.user.username }}</div>
                                <div class="small text-muted">@{{ profile.user.username }}</div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div><i class="bi bi-envelope text-muted"></i> {{ profile.user.email }}</div>
                        {% if profile.phone %}<div><i class="bi bi-telephone text-muted"></i> {{ profile.phone }}</div>{% endif %}
                    </td>
                    <td><span class="badge bg-secondary rounded-pill">{{ profile.user.predictions.count|default:0 }}</span></td>
                    <td>
                        {% if profile.user.is_active %}
                            <span class="badge bg-success">{% trans "Active" %}</span>
                        {% else %}
                            <span class="badge bg-danger">{% trans "Disabled" %}</span>
                        {% endif %}
                    </td>
                    <td>{{ profile.user.date_joined|date:"M d, Y" }}</td>
                    <td class="text-end">
                        <a href="{% url 'accounts:admin_farmer_detail' profile.user.id %}" class="btn btn-sm btn-light" title="{% trans 'View Details' %}"><i class="bi bi-eye"></i></a>
                        <form method="post" action="{% url 'accounts:admin_toggle_active' profile.user.id %}" class="d-inline">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-sm {% if profile.user.is_active %}btn-outline-warning{% else %}btn-outline-success{% endif %}" title="{% trans 'Toggle Status' %}">
                                <i class="bi {% if profile.user.is_active %}bi-pause-circle{% else %}bi-play-circle{% endif %}"></i>
                            </button>
                        </form>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="6" class="text-center py-5 text-muted">{% trans "No farmers found." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% if farmers.has_other_pages %}
<nav class="mt-4">
    <ul class="pagination justify-content-center">
        {% if farmers.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ farmers.previous_page_number }}">{% trans "Previous" %}</a></li>
        {% endif %}
        <li class="page-item active"><span class="page-link">{{ farmers.number }}</span></li>
        {% if farmers.has_next %}
        <li class="page-item"><a class="page-link" href="?page={{ farmers.next_page_number }}">{% trans "Next" %}</a></li>
        {% endif %}
    </ul>
</nav>
{% endif %}
{% endblock %}
"""

files["templates/accounts/admin_panel/farmer_detail.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Farmer Details" %}{% endblock %}

{% block dashboard_content %}
<div class="mb-3">
    <a href="{% url 'accounts:admin_farmers' %}" class="text-decoration-none text-muted"><i class="bi bi-arrow-left"></i> {% trans "Back to Farmers" %}</a>
</div>

<div class="row g-4">
    <div class="col-lg-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                {% if farmer.avatar %}
                    <img src="{{ farmer.avatar.url }}" class="rounded-circle mb-3 border" width="120" height="120" style="object-fit: cover;">
                {% else %}
                    <div class="rounded-circle bg-light d-inline-flex align-items-center justify-content-center text-muted mb-3 border" style="width: 120px; height: 120px; font-size: 3rem;"><i class="bi bi-person"></i></div>
                {% endif %}
                <h4 class="fw-bold mb-1">{{ farmer.full_name|default:farmer.user.username }}</h4>
                <p class="text-muted mb-3">@{{ farmer.user.username }}</p>
                
                <div class="d-flex justify-content-center gap-2 mb-4">
                    {% if farmer.user.is_active %}
                        <span class="badge bg-success">{% trans "Active Account" %}</span>
                    {% else %}
                        <span class="badge bg-danger">{% trans "Disabled Account" %}</span>
                    {% endif %}
                    <span class="badge bg-primary">{{ farmer.user.date_joined|date:"M Y" }}</span>
                </div>
                
                <ul class="list-group list-group-flush text-start mb-4">
                    <li class="list-group-item px-0"><i class="bi bi-envelope me-2 text-muted"></i> {{ farmer.user.email }}</li>
                    <li class="list-group-item px-0"><i class="bi bi-telephone me-2 text-muted"></i> {{ farmer.phone|default:"N/A" }}</li>
                    <li class="list-group-item px-0"><i class="bi bi-geo-alt me-2 text-muted"></i> {{ farmer.location|default:"N/A" }}</li>
                    <li class="list-group-item px-0"><i class="bi bi-gender-ambiguous me-2 text-muted"></i> {{ farmer.get_gender_display|default:"N/A" }}</li>
                </ul>
                
                <div class="d-grid gap-2">
                    <form method="post" action="{% url 'accounts:admin_toggle_active' farmer.user.id %}">
                        {% csrf_token %}
                        <button type="submit" class="btn {% if farmer.user.is_active %}btn-outline-warning{% else %}btn-success{% endif %} w-100">
                            {% if farmer.user.is_active %}<i class="bi bi-pause-circle"></i> {% trans "Disable Account" %}{% else %}<i class="bi bi-play-circle"></i> {% trans "Enable Account" %}{% endif %}
                        </button>
                    </form>
                    <button class="btn btn-outline-danger w-100" data-bs-toggle="modal" data-bs-target="#deleteModal"><i class="bi bi-trash"></i> {% trans "Delete Account" %}</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-8">
        <div class="row g-3 mb-4">
            <div class="col-sm-4">
                <div class="card bg-primary text-white text-center p-3">
                    <h3 class="mb-0 fw-bold">{{ farmer.user.predictions.count }}</h3>
                    <div class="small opacity-75">{% trans "Total Scans" %}</div>
                </div>
            </div>
            <!-- Add more stat cards if needed -->
        </div>
        
        <div class="card">
            <div class="card-header bg-white py-3 fw-bold">{% trans "Recent Scans by this Farmer" %}</div>
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>{% trans "Image" %}</th>
                            <th>{% trans "Result" %}</th>
                            <th>{% trans "Confidence" %}</th>
                            <th>{% trans "Date" %}</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for scan in farmer.user.predictions.all|slice:":10" %}
                        <tr>
                            <td>
                                {% if scan.image %}
                                <img src="{{ scan.image.url }}" width="50" height="50" class="rounded object-fit-cover">
                                {% endif %}
                            </td>
                            <td><span class="badge {% if scan.disease_class == 'Healthy' %}bg-success{% else %}bg-warning text-dark{% endif %}">{{ scan.disease_class }}</span></td>
                            <td>{{ scan.confidence|floatformat:1 }}%</td>
                            <td>{{ scan.created_at|date:"M d, Y H:i" }}</td>
                            <td class="text-end"><a href="{% url 'disease_app:result' scan.pk %}" class="btn btn-sm btn-light">{% trans "View" %}</a></td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="5" class="text-center py-4 text-muted">{% trans "No scans recorded yet." %}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Delete Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">{% trans "Confirm Deletion" %}</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                {% trans "Are you sure you want to permanently delete this farmer's account and all their data?" %}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "Cancel" %}</button>
                <form method="post" action="{% url 'accounts:admin_delete_farmer' farmer.user.id %}">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-danger">{% trans "Delete" %}</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

files["templates/accounts/admin_panel/scans.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "All Scans" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div class="d-flex gap-2">
            <select class="form-select" style="width: auto;">
                <option value="">{% trans "All Diseases" %}</option>
                <option value="Healthy">{% trans "Healthy" %}</option>
                <option value="Leaf Spot">{% trans "Leaf Spot" %}</option>
                <option value="White Rust">{% trans "White Rust" %}</option>
            </select>
            <select class="form-select" style="width: auto;">
                <option value="">{% trans "All Risks" %}</option>
                <option value="High">{% trans "High Risk" %}</option>
                <option value="Low">{% trans "Low Risk" %}</option>
            </select>
        </div>
        <div class="input-group" style="max-width: 250px;">
            <input type="text" class="form-control" placeholder="{% trans 'Search...' %}">
            <button class="btn btn-outline-secondary"><i class="bi bi-search"></i></button>
        </div>
    </div>
    
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th>{% trans "Image" %}</th>
                    <th>{% trans "Farmer" %}</th>
                    <th>{% trans "Disease" %}</th>
                    <th>{% trans "Confidence" %}</th>
                    <th>{% trans "Date" %}</th>
                    <th class="text-end">{% trans "Action" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for scan in all_predictions %}
                <tr>
                    <td>
                        {% if scan.image %}
                        <img src="{{ scan.image.url }}" width="60" height="40" class="rounded border object-fit-cover">
                        {% endif %}
                    </td>
                    <td>{{ scan.user.username }}</td>
                    <td>
                        <span class="badge {% if scan.disease_class == 'Healthy' %}bg-success{% else %}bg-warning text-dark{% endif %}">
                            {{ scan.disease_class }}
                        </span>
                    </td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <span>{{ scan.confidence|floatformat:1 }}%</span>
                            <div class="progress flex-grow-1" style="height: 5px; width: 50px;">
                                <div class="progress-bar bg-primary" style="width: {{ scan.confidence|floatformat:0 }}%;"></div>
                            </div>
                        </div>
                    </td>
                    <td>{{ scan.created_at|date:"M d, Y H:i" }}</td>
                    <td class="text-end">
                        <a href="{% url 'disease_app:result' scan.pk %}" class="btn btn-sm btn-light">{% trans "View" %}</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="6" class="text-center py-5 text-muted">{% trans "No scans available." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% if all_predictions.has_other_pages %}
<nav class="mt-4">
    <ul class="pagination justify-content-center">
        {% if all_predictions.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ all_predictions.previous_page_number }}">{% trans "Previous" %}</a></li>
        {% endif %}
        <li class="page-item active"><span class="page-link">{{ all_predictions.number }}</span></li>
        {% if all_predictions.has_next %}
        <li class="page-item"><a class="page-link" href="?page={{ all_predictions.next_page_number }}">{% trans "Next" %}</a></li>
        {% endif %}
    </ul>
</nav>
{% endif %}
{% endblock %}
"""

files["templates/accounts/admin_panel/reports.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "Analytics & Reports" %}{% endblock %}

{% block dashboard_content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h5 class="mb-0 fw-bold">{% trans "Monthly Summary" %}</h5>
    <div class="d-flex gap-2">
        <input type="month" class="form-control" value="2023-10">
        <button class="btn btn-primary"><i class="bi bi-download"></i> {% trans "Export Report" %}</button>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-md-4">
        <div class="card h-100 border-start border-4 border-primary">
            <div class="card-body">
                <h6 class="text-muted">{% trans "Total Scans (This Month)" %}</h6>
                <h2 class="fw-bold mb-0">1,245</h2>
                <small class="text-success"><i class="bi bi-arrow-up-right"></i> 12% {% trans "from last month" %}</small>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 border-start border-4 border-success">
            <div class="card-body">
                <h6 class="text-muted">{% trans "Healthy Crops Detected" %}</h6>
                <h2 class="fw-bold mb-0">65%</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 border-start border-4 border-danger">
            <div class="card-body">
                <h6 class="text-muted">{% trans "High Risk Areas" %}</h6>
                <h2 class="fw-bold mb-0">3</h2>
                <small class="text-danger">{% trans "Requires immediate attention" %}</small>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-header bg-white py-3 fw-bold">{% trans "Disease Breakdown" %}</div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th>{% trans "Disease Name" %}</th>
                    <th>{% trans "Total Occurrences" %}</th>
                    <th>{% trans "Percentage" %}</th>
                    <th>{% trans "Trend" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for item in disease_stats|default:"" %}
                <tr>
                    <td><span class="badge bg-secondary">{{ item.name|default:"Leaf Spot" }}</span></td>
                    <td>{{ item.count|default:"450" }}</td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <span>{{ item.percentage|default:"35" }}%</span>
                            <div class="progress flex-grow-1" style="height: 6px;">
                                <div class="progress-bar bg-primary" style="width: {{ item.percentage|default:'35' }}%;"></div>
                            </div>
                        </div>
                    </td>
                    <td class="text-danger"><i class="bi bi-graph-up-arrow"></i> +5%</td>
                </tr>
                {% empty %}
                <tr>
                    <td><span class="badge bg-warning text-dark">Leaf Spot</span></td>
                    <td>250</td>
                    <td>
                        <div class="d-flex align-items-center gap-2"><span>25%</span><div class="progress flex-grow-1" style="height: 6px;"><div class="progress-bar bg-warning" style="width: 25%;"></div></div></div>
                    </td>
                    <td class="text-danger"><i class="bi bi-graph-up-arrow"></i> +2%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

files["templates/accounts/admin_panel/feedback.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "User Feedback" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white py-3 d-flex gap-3">
        <select class="form-select" style="max-width: 200px;">
            <option value="">{% trans "All Categories" %}</option>
            <option value="Bug">{% trans "Bug Reports" %}</option>
            <option value="Feature">{% trans "Feature Requests" %}</option>
        </select>
        <select class="form-select" style="max-width: 200px;">
            <option value="">{% trans "All Statuses" %}</option>
            <option value="pending">{% trans "Pending" %}</option>
            <option value="resolved">{% trans "Resolved" %}</option>
        </select>
    </div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th>{% trans "User" %}</th>
                    <th>{% trans "Category" %}</th>
                    <th>{% trans "Subject" %}</th>
                    <th>{% trans "Rating" %}</th>
                    <th>{% trans "Date" %}</th>
                    <th>{% trans "Status" %}</th>
                    <th class="text-end">{% trans "Action" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for item in feedbacks %}
                <tr>
                    <td>
                        <div class="fw-bold">{{ item.user.username }}</div>
                        <small class="text-muted">{{ item.user.email }}</small>
                    </td>
                    <td><span class="badge bg-secondary">{{ item.category }}</span></td>
                    <td style="max-width: 300px;" class="text-truncate" title="{{ item.subject }}">{{ item.subject }}</td>
                    <td class="text-warning">
                        {% for i in "12345"|make_list %}
                            {% if forloop.counter <= item.rating %}<i class="bi bi-star-fill"></i>{% else %}<i class="bi bi-star"></i>{% endif %}
                        {% endfor %}
                    </td>
                    <td>{{ item.created_at|date:"M d, Y" }}</td>
                    <td>
                        {% if item.is_resolved %}
                            <span class="badge bg-success">{% trans "Resolved" %}</span>
                        {% else %}
                            <span class="badge bg-warning text-dark">{% trans "Pending" %}</span>
                        {% endif %}
                    </td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#feedbackModal{{ item.id }}">{% trans "View" %}</button>
                    </td>
                </tr>
                
                <!-- Modal for each feedback -->
                <div class="modal fade" id="feedbackModal{{ item.id }}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">{% trans "Feedback Details" %}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <h6><strong>{% trans "Subject:" %}</strong> {{ item.subject }}</h6>
                                <p class="bg-light p-3 rounded text-secondary">{{ item.message }}</p>
                                <hr>
                                <form method="post" action="#">
                                    {% csrf_token %}
                                    <div class="form-check form-switch mb-3">
                                        <input class="form-check-input" type="checkbox" id="resolvedCheck{{ item.id }}" {% if item.is_resolved %}checked{% endif %}>
                                        <label class="form-check-label" for="resolvedCheck{{ item.id }}">{% trans "Mark as Resolved" %}</label>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">{% trans "Update Status" %}</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                {% empty %}
                <tr><td colspan="7" class="text-center py-5 text-muted">{% trans "No feedback entries found." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% if feedbacks.has_other_pages %}
<!-- Pagination component -->
{% endif %}
{% endblock %}
"""

files["templates/accounts/admin_panel/logs.html"] = """{% extends 'accounts/_dashboard_base.html' %}
{% load i18n %}

{% block page_title %}{% trans "System Logs" %}{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h6 class="mb-0 fw-bold">{% trans "Recent Activity & Security Logs" %}</h6>
        <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-funnel"></i> {% trans "Filter" %}</button>
    </div>
    <div class="table-responsive">
        <table class="table table-hover table-sm align-middle font-monospace small mb-0">
            <thead class="table-light">
                <tr>
                    <th>{% trans "Timestamp" %}</th>
                    <th>{% trans "Level" %}</th>
                    <th>{% trans "User" %}</th>
                    <th>{% trans "Action/Description" %}</th>
                    <th>{% trans "IP Address" %}</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td class="text-muted">{{ log.created_at|date:"Y-m-d H:i:s" }}</td>
                    <td>
                        {% if log.level == 'ERROR' %}<span class="badge bg-danger">ERROR</span>
                        {% elif log.level == 'WARNING' %}<span class="badge bg-warning text-dark">WARN</span>
                        {% else %}<span class="badge bg-info">INFO</span>{% endif %}
                    </td>
                    <td>{{ log.user.username|default:"System" }}</td>
                    <td>{{ log.description }}</td>
                    <td class="text-muted">{{ log.ip_address|default:"-" }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="text-center py-4">{% trans "No logs found." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

for filepath, content in files.items():
    with open(os.path.join(base_dir, filepath), 'w', encoding='utf-8') as f:
        f.write(content)

print("Batch 2 created")

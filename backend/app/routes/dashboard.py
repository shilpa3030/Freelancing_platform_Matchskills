from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)


# ——— Client ———
@bp.route('/dashboard/client')
def client_overview():
    return render_template('dashboard/client/overview.html')


@bp.route('/dashboard/client/profile')
def client_profile():
    return render_template('dashboard/client/profile.html')


@bp.route('/dashboard/client/messages')
def client_messages():
    return render_template('dashboard/client/messages.html')


@bp.route('/dashboard/client/my-projects')
def client_my_projects():
    return render_template('dashboard/client/my_projects.html')


@bp.route('/dashboard/client/projects/total')
def client_projects_total():
    return render_template('dashboard/client/projects_total.html')


@bp.route('/dashboard/client/projects/active')
def client_projects_active():
    return render_template('dashboard/client/projects_active.html')


@bp.route('/dashboard/client/projects/completed')
def client_projects_completed():
    return render_template('dashboard/client/projects_completed.html')


@bp.route('/dashboard/client/projects/new')
def client_project_new():
    return render_template('dashboard/client/project_new.html')


@bp.route('/dashboard/client/projects/<int:project_id>/bids')
def client_project_bids(project_id):
    return render_template('dashboard/client/project_bids.html', project_id=project_id)


# ——— Freelancer (student) ———
@bp.route('/dashboard/freelancer')
def freelancer_overview():
    return render_template('dashboard/freelancer/overview.html')


@bp.route('/dashboard/freelancer/profile')
def freelancer_profile():
    return render_template('dashboard/freelancer/profile.html')


@bp.route('/dashboard/freelancer/messages')
def freelancer_messages():
    return render_template('dashboard/freelancer/messages.html')


@bp.route('/dashboard/freelancer/projects')
def freelancer_projects_total():
    return render_template('dashboard/freelancer/projects_total.html')


@bp.route('/dashboard/freelancer/bids')
def freelancer_bids():
    return render_template('dashboard/freelancer/bids.html')


@bp.route('/dashboard/freelancer/bids/recent')
def freelancer_bids_recent():
    return render_template('dashboard/freelancer/bids_recent.html')


@bp.route('/dashboard/freelancer/rating')
def freelancer_rating():
    return render_template('dashboard/freelancer/rating.html')


@bp.route('/dashboard/freelancer/reviews')
def freelancer_reviews():
    return render_template('dashboard/freelancer/reviews.html')


@bp.route('/dashboard/freelancer/recommended')
def freelancer_recommended():
    return render_template('dashboard/freelancer/recommended.html')

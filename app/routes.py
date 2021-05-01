from app import app, db
from flask import render_template, request, flash, redirect, url_for
from app.forms import UserInfoForm, LoginForm, AddSiteForm, EditSiteForm, AddReportForm, UpdateUserInfoForm, UpdatePasswordForm
from app.models import User, Report, Site, ReportUpdate, SiteUpdate, NewAction, NewDoc
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.scrape import InitialSiteScan, ReportUpdateScan
import datetime as dt

@app.route('/', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        my_reports = current_user.reports
        context = {
            'title': 'GecMonitor | My Reports',
            'my_reports': current_user.reports,
            'ReportUpdateScan': ReportUpdateScan,
            'dt': dt
        }
        if request.method == "POST":
            for i in range(len(my_reports)):
                if request.form.get(f"report_id{my_reports[i].id}"):
                    new_scan = ReportUpdateScan(my_reports[i].id)
                    new_scan.start()
                    flash(f"We've prepared an update for {my_reports[i].report_name}!")
                    return redirect(url_for("index"))
        return render_template('index.html', **context)
    else:
        return render_template('index.html')

@app.route('/about')
def about():
    title = "GecMonitor | About"
    return render_template('about.html', title=title)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title = "GecMonitor | Sign Up"
    form = UserInfoForm()
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data 
        last_name = form.last_name.data 
        email = form.email.data 
        password = form.password.data 
        new_user = User(first_name, last_name, email, password)
        db.session.add(new_user)
        db.session.commit()
        flash("You have successfully signed up!", "success")
        return redirect(url_for('index'))
    return render_template('signup.html', title=title, form=form)


@app.route('/accountdetails/<int:current_user_id>', methods=['GET', 'POST'])
@login_required
def accountdetails(current_user_id):
    title = "GecMonitor | Account Details"
    return render_template('account_details.html', title=title, current_user=current_user)

@app.route('/editaccount/<int:current_user_id>', methods=['GET', 'POST'])
@login_required
def editaccount(current_user_id):
    title = "GecMonitor | Edit Account"
    form = UpdateUserInfoForm(first_name=current_user.first_name, last_name=current_user.last_name, email=current_user.email)
    if request.method == 'POST' and form.validate():
        current_user.first_name = form.first_name.data 
        current_user.last_name = form.last_name.data 
        current_user.email = form.email.data 
        db.session.commit()
        flash("You have successfully signed up!", "success")
        return redirect(url_for('accountdetails', current_user_id=current_user.id))
    return render_template('edit_account.html', title=title, form=form, current_user=current_user)

@app.route('/updatepassword/<int:current_user_id>', methods=['GET', 'POST'])
@login_required
def updatepassword(current_user_id):
    title = "GecMonitor | Update Password"
    form = UpdatePasswordForm()
    if request.method == 'POST' and form.validate():
        current_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash("You have successfully signed up!", "success")
        return redirect(url_for('accountdetails', current_user_id=current_user.id))
    return render_template('update_password.html', title=title, form=form, current_user=current_user)

@app.route('/deleteaccount/<int:user_id>', methods=['POST'])
@login_required
def account_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted", "danger")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "GecMonitor | Login"
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        email = form.email.data 
        password = form.password.data 
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password, password):
            flash('Incorrect email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash("Welcome back!", "success")
        return redirect(url_for('index'))
    return render_template('login.html', title=title, form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('See you next time!', 'primary')
    return redirect(url_for('index'))


@app.route('/addsite', methods=['GET', 'POST'])
@login_required
def addsite():
    title = "GecMonitor | Add a Site"
    site = Site()
    form = AddSiteForm()
    if request.method == 'POST' and form.validate():
        site_name = form.site_name.data
        gt_global_id = form.gt_global_id.data
        # This adds the new site to the Site table via User.sites, meaning the "user_id" value in the Site table will be the current user's
        new_site = Site(site_name=site_name, gt_global_id=gt_global_id)
        current_user.sites.append(new_site)
        db.session.add(new_site)
        db.session.commit()
        flash(f"{site_name} has been added to your sites!")
        return redirect(url_for("mysites"))
    return render_template("add_site.html", title=title, site=site, form=form)

@app.route('/editsite/<int:site_id>', methods=['GET', 'POST'])
@login_required
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    title = f"GecMonitor | Edit {site.site_name}"
    # create list of site ids currently associated with the site
    form = EditSiteForm(site_name=site.site_name)
    context = {
        'site': site,
        'title': title,
        'form': form,
        'gt_global_id': site.gt_global_id
    }
    if request.method == 'POST' and form.validate():
        site.site_name = form.site_name.data
        db.session.commit()
        flash(f"{site.site_name} has been updated!")
        return redirect(url_for("mysites"))
    return render_template("edit_site.html", **context)


@app.route('/deletesite/<int:site_id>', methods=['POST'])
@login_required
def site_delete(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    flash("Your report has been deleted", "danger")
    return redirect(url_for('index'))

@app.route('/mysites')
@login_required
def mysites():
    context = {
        'title': 'GecMonitor | My Sites',
        'my_sites': current_user.sites
    }
    return render_template('my_sites.html', **context)

@app.route('/addreport', methods=['GET', 'POST'])
@login_required
def addreport(): 
    form = AddReportForm()
    report = Report()
    context = {
        'title': "GecMonitor | Add a Report",
        'report': report,
        'form': form,
        'sites': current_user.sites
    }   
    if request.method == 'POST' and form.validate():
        report_name = form.report_name.data
        selected_sites = form.current_user_sites.data
        description = form.description.data
        new_report = Report(report_name=report_name, sites=selected_sites, description=description)
        current_user.reports.append(new_report)
        db.session.add(new_report)
        db.session.commit()
        sites_list = [[site.id, site.gt_global_id] for site in new_report.sites]
        initial_site_scan = InitialSiteScan(sites_list, new_report.id)
        initial_site_scan.start()
        flash(f"{report_name} has been added to your sites!")
        return redirect(url_for("index"))
    return render_template("add_report.html", **context)

@app.route('/editreport/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    title = f"GecMonitor | Edit {report.report_name}"
    # create list of site ids currently associated with the report
    current_sites = [site.id for site in report.sites]
    form = AddReportForm(report_name=report.report_name, current_user_sites=report.sites, description=report.description)
    if request.method == 'POST' and form.validate():
        report.report_name = form.report_name.data
        # Isolate newly added sites to create sites_list
        new_sites = [site for site in form.current_user_sites.data if site.id not in current_sites]
        report.sites = form.current_user_sites.data
        report.description = form.description.data
        db.session.commit()
        sites_list = [[site.id, site.gt_global_id] for site in new_sites]
        initial_site_scan = InitialSiteScan(sites_list, report.id)
        initial_site_scan.start()
        flash(f"{report.report_name} has been updated!")
        return redirect(url_for("index"))
    return render_template("edit_report.html", title=title, report=report, form=form)


@app.route('/delete/<int:report_id>', methods=['POST'])
@login_required
def report_delete(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash("Your report has been deleted", "danger")
    return redirect(url_for('index'))


@app.route('/<int:report_id>')
@login_required
def report_details(report_id):
    report = Report.query.get_or_404(report_id)
    report_updates = report.report_updates
    sites_list = [report.sites[i].gt_global_id for i in range(len(report.sites))]
    context = {
        'title': f'GecMonitor | {report.report_name}',
        'report': report,
        'report_updates': report_updates,
        'sites_list': sites_list,
        'dt': dt
    }
    return render_template('report_details.html', **context)


@app.route('/<int:report_id>/<int:report_update_id>')
@login_required
def report_update(report_id, report_update_id):
    report = Report.query.get_or_404(report_id)
    report_update = ReportUpdate.query.get_or_404(report_update_id)
    site_updates = report_update.site_updates
    site_update_ids = [site_update.id for site_update in site_updates]
    sites_list = [[site_update.site_id, site_update.site.gt_global_id] for site_update in site_updates]
    context = {
        'title': f'GecMonitor | {report.report_name}: {report_update.scraped_on} Report',
        'report': report,
        'report_update': report_update,
        'Site': Site(),
        'site_updates': site_updates,
        'dt': dt
    }
    return render_template('report_update.html', **context)



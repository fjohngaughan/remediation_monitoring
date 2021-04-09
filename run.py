from app import app, db
from app.models import User, Report, Site, ReportUpdate, SiteUpdate, NewAction, NewDoc

if __name__ == '__main__':
    app.run(debug=True)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Report': Report, 'Site': Site, 
    'ReportUpdate': ReportUpdate, 'SiteUpdate': SiteUpdate, 'NewAction': NewAction,
    'NewDoc': NewDoc}
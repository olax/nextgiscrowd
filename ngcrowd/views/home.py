# -*- coding: utf-8 -*-

from ngcrowd.models import DBSession, User, EntityProperty, Application
from ngcrowd.security import generate_session_id
from pyramid.view import view_config
from sqlalchemy.sql.expression import asc
from sqlalchemy.orm import joinedload

@view_config(route_name='home', renderer='base.mako')
def home(request):
    user_name = None
    if hasattr(request, 'cookies') and 'sk' in request.cookies.keys() and 'sk' in request.session and \
                    request.session['sk'] == request.cookies['sk'] and 'u_name' in request.session:
        user_name = request.session['u_name']

    session = DBSession()

    fields = session.query(EntityProperty)\
        .options(joinedload('reference_book_values'))\
        .order_by(EntityProperty.visible_order)\
        .all()

    app = session.query(Application).one()
    session.close()

    return {
        'u_name': user_name,
        'project': 'ngcrowd',
        'fields': fields,
        'static_version': request.registry.settings['static_version'],
        'app': app
    }

@view_config(route_name='home', request_method='POST', renderer='base.mako')
def home_signin(request):
    result = home(request)

    if 'sign_out' in request.POST.keys():
        request.session.invalidate()
        result['u_name'] = None

    else:
        email = request.POST['mail']
        password = request.POST['pass']

        session = DBSession()
        user = session.query(User) \
            .filter(User.email == email, User.password == User.password_hash(password, 'rte45EWRRT')) \
            .first()
        if user:
            request.session['sk'] = generate_session_id()
            request.session['u_name'] = user.display_name
            request.session['u_id'] = user.id
            request.response.set_cookie('sk', value=request.session['sk'], max_age=86400)
            result['u_name'] = user.display_name
        session.close()

    result['static_version'] = request.registry.settings['static_version']

    return result
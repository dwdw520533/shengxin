# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'

import logging
import traceback
import web
import settings
from sqlalchemy.orm import scoped_session, sessionmaker


urls = (
    "/weagent/service", "package_handler.Method",
)


def load_sqla(handler=None):
    web.ctx.db = scoped_session(sessionmaker(bind=settings.engine))
    try:
        return handler() if handler else None
    except web.HTTPError:
        errmsg = traceback.format_exc()
        logging.error(errmsg)
        web.ctx.db.commit()
        raise
    except:
        errmsg = traceback.format_exc()
        logging.error(errmsg)
        web.ctx.db.rollback()
        raise
    finally:
        web.ctx.db.commit()
        # If the above alone doesn't work, uncomment
        # the following line:
        #web.ctx.db.expunge_all()


app = web.application(urls, locals())
app.add_processor(load_sqla)

application = app.wsgifunc()

if __name__ == '__main__':
    app.run()
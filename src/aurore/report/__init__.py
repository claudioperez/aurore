
def init_report(args, config)->tuple:
    if args.template=="tmpl-0001":
        from .tmpl_0001 import init, item, close
    if args.template=="tmpl-0002":
        from .tmpl_0002 import init, item, close
    if args.template=="tmpl-0003":
        from .tmpl_0003 import init, item, close
    return init, item, close

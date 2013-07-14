from pecan import make_app
from smiley.web import model
from smiley.web import hooks


def setup_app(config):

    model.init_model()

    return make_app(
        config.app.root,
        static_root=config.app.static_root,
        template_path=config.app.template_path,
        logging={},  # let cliff configure logging, otherwise output repeats
        debug=getattr(config.app, 'debug', False),
        force_canonical=getattr(config.app, 'force_canonical', True),
        guess_content_type_from_ext=getattr(
            config.app,
            'guess_content_type_from_ext',
            True),
        hooks=[
            hooks.DBHook(config.smiley.database_name),
        ],
    )

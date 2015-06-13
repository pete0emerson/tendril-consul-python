import click

class Config():
    def __init__(self, application, environment, debug, verbose, consul_server, consul_port, consul_token, consul_use_ssl):
        self.application = application
        self.environment = environment
        self.debug = debug
        self.verbose = verbose
        self.consul_server = consul_server
        self.consul_port = consul_port
        self.consul_token = consul_token
        self.consul_use_ssl = consul_use_ssl

@click.group()
@click.option('--application', envvar='APPLICATION')
@click.option('--environment', envvar='ENVIRONMENT')
@click.option('-d', '--debug', envvar='DEBUG', default=False, is_flag=True, help='Debug mode')
@click.option('-v', '--verbose', envvar='VERBOSE', count=True, help='Verbose mode')
@click.option('--consul_server', envvar='CONSUL_SERVER', default='localhost', help='Consul hostname (default: localhost)')
@click.option('--consul_port', envvar='CONSUL_PORT', default=8500, help='Consul port (default: 8500)')
@click.option('--consul_token', envvar='CONSUL_TOKEN')
@click.option('--consul_use_ssl', envvar='CONSUL_USE_SSL', default=False, is_flag=True)
@click.pass_context
def cli(ctx, application, environment, debug, verbose, consul_server, consul_port, consul_token, consul_use_ssl):
    """help me obiwan kenobi you're my only hope"""
    ctx.obj = Config(application, environment, debug, verbose, consul_server, consul_port, consul_token, consul_use_ssl)

@cli.group()
@click.pass_obj
def config(ctx):
    """Manipulate application configurations."""
    pass

@config.command(name='list')
@click.pass_obj
def config_list(ctx):
    """List available configuration versions."""
    pass

@config.command(name='show')
@click.pass_obj
@click.option('--decrypt', default=False, is_flag=True, help='Decrypt encrypted values')
def config_show(ctx, decrypt):
    """Show a specific configuration version."""
    pass

@config.command(name='edit')
@click.pass_obj
def config_edit(ctx):
    """Edit a configuration."""
    pass

@config.command(name='promote')
@click.pass_obj
@click.argument('version')
def config_promote(ctx, version):
    """Promote a configuration version."""
    pass

@cli.group()
@click.pass_obj
def key(ctx):
    """Manipulate application keys."""
    pass

@key.command(name='generate')
@click.pass_obj
def key_generate(ctx):
    """Generate a secret key."""
    pass

@key.command(name='rotate')
@click.pass_obj
def key_generate(ctx):
    """Rotate a secret key."""
    pass

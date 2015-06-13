# Overview

Tendril is a configuration tool that helps you manage your application
configurations. It uses [Hashicorp's consul](https://www.google.com "consul") as
a backend data store, and has two interfaces: a CLI and an API. Centered around
the core concepts of "environments" and "applications", application
configurations are versioned, and sensitive data can be encrypted. All sets of
configurations are versioned for easy deployment and rollback.

# Core concepts

A configuration is a set of key/value pairs that apply to a specific environment
and application.

Typically, an environment is something like `prod`, `stage`, `dev`, `local`, but
the definition is up to you.

Likewise, an application would usually be something like `api`, `proxy`,
`webapp`, et cetera.

The configurations are versioned, starting with 1 and incrementing by 1. Version
numbers are unique across the application.

This means that if you have a configuration version 1 for your `stage`
environment / `api` application, you will not have a configuration version 1 for
your `prod` environment / `api` application. This is by design! You will likely
have environment specific variables, and so your configurations are different
and unique across environments.

It is also possible to share variables, show which configurations are effected
when changing those shared variables, and discourage promotion when a shared
variable is in use.
# Installation

    pip install tendril

# Configuration

## Server configuration

Tendril relies on Consul's ACLs to allow you access to the right subset of
configurations. You can permit access to read configurations with or without
the ability to decrypt sensitive key / value pairs, and you can permit access
to write configurations with or without the same decryption abilities. This
means that you can allow someone to copy a config with encrypted data in it
without being privy to what that encrypted data is.

Tendril requires access to three subtrees in the Consul database. It stores
its configuration under the `/tendril` prefix in `/tendril/configs`,
`/tendril/index`, `/tendril/metadata`, and `/tendril/keys`.

`/tendril/configs` stores the actual configuration key / values in the following
pattern:

`/tendril/configs/{{ environment }}/{{ application }}/{{ version }}/{{ key }}/{{ value }}`

`/tendril/index` is an atomically incremented counter used to determine the next
version of a configuration. This is done on a per application basis, regardless
of environment.

`/tendril/metadata` contains information about who created what configuration when.

`/tendril/keys` contains the secret necessary to encrypt / decrypt sensitive data.

Superuser access can be granted in Consul by the following Consul ACL:

```
key "tendril/" {
  policy = "write"
}
```

## Client configuration


Tendril's CLI can be run without any configuration. However, if you desire to do
so, your command can run quite long. For example, here's how you might show
version `10` of a `mywebapp` configuration in the `prod` environment:

    tendril --application mywebapp --environment prod --consul_server consul.mycompany.com --consul_port 443 --consul_token 1ae5c152-d443-9890-a266-952b27433ecc --consul_use_ssl config show 10

That's 190 characters! Fortunately, we can accomplish the same thing by stuffing
most of those options in a JSON file. tendril will read its configuration from
(in order of least precidence)`/etc/tendril.cfg`, `~/.tendril`, `.tendril`, and
the command line arguments.

If we put this JSON in '.tendril':

    {
      "application" : "mywebapp",
      "environment" : "prod",
      "consul_server" : "consul.mycompany.com",
      "consul_port" : 443,
      "consul_token" : "1ae5c152-d443-9890-a266-952b27433ecc",
      "consul_use_ssl" : true
    }

then we can run a command identical to the one above:

    tendril config show 10

Since the CLI arguments takes the highest precidence, you can override any of
the configurations (most commonly the `application` and `environment`):

    tendril --environment=stage config show 9

# Getting Started

Let's get started with a sample tendril workflow. Let's assume you have
configured tendril properly as above.

## Create a configuration

First, let's create a configuration.

    tendril config edit

This will throw you into an editor (`vim` if the `EDITOR` environment variable
is not set)

We specify our variables as key/value pairs separated by an `=`. The value must
be quoted.

    DB_HOST="db.mycompany.com"
    DB_USER="alice"
    DB_PASS="myplaintextsecret" # decrypted

Note the comment to the right of the `DB_PASS` key/value. Given sufficient
permissions, tendril will encrypt this entry. Tell the editor to save the
document, and this configuration will be saved in the consul database.

## List all configurations

If you ask tendril to list the configurations, you'll see that you've created
version `1`.

    tendril config list
    1

## Promote a configuration version

You can "promote" a version. This marks it as the current version.

    tendril config promote --version=1
    tendril config list
    1 current

## Using a configuration version

In order to use these variables in your application, you run tendril and source
the variables as environment variables prior to running your code. It might look
something like this:

    #!/bin/sh

    eval `tendril config show --decrypt`
    python myapp.py

It is then expected that your application will honor those environment variables
appropriately. Note that the consul credential used by tendril must have
permissions to decrypt the sensitive data in order to have the plaintext version
of the value stored. Also note that in this fashion, the configuration variables
are never stored on disk on the application server. While this adds a small
amount of security, a clever person could figure out that the token that tendril
is using is the key to getting at this sensitive data. However, your deployment
mechanism could pass the token in remotely in order to start your application,
adding additional security.

The output of the tendril command above looks identical to the way it was
entered into the editor. If you omit the `--decrypt` flag, it will look slightly
different:

    DB_HOST="db.mycompany.com"
    DB_USER="alice"
    DB_PASS="gAAAAABVN9-bGKrKdn-GoZYmeXrqvZdTwz20C_rvbX4mQzJ1UshY-BWQuPSNwd2prNrDpthk3GpLW11Pc0PPjgSlEHthGwl0o0iy0GX1h0tPw-ckCz5w0h0=" # encrypted

You may have permissions to create new configuration versions (and therefore can
copy the `DB_PASS` credential elsewhere), but **not** have permissions to see
the credential itself.

## Create another configuration based on the previous configuration

Okay, let's create a new configuration. Most of the time you'll probably want to
start with an existing configuration. Add the `--version` flag to your `edit`
command.

    tendril config edit --version=1

Now you can add, edit, or delete key/value pairs. When you save your changes, a
new configuration version will be created. You can now list all of your configs:

    tendril config list
    2
    1 current

and then promote the new version when desired:

    tendril config promote --version=2
    tendril config list
    2 current
    1

# CLI

Extensive help for all commands can be requested by using the `--help` option.

    $ tendril --help

    Usage: tendril [OPTIONS] COMMAND [ARGS]...

      help me obiwan kenobi you're my only hope

    Options:
      --application TEXT
      --environment TEXT
      -d, --debug            Debug mode
      -v, --verbose          Verbose mode
      --consul_server TEXT   Consul hostname (default: localhost)
      --consul_port INTEGER  Consul port (default: 8500)
      --consul_token TEXT
      --consul_use_ssl
      --help                 Show this message and exit.

    Commands:
      config  Manipulate application configurations.

Like the [git](http://git-scm.com/ "git") command line,
tendril uses commands and sub-commands  to accomplish its tasks.


## Commands

### config

    $ tendril config --help
    Usage: tendril config [OPTIONS] COMMAND [ARGS]...

      Manipulate application configurations.

    Options:
      --help  Show this message and exit.

    Commands:
      edit     Edit a configuration.
      list     List available configuration versions.
      promote  Promote a configuration version.
      show     Show a specific configuration version.

#### list

    $ tendril config list --help
    Usage: tendril config list [OPTIONS]

      List available configuration versions.

    Options:
      --help  Show this message and exit.

#### edit

    $ tendril config edit --help
    Usage: tendril config edit [OPTIONS]

      Edit a configuration.

    Options:
      --version TEXT
      --force
      --inherit / --no-inherit  Interpret inherited variables
      --help                    Show this message and exit.

#### show

    $ tendril config show --help
    Usage: tendril config show [OPTIONS]

      Show a specific configuration version.

    Options:
      --version TEXT
      --decrypt                 Decrypt encrypted values
      --inherit / --no-inherit  Interpret on inherited variables
      --help                    Show this message and exit.

#### promote

    $ tendril config promote --help
    Usage: tendril config promote [OPTIONS]

      Promote a configuration version.

    Options:
      --version TEXT
      --help          Show this message and exit.

# Advanced Usage

Tendril can inherit values from other configurations. For example, if you have a
variable stored in `environment=prod`, `application=base`, `version=5`,
`key=foo`, it can be used in another configuration by storing a value of
`{{ prod/base/5/foo }}`. Currently, recursion is not supported.

`base` application that will be inherited from:

    $ tendril --environment=testenv --application=base config show --version=5
    # Version: 5

    export basevar="base variable"

`testapp` application that inherits from `base`:

    $ tendril --environment=testenv --application=testapp config show --version=16
    # Version: 16

    export bar="baz"
    export foo="bar"
    export inherited="base variable"

`testapp` application showing the inheritance:

    $ tendril --environment=testenv --application=testapp config show --version=16 --no-inherit
    # Version: 16

    export bar="baz"
    export foo="bar"
    export inherited="{{ testenv/base/2/basevar }}"

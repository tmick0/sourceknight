# sourceknight

A simple dependency manager and build system for sourcemod projects

## Overview

`sourceknight` was created to simplify the process of building and developing sourcemod plugins. It lets you specify dependencies in a configuration file so they can be automatically updated, and manages the sourcemod build tree for you.

Right now, `sourceknight` is essentially a proof of concept -- it is only capable of building some simple projects on Linux hosts. It can acquire and unpack dependencies from git repos or tar archives and run `spcomp`. Additional functionality will be implemented as needed (or maybe requested).

## Building and installing

You can now install `sourceknight` from pypi: `pip install sourceknight`.

Alternatively, compile and install from source: `pip install .`.

## Defining a project

The core concept of `sourceknight` is the *project*, which encapsulates any plugins you're trying to build and their dependencies (including sourcemod itself).

A *project directory* will include a *project file* called `sourceknight.yaml` that defines all the parameters of your project, including its name,
its dependencies, and the plugins it will build. The project file is written in [YAML](https://en.wikipedia.org/wiki/YAML).

If building your own plugin, your project directory will likely also include any sourcepawn files you need, but this is optional --
you can also also use `sourcepawn` just to simplify compiling a collection of third party plugins by declaring them as dependencies.

A minimal `sourceknight.yaml` might look something like this:

```yaml
project:
  name: myplugin-example
  sourceknight: 0.2
  dependencies:
    - name: sourcemod
      type: tar
      version: 1.10.0-git6503
      location: https://sm.alliedmods.net/smdrop/1.10/sourcemod-1.10.0-git6503-linux.tar.gz
      unpack:
      - source: /addons
        dest: /addons
  root: /
  targets:
    - myplugin
```

Here, we're just telling `sourceknight` where to download `sourcemod` itself, and specifying that we want to build `myplugin`.

Details about the individual sections of the project file follow.

### Metadata

The `name` key specifies the name of your project. (Technically, it isn't even required to be specified right now, but that might change.)

The `sourceknight` key specifies the version of sourceknight this package was designed for. This allows users to be warned if they need to update.

### Dependencies

Dependencies describe any external code, including external plugins you want to build, include files you need, and even `sourcemod` itself. You will likely need to specify the `sourcemod` dependency for every project because it provides the compiler for sourcepawn code (`spcomp`) as well as several essential headers.

The most important keys in your dependency declarations are its `name`, its `type`, and `unpack` instructions. Each dependency must have a unique `name`. The `type` tells `sourceknight` how to acquire the dependency.

Depending on the `type`, different additional fields may be required. Right now, only two `type`s are supported: `git` and `tar`, which refer to git repositories and tar archives, respectively.

**`tar`:**

- `location`: URL to download the tar file from
- Optional: `version`, which can be manually specified to help prevent re-downloading the same file unnecessarily

**`git`:**

- `repo`: Git repository URL to clone

Both of these types of dependencies must have an `unpack` block, which tells us which files to copy out of them and where they belong relative to the `sourceknight` *build root*. The build root is a hidden directory maintained by `sourceknight` which will contain the entire sourcemod tree (i.e., it will contain the `addons` directory) as well as any other dependencies and sources specified by your project.

In the example above, the `unpack` declaration for `sourcemod` says to unpack the `/addons` directory to `/addons`. In sourcemod's case, this means we're copying the entire contents of the archive. However, the [extended example project file](example/sourceknight.yaml) includes other examples of unpack declarations. Note that the destination of an unpack operation is always relative to the build tree. Multiple `source`, `dest` pairs can be specified in the `unpack` section if needed.

### Build specification

The last part of the example specifies how to build the project.

The `root` key tells `sourceknight` where in the project directory your source tree originates. That is, a sourcemod project will typically have a structure containing `/addons/sourcemod/scripting/` -- in this case `root` will refer to the directory that contains `addons`, relative to your project directory. Note that your project does not need to specify a `root` if you aren't compiling any sources of your own (i.e., you're only compiling external plugins you specified as dependencies).

The `targets` list contains all the plugins you want built, whether from dependencies or your own sources. Each of these should have a corresponding `.sp` file in the `/addons/sourcemod/scripting` directory and will result in a `.smx` file being generated.

You can optionally specify two additional keys that tell `sourceknight` how to compile your project: `compiler` to override the default location of `spcomp`, and `workdir` to define the working directory for compilation (both relative to the build root).

## Building your project

The easy way to get `sourceknight` to build your project is to simply go to your project directory and run the `build` command:

```bash
example$ sourceknight build
Updating...
Updating: sourcemod
 Downloading https://sm.alliedmods.net/smdrop/1.10/sourcemod-1.10.0-git6503-linux.tar.gz...
Updating: sourcecolors
 Cloning from https://github.com/Ilusion9/sourcecolors-inc-sm
Updating: extend-map
 Cloning from https://github.com/Ilusion9/extend-map-sm
Unpacking...
Unpacking sourcemod...
 Unpacking archive...
 Extracting addons to addons
Unpacking sourcecolors...
 Extracting include to addons/sourcemod/scripting/include
Unpacking extend-map...
 Extracting scripting to addons/sourcemod/scripting
Compiling...
Copying sources...
Building extendmap...
 ...
Building example...
 ...
```

The `build` command, when run from your project directory, will automatically perform all the steps needed to build your plugins, and the `.smx` files will be output there (i.e., to the working directory). If you want to put the compiled plugins somewhere else, you can pass the `-o` option:

```
example$ sourceknight build -o compiled
```

If you don't want to run `sourceknight` from your project directory every time, you can specify `-p` to provide the path to it:

```bash
sourceknight$ sourceknight -p example build
```

The `-p` option is applicable to every `sourceknight` subcommand, and must be specified before it.

Behind the scenes, `build` is running three independent steps: `update`, `unpack`, and `compile`. The `update` step downloads and caches dependencies, `unpack` extracts them into the build directory, and `compile` compiles the plugins.

There is also a `status` command, which provides useful information about the version of dependencies which are cached and unpacked:

```bash
example$ sourceknight status
sourcemod
 Cached version: 1.10.0-git6503
 Unpacked version: 1.10.0-git6503
sourcecolors
 Cached version: d7b112be7c2a88a3d7b5b124017c102ce320dee3
 Unpacked version: d7b112be7c2a88a3d7b5b124017c102ce320dee3
extend-map
 Cached version: 5c3d88be409f9c826bf7a84f319c826eaef5ceb5
 Unpacked version: 5c3d88be409f9c826bf7a84f319c826eaef5ceb5
```

If you want to learn more, all of the `sourceknight` subcommands have additional information available with the `-h` flag:

```bash
$ sourceknight unpack -h
usage: sourceknight unpack [-h] [-a,--all] [-c,--clean]

optional arguments:
  -h, --help  show this help message and exit
  -a,--all    Force unpacking all dependencies, even if they have not been updated
  -c,--clean  Force creating a new unpack directory, even if one already exists
```

## sourceknight state

`sourceknight` will create a directory called `.sourceknight` in your project directory. All the cached dependencies and the build directory are located within it. If you want to clean up after yourself, or if something goes horribly wrong, delete `.sourceknight`.

## License 

This project is made available under the terms of the [MIT license](LICENSE).

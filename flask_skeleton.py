# Standard imports #

import sys
import os
import argparse
import codecs
import subprocess
import shutil
from shutil import which
import platform


# PyPi imports #

import jinja2


# Globals #

cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))


# Jinja2 environment #

template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(script_dir, "templates"))
template_env = jinja2.Environment(loader=template_loader)


def get_arguments(argv):
    parser = argparse.ArgumentParser(description='Scaffold a Flask Skeleton.')
    parser.add_argument('appname', help='The application name')
    parser.add_argument('-s', '--skeleton', help='The skeleton folder to use.')
    parser.add_argument('-y', '--yarn', help='Install dependencies via yarn')
    parser.add_argument('-g', '--git', action='store_true')
    args = parser.parse_args()
    return args


def generate_brief(args):
    template_var = {
        'pyversion': platform.python_version(),
        'appname': args.appname,
        'yarn': args.yarn,
        'skeleton': args.skeleton,
        'path': os.path.join(cwd, args.appname),
        'git': args.git
    }
    template = template_env.get_template('brief.jinja2')
    return template.render(template_var)


def main(args):
    print("\nScaffolding...")

    # Variables #

    appname = args.appname
    fullpath = os.path.join(cwd, appname)
    skeleton_dir = args.skeleton

    # Tasks #

    # Copy files and folders
    print("Copying files and folders...")
    shutil.copytree(os.path.join(script_dir, skeleton_dir), fullpath)

    # Create config.py
    print("Creating the config...")
    secret_key = codecs.encode(os.urandom(32), 'hex').decode('utf-8')
    template = template_env.get_template('config.jinja2')
    template_var = {
        'secret_key': secret_key,
    }

    with open(os.path.join(fullpath, 'config.py'), 'w') as fd:
        fd.write(template.render(template_var))

    # Git init
    if args.git:
        print("Initializing Git...")
        output, error = subprocess.Popen(
            ['git', 'init', fullpath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        if error:
            with open('git_error.log', 'w') as fd:
                fd.write(error.decode('utf-8'))
                print("Error with git init")
                sys.exit(2)
        shutil.copyfile(
            os.path.join(script_dir, 'templates', '.gitignore'),
            os.path.join(fullpath, '.gitignore')
        )



if __name__ == '__main__':
    arguments = get_arguments(sys.argv)
    print(generate_brief(arguments))
    proceed = input("\nProceed (yes/no)? ")
    valid = ["yes", "y", "no", "n"]
    while True:
        if proceed.lower() in valid:
            if proceed.lower() == "yes" or proceed.lower() == "y":
                main(arguments)
                print("Done!")
                break
            else:
                print("Goodbye!")
                break
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")
            proceed = input("\nProceed (yes/no)? ")
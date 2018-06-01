#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import argparse
import subprocess
import yaml
import os


def git_checkout(repoDir, branch):
    cmd = ['git', 'checkout', branch]
    return run_command(cmd, repoDir)


def git_status(repoDir):
    cmd = ['git', 'status']
    return run_command(cmd, repoDir)


def run_command(command, cwd):
    """
    Run a command.

    command: sequence of arguments
    return status, std_out, std_err
    """
    pop = subprocess.Popen(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, cwd=cwd)
    exit_status = pop.wait()
    if pop.stdout is not None:
        out = pop.stdout.read()
    else:
        out = ''
    if pop.stderr is not None:
        err = pop.stderr.read()
    else:
        err = ''
    return exit_status, out, err


def synchronize_depositories(depositories_path, main_depo):
    # Find the yaml file of the main depository
    project_requirements_path = os.path.normpath(os.path.join(depositories_path,
                                                              main_depo,
                                                              "project_requirements.yaml"))
    if not os.path.isfile(project_requirements_path):
        raise RuntimeError("The requirement file cannot be found "
                           "at the following path: {}".format(project_requirements_path))

    # Read the yaml file of the main depository
    with open(project_requirements_path, "r") as stream:
        yaml_file = yaml.load(stream)
        req_list = yaml_file["depositories_requirements"]

        # For each requirement, do a series a checks
        for req in req_list:
            # Check if the directory really exists
            req_dir = os.path.normpath(os.path.join(depositories_path, req["name"]))
            if not os.path.isdir(req_dir):
                raise RuntimeError("Directory {} listed in {} cannot be found in {}".format(
                                    req["name"], project_requirements_path, depositories_path)
                                   )

            # Check if this directory is a git depository
            exit_status, out, err = git_status(req_dir)
            if exit_status != 0:
                raise RuntimeError("GIT returned an error in directory {}".format(req_dir))

            # Check if this git depository is clear
            if "la copie de travail est propre" not in out:
                raise RuntimeError("Working directory is not clear in {}".format(req_dir))

            # Check if the wanted branch or tag exists
            for target in ["tag", "branch"]:
                if req[target] is not None:
                    exit_status, out, err = run_command(["git", target], req_dir)
                    target_list = [t[2:] for t in out.split('\n')]
                    if not req[target] in target_list:
                        raise RuntimeError("Wanted {} named '{}' is not found "
                                           "in the repository {}".format(
                                            target, req[target], req_dir
                                            ))
                    break

            # All checks passed ==> Checkout the given branch or tag
            exit_status, out, err = git_checkout(req_dir, req[target])
            if exit_status != 0:
                raise RuntimeError("`git checkout` returned an error"
                                   " in directory {}".format(req_dir))

    # Here, all requirements have been processed correctly
    print("=== All requirements are synchronized ! ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synchronize git repositories dependencies.')
    parser.add_argument("depositories_path", help=("Path to the directory containing "
                                                   "all depositories to synchronize."))
    parser.add_argument("main_depo", help="Name of the depository which provides the requirements.")
    args = parser.parse_args()

    synchronize_depositories(args.depositories_path, args.main_depo)

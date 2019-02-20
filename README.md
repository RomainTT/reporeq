# Reporeq

This tools is used to manage dependencies between different git depositories.

Example: in the directory `dir/` there are 3 different repositories A, B, C.
In the current branch of A, A uses the branch b1 of B and the branch c1 of C.
This tools ensures that B and C are checked out in the correct branches for A
to work properly.

Currently, yhis mechanism of dependencies is only supported by Reporeq when
all of the repositories are in a common directory.

## How to use it

In each depository, you must create a file named `project_dependency.yaml`
with the following structure:

```yaml
depositories_requirements:
    - name: my_repo
      branch: my_branch
    - name: my_repo_2
      tag: my_tag
```

Then, from any location, run the main script of Reporeq:

```bash
python sync_repositories.py /path/to/repositories main_repo
```

Where `main_repo` is the depository where you are currently working and
which needs the other repos to respect its requirements. The script won't
change the branch/tag of `main_repo` as it is the reference.


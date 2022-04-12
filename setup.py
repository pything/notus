#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import re
from pathlib import Path
from typing import IO, List, Sequence, Union

from setuptools import find_packages, setup


def python_version_check(major: int = 3, minor: int = 7) -> None:
    """

    :param major:
    :param minor:
    """
    import sys

    assert sys.version_info.major == major and sys.version_info.minor >= minor, (
        f"This project is utilises language features only present Python {major}.{minor} and greater. "
        f"You are running {sys.version_info}."
    )


python_version_check()


def read_reqs(file: str, path: Path) -> List[str]:
    """

    :param file:
    :param path:
    :return:
    """

    def readlines_ignore_comments(f: IO):
        """

        :param f:
        :return:
        """
        return [a_ for a_ in f.readlines() if "#" not in a_ and a_]

    def recursive_flatten_ignore_str(seq: Sequence) -> Sequence:
        """

        :param seq:
        :return:
        """
        if not seq:  # is empty Sequence
            return seq
        if isinstance(seq[0], str):
            return seq
        if isinstance(seq[0], Sequence):
            return (
                *recursive_flatten_ignore_str(seq[0]),
                *recursive_flatten_ignore_str(seq[1:]),
            )
        return (*seq[:1], *recursive_flatten_ignore_str(seq[1:]))

    def unroll_nested_reqs(req_str: str, base_path: Path) -> Sequence:
        """

        :param req_str:
        :param base_path:
        :return:
        """
        if req_str.startswith("-r"):
            with open(base_path / req_str.strip("-r").strip()) as f:
                return [unroll_nested_reqs(req.strip(), base_path) for req in readlines_ignore_comments(f)]
        else:
            return (req_str,)

    requirements_group = []
    with open(str(path / file)) as f:
        requirements = readlines_ignore_comments(f)
        for requirement in requirements:
            requirements_group.extend(
                recursive_flatten_ignore_str(unroll_nested_reqs(requirement.strip(), path))
            )

    req_set = set(requirements_group)
    req_set.discard("")
    return list(req_set)


with open(Path(__file__).parent / "notus" / "__init__.py", "r") as project_init_file:
    str_reg_exp = "['\"]([^'\"]*)['\"]"
    content = project_init_file.read()  # get strings from module
    version = re.search(rf"__version__ = {str_reg_exp}", content, re.M).group(1)
    project_name = re.search(rf"__project__ = {str_reg_exp}", content, re.M).group(1)
    author = re.search(rf"__author__ = {str_reg_exp}", content, re.M).group(1)
__author__ = author


class NotusPackage:
    @property
    def test_dependencies(self) -> list:
        """

        returns the list of test dependencies

        :return:
        :rtype:
        """
        return read_reqs("requirements_tests.txt", Path(__file__).parent / "requirements")

    @property
    def setup_dependencies(self) -> list:
        """
        returns the setup requirements

        :return:
        """
        return read_reqs("requirements_setup.txt", Path(__file__).parent / "requirements")

    @property
    def package_name(self) -> str:
        """
        returns the name of the package

        :return:
        """
        return project_name

    @property
    def url(self) -> str:
        """
        returns the url of the project

        :return:
        """
        return "https://github.com/pything/notus"

    @property
    def download_url(self) -> str:
        """
        returns the download url for the package

        :return:
        """
        return f"{self.url}/releases"

    @property
    def readme_type(self) -> str:
        """
        returns the type of readme to use

        :return:
        """
        return "text/markdown"

    @property
    def packages(self) -> List[Union[bytes, str]]:
        """
        returns a list of packages to include in the distribution

        :return:
        """
        return find_packages(
            exclude=[
                # 'Path/To/Exclude'
            ]
        )

    @property
    def author_name(self) -> str:
        """

        returns the author's name

        :return:
        """
        return author

    @property
    def author_email(self) -> str:
        """
        returns the author's email

        :return:
        """
        return "christian.heider@alexandra.dk"

    @property
    def maintainer_name(self) -> str:
        """
        returns the maintainer's name

        :return:
        """
        return self.author_name

    @property
    def maintainer_email(self) -> str:
        """
        returns the maintainer's email

        :return:
        """
        return self.author_email

    @property
    def package_data(self) -> dict:
        """
        returns the package data to include in the distribution

        :return:
        """
        data = glob.glob(str(Path.cwd() / "notus" / "data"), recursive=True)
        return {"notus": [*data]}

    @property
    def entry_points(self) -> dict:
        """
        returns the entry points to include in the distribution

        :return:
        """
        return {
            "console_scripts": [
                # "name_of_executable = module.with:function_to_execute"
                "toast-open=notus.entry_points.toast:main"
            ]
        }

    @property
    def extras(self) -> dict:
        """
        returns the extras to include in the distribution

        :return:
        """
        these_extras = {
            # 'ExtraName':['package-name; platform_system == "System(Linux,Windows)"'
        }

        path: Path = Path(__file__).parent / "requirements"

        for file in path.iterdir():
            if file.name.startswith("requirements_"):
                group_name_ = "_".join(file.name.strip(".txt").split("_")[1:])
                these_extras[group_name_] = read_reqs(file.name, path)

        all_dependencies = []
        for group_name in these_extras:
            all_dependencies += these_extras[group_name]
        these_extras["all"] = list(set(all_dependencies))

        return these_extras

    @property
    def requirements(self) -> list:
        """description

        :return:
        """
        return read_reqs("requirements.txt", Path(__file__).parent)

    @property
    def description(self) -> str:
        """description

        :return:
        """
        return "A package for providing a system notification interface"

    @property
    def readme(self) -> str:
        """description

        :return:
        """
        with open("README.md", encoding="utf8") as f:
            return f.read()

    @property
    def keyword(self) -> str:
        """description

        :return:
        """
        with open("KEYWORDS.md") as f:
            return f.read()

    @property
    def license(self) -> str:
        """description

        :return:
        """
        return "Apache License, Version 2.0"

    @property
    def classifiers(self) -> List[str]:
        """description

        :return:
        """
        return [
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Natural Language :: English",
            # 'Topic :: Scientific/Engineering :: Artificial Intelligence'
            # 'Topic :: Software Development :: Bug Tracking',
        ]

    @property
    def version(self) -> str:
        """description

        :return:
        """
        return version


if __name__ == "__main__":
    pkg = NotusPackage()

    setup(
        name=pkg.package_name,
        version=pkg.version,
        packages=pkg.packages,
        package_data=pkg.package_data,
        author=pkg.author_name,
        author_email=pkg.author_email,
        maintainer=pkg.maintainer_name,
        maintainer_email=pkg.maintainer_email,
        description=pkg.description,
        license=pkg.license,
        keywords=pkg.keyword,
        url=pkg.url,
        download_url=pkg.download_url,
        install_requires=pkg.requirements,
        extras_require=pkg.extras,
        setup_requires=pkg.setup_dependencies,
        entry_points=pkg.entry_points,
        classifiers=pkg.classifiers,
        long_description_content_type=pkg.readme_type,
        long_description=pkg.readme,
        tests_require=pkg.test_dependencies,
        include_package_data=True,
        python_requires=">=3.6",
    )

from setuptools import setup
from setuptools.command.build_py import build_py
import glob
import os
import platform
import subprocess
from pathlib import Path
from shutil import copyfile
import sys

include_java_stubs = os.environ.get('INCLUDE_JAVA_STUBS', 'false').lower() == 'true'
"""
If Java type stubs should be generated.
These are for our own type checker; users should never need
to use them (since they should be using the Python classes).

Not included in the default build since IDE's will see multiple
packages that define a class (the one from `ai.timefold...`
and the one from `timefold.solver...`), which can lead to the
wrong one being imported.
"""


class FetchDependencies(build_py):
    """
    A command class that fetch Java Dependencies and
    add them as files within a python package
    """
    def create_stubs(self, project_root, command):
        working_directory = project_root / 'timefold-solver-python-core'
        subprocess.run([str((project_root / command).absolute()), 'dependency:copy-dependencies'],
                       cwd=working_directory, check=True)
        subprocess.run([str((project_root / command).absolute()), 'dependency:copy-dependencies',
                        '-Dclassifier=javadoc'], cwd=working_directory, check=True)
        subprocess.run([sys.executable, str((project_root / 'create-stubs.py').absolute())],
                       cwd=working_directory, check=True)
        target_dir = self.build_lib
        for file_name in find_stub_files(str(working_directory / 'java-stubs')):
            path = file_name[len(str(working_directory)) + 1:]
            os.makedirs(os.path.dirname(os.path.join(target_dir, path)), exist_ok=True)
            copyfile(os.path.join(str(working_directory), path), os.path.join(target_dir, path))
        for file_name in find_stub_files(str(working_directory / 'jpype-stubs')):
            path = file_name[len(str(working_directory)) + 1:]
            os.makedirs(os.path.dirname(os.path.join(target_dir, path)), exist_ok=True)
            copyfile(os.path.join(str(working_directory), path), os.path.join(target_dir, path))
        for file_name in find_stub_files(str(working_directory / 'ai-stubs')):
            path = file_name[len(str(working_directory)) + 1:]
            os.makedirs(os.path.dirname(os.path.join(target_dir, path)), exist_ok=True)
            copyfile(os.path.join(str(working_directory), path), os.path.join(target_dir, path))

    def run(self):
        if not self.dry_run:
            project_root = Path(__file__).parent
            # Do a mvn clean install
            # which is configured to add dependency jars to 'target/dependency'
            command = 'mvnw'
            if platform.system() == 'Windows':
                command = 'mvnw.cmd'

            subprocess.run([str((project_root / command).absolute()), 'clean', 'install'],
                           cwd=project_root, check=True)

            if include_java_stubs:
                self.create_stubs(project_root, command)

            classpath_jars = []
            # Add the main artifact
            classpath_jars.extend(glob.glob(os.path.join(project_root, 'timefold-solver-python-core', 'target', '*.jar')))
            # Add the main artifact's dependencies
            classpath_jars.extend(glob.glob(os.path.join(project_root, 'timefold-solver-python-core', 'target', 'dependency', '*.jar')))

            self.mkpath(os.path.join(self.build_lib, 'timefold', 'solver', 'jars'))

            # Copy classpath jars to timefold.solver.jars
            for file in classpath_jars:
                copyfile(file, os.path.join(self.build_lib, 'timefold', 'solver', 'jars', os.path.basename(file)))

            # Make timefold.solver.jars a Python module
            fp = open(os.path.join(self.build_lib, 'timefold', 'solver', 'jars', '__init__.py'), 'w')
            fp.close()
        build_py.run(self)


def find_stub_files(stub_root: str):
    for root, dirs, files in os.walk(stub_root):
        for file in files:
            if file.endswith(".pyi"):
                yield os.path.join(root, file)


packages = [
            'timefold.solver',
            'timefold.solver.config',
            'timefold.solver.domain',
            'timefold.solver.heuristic',
            'timefold.solver.score',
            'timefold.solver.test',
            '_jpyinterpreter',
            ]

package_dir = {
    'timefold.solver': 'timefold-solver-python-core/src/main/python',
    '_jpyinterpreter': 'jpyinterpreter/src/main/python',
}

if include_java_stubs:
    packages += [
                 'java-stubs',
                 'jpype-stubs',
                 'ai-stubs',
                ]
    package_dir.update({
        'java-stubs': 'timefold-solver-python-core/src/main/resources',
        'jpype-stubs': 'timefold-solver-python-core/src/main/resources',
        'ai-stubs': 'timefold-solver-python-core/src/main/resources',
    })

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
timefold_solver_python_version = '1.10.0a0'

setup(
    name='timefold-solver',
    version=timefold_solver_python_version,
    license='Apache License Version 2.0',
    license_file='LICENSE.txt',
    description='An AI constraint solver that optimizes planning and scheduling problems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TimefoldAI/timefold-solver-python',
    project_urls={
        'Timefold Solver Documentation': 'https://timefold.ai/docs/timefold-solver/latest',
        'Timefold Homepage': 'https://timefold.ai',
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Java Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    packages=packages,
    package_dir=package_dir,
    test_suite='tests',
    python_requires='>=3.10',
    install_requires=[
        'JPype1>=1.5.0',
    ],
    cmdclass={'build_py': FetchDependencies},
    package_data={
        'timefold.solver.jars': ['*.jar'],
    },
)

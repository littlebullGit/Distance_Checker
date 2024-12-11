from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
def read_requirements(filename: str):
    # Packages that should not be included in install_requires
    build_packages = {'pyinstaller'}
    
    with open(filename, 'r') as file:
        requirements = []
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name without version
                package = line.split('==')[0]
                # Only include if not in build_packages
                if package not in build_packages:
                    requirements.append(line)
        return requirements

# Read long description from README.md
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Distance Checker Application"

# Project root directory
project_root = Path(__file__).parent

# Get requirements
requirements = read_requirements(project_root / 'requirements.txt')

setup(
    name="distance_checker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'distance_checker=main:main',
        ],
    },
    author="Derek Peng",
    author_email="your.email@example.com",
    description="A tool for checking driving distances between locations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    keywords="maps distance location driving-time",
    url="https://github.com/yourusername/distance_checker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.8',
    # Include additional files
    package_data={
        '': ['*.txt', '*.md'],
    },
)
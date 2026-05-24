from setuptools import setup, find_packages

setup(
    name="video_edit_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "moviepy>=2.0.0",
        "pyyaml>=6.0",
        "click>=8.0",
        "anthropic>=0.30.0",
        "pydantic>=2.0",
        "opencv-python>=4.8.0",
    ],
    entry_points={
        "console_scripts": [
            "vedit=cli:cli",
        ],
    },
)

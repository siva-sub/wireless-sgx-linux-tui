from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wirelesssgx",
    version="1.0.0",
    author="Sivasubramanian Ramanathan",
    author_email="hello@sivasub.com",
    description="A modern TUI for Wireless@SGx setup on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/siva-sub/wireless-sgx-linux-tui",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.41.0",
        "pycryptodome>=3.19.0",
        "keyring>=24.0.0",
        "python-dateutil>=2.8.2",
        "requests>=2.31.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "wirelesssgx=wirelesssgx.app:main",
        ],
    },
)
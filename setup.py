from setuptools import setup, find_packages

setup(
    name             = "julian-bot-core",
    version          = "1.0.0",
    description      = "Shared library for all TheBooleanJulian Telegram bots",
    author           = "TheBooleanJulian",
    url              = "https://github.com/TheBooleanJulian/julian-bot-core",
    packages         = find_packages(),
    package_data     = {"julian_bot_core": ["status_template.html"]},
    python_requires  = ">=3.11",
    install_requires = [
        "python-telegram-bot>=21.0",
        "flask>=3.0",
        "pytz",
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

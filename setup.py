from setuptools import setup, find_packages

setup(
    name             = "thebooleanjulian-bot-core",
    version          = "2.1.0",
    description      = "Shared, opt-in building blocks for TheBooleanJulian Telegram bots",
    author           = "TheBooleanJulian",
    url              = "https://github.com/TheBooleanJulian/thebooleanjulian-bot-core",
    packages         = find_packages(),
    python_requires  = ">=3.11",
    install_requires = [
        "python-telegram-bot>=21.0",
    ],
    extras_require = {
        # Only needed if you use health.FlaskStatusServer instead of the
        # default stdlib-based SimpleStatusServer.
        "flask": ["flask>=3.0"],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

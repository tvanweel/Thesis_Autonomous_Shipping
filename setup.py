from setuptools import setup, find_packages

setup(
    name="autonomous-shipping-safety",
    version="0.1.0",
    author="Tijn van Weel",
    author_email="v.b.vanweel@student.tudelft.nl",
    description="Agent-based model for autonomous inland shipping safety assessment",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tvanweel/Thesis_Autonomous_Shipping",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mesa>=3.0.0",
        "networkx>=3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.20.0",
        ],
    },
)

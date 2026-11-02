from setuptools import find_packages, setup

package_name = "op3_equal_live_report"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools", "matplotlib", "numpy", "PyYAML"],
    zip_safe=True,
    maintainer="BhreW",
    maintainer_email="BhreW@users.noreply.github.com",
    description="Document equal OP3 live runs without changing detector or motor packages.",
    license="MIT",
    entry_points={"console_scripts": [
        "op3-equal-live-report=op3_equal_live_report.report:main",
        "op3-equal-live-capture=op3_equal_live_report.capture:main",
    ]},
)

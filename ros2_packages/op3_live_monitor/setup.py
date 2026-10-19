from setuptools import find_packages, setup

package_name = "op3_live_monitor"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="BhreW",
    maintainer_email="BhreW@users.noreply.github.com",
    description="Live OP3 camera detection and tracking X11 window",
    license="MIT",
    entry_points={"console_scripts": ["op3-live-monitor = op3_live_monitor.monitor:main"]},
)

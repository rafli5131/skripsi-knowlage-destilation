from setuptools import find_packages, setup

package_name = "op3_servo_torque_disable"

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
    description="Safely disable OP3 servo torque before controller initialization.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "op3-disable-all-servos=op3_servo_torque_disable.cli:main",
        ],
    },
)

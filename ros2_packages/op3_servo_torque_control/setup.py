from setuptools import find_packages, setup

package_name = "op3_servo_torque_control"

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
    description="Safely enable OP3 body servo torque while excluding head IDs 19/20.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "op3-enable-body-servos=op3_servo_torque_control.cli:main",
        ],
    },
)

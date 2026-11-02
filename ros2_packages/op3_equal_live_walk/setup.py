from setuptools import find_packages, setup

package_name = "op3_equal_live_walk"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]), ("share/" + package_name, ["package.xml"])],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="BhreW",
    maintainer_email="BhreW@users.noreply.github.com",
    description="Guarded walking gait for matched OP3 live evaluation.",
    license="MIT",
    entry_points={"console_scripts": ["op3-equal-live-walk=op3_equal_live_walk.guard:main"]},
)
